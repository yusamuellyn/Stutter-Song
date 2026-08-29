from flask import Flask, request, jsonify 
import os
import whisperx
import gc 
from whisperx.diarize import DiarizationPipeline
import json 
import firebase_admin 
from firebase_admin import credentials, firestore, storage 
from datetime import datetime 
from werkzeug.utils import secure_filename
import mido
import base64 
import io
import random
from flask_cors import CORS
from datetime import datetime
from collections import Counter
import uuid 


def get_next_version(user_folder):
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return 1
    return max(get_version_number(f) for f in existing) + 1

def get_latest_version(user_folder):
    if not os.path.isdir(user_folder):
        return None
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return None
    return max(get_version_number(f) for f in existing)

def get_user_folder(user_id):
    folder = os.path.join(audio_folder, user_id)
    os.makedirs(folder, exist_ok=True)
    return folder

def get_last_n_versions(user_folder, n=3):
    if not os.path.isdir(user_folder):
        return []
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return []
    versions = sorted({get_version_number(f) for f in existing}, reverse=True)
    return versions[:n]


device = "cpu"
ts_model = whisperx.load_model("large-v3", device)

audio_folder = "recordings"
os.makedirs(audio_folder, exist_ok= True)

audio_path = os.path.join(audio_folder, "most_recent_rec.mp4")

recording_extensions = {"mp4", "wav", "webm"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in recording_extensions

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


app = Flask(__name__)
CORS(app)

model = None

def get_version_number(filename):
    return int(filename.split("_v")[1].split(".")[0])



@app.route("/transcribe", methods=["POST"])
def detect_stutter(audio_path = None, user_id = None, version_num = None, sentence_text = None):
    wordScores = []
    textParts = []

    # Understand
    if audio_path is None:
        if user_id is None:
            return jsonify({"error": "userId required"}), 400
        user_folder = get_user_folder(user_id)
        version_num = get_latest_version(user_folder)
        if version_num is None:
            return jsonify({"Error: No Previous Versions Found"}), 400
        audio_path = os.path.join(user_folder, f"rec_v{version_num}.mp4")
    else:
        version_num = get_version_number(os.path.basename(audio_path))


    audio = whisperx.load_audio(audio_path)
    # model = whisperx.load_model("large-v3", device)
    result = ts_model.transcribe(audio, batch_size=16)

    # base_filename = os.path.basename(audio_path)
    # version_num = get_version_number(base_filename)

    
    
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device)

    for segment in result['segments']:
        textParts.append(segment['text'].strip())
        for w in segment['words']:
            wordScores.append(w['score'])

    textTranscription = " ".join(textParts)

    doc = db.collection("transcripts").document(f"{user_id}_v{version_num}")
    doc.set({
        "created_at": datetime.utcnow(),
        "audio_path": audio_path,
        "userId": user_id,
        "sentence": sentence_text
    })
    for i, seg in enumerate(result["segments"]):
        doc.collection("segments").document(str(i)).set(seg)

    doc.collection("text").document("full").set({"text": textTranscription})
    doc.collection("scores").document("full").set({"scores":wordScores})

    return {
      "text_scores": wordScores,
      "text": textTranscription,
      "segments": result["segments"],
      "version": version_num
      }
    


@app.route("/get-sentence", methods = ["GET"])
def getSentence():

    randomSentenceNums = random.sample(range(1,30),3)

 
    doc_ref = db.collection("Sentences").document("SkROjYeo8NiV76JyRnfR")
    doc = doc_ref.get()  # fetches the document from Firestore

    if not doc.exists:
        return jsonify({"error": "document not found"}), 404

    data = doc.to_dict()  # turns the document into a normal Python dict
    sentences = [data.get(f"Sentence{n}") for n in randomSentenceNums]

    sentence_rem_id = str(uuid.uuid4())
    db.collection("sentenceRems").document(sentence_rem_id).set({"sentence": sentences})

    return jsonify({"sentence": sentences, "SRI": sentence_rem_id})


@app.route("/makeRecording", methods = ["POST"])
def makeRecording():
    if "recording" not in request.files: 
        return jsonify({"error": "No Recording Found"}), 400

    recording_file = request.files["recording"]

    if recording_file.filename == "":
     return jsonify({"error": "No filename found"}), 400

    if not allowed_file(recording_file.filename):
      return jsonify({"error": "Not correct file type"}), 400
  
    sentence_index = request.form.get("sentenceIndex")
    # Generate userID
    user_id = request.form.get("userID") or str(uuid.uuid4())

    SRI = request.form.get("SRI")

    sentence = None
    if SRI:
      sentence_doc = db.collection("sentenceRems").document(SRI).get()
      if sentence_doc.exists:
        sentence = sentence_doc.to_dict().get("sentence")
    
    user_folder = get_user_folder(user_id)
    version = get_next_version(user_folder)
    filename = f"rec_v{version}.mp4"
    

    # existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]
    # version = len(existing) + 1
    # filename = f"most_recent_rec_v{version}.mp4"

    filepath = os.path.join(user_folder, filename)

    recording_file.save(filepath)

    transcribe_file = detect_stutter(filepath, user_id, version, sentence_text= sentence)

    return jsonify({
    "message": "Voice memo saved",
    "userId": user_id,
    "filename": filename,
    "sentenceIndex": sentence_index,
    "size_kb": round(os.path.getsize(filepath) / 1024, 1),
    **transcribe_file # ** Splits File Correctly
    }), 201



@app.route("/upload-song", methods=["POST"])
def uploadSong():
    file = request.files["file"]
    
    song_id = request.form.get("id")
    title = request.form.get("title")
    artist = request.form.get("artist")
    youtube_id = request.form.get("youtube-id")
    threshold = request.form.get("threshold")

 
    doc_data = {
        "title": title,
        "artist": artist,
        "threshold": threshold,
        "youtube-id": youtube_id,
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    db = firestore.client()
    db.collection("songs").document(song_id).set(doc_data)
    return jsonify({
        "success": True,
        "id": song_id,
        
    }), 201
    
# Organize Endpoint
@app.route("/stutterSeverity", methods = ["POST", "GET"])
def stutterSeverity():
    user_id = request.args.get("userId") or request.form.get("userId")
    if not user_id:
        return jsonify({"error": "userId required"}), 400
    
    user_folder = get_user_folder(user_id)
    versions= get_last_n_versions(user_folder, 3)
    if not versions:
        return jsonify({"error": "No previous versions found"}), 400
    
    stutterLevel = "None"
    
    scores = []
    number_Stutters = 0
    # existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]
    
    # if not existing:
    #     return jsonify({"Error: No Previous Versions Found"}), 400

    # last_file = max(existing, key=get_version_number)
    # version_num = get_version_number(last_file)

    for version_num in versions:
        doc_ref = db.collection("transcripts").document(f"{user_id}_v{version_num}")

        parent_doc = doc_ref.get()
        sentence = None
        if parent_doc.exists:
            sentence = parent_doc.to_dict().get("sentence")

        text_doc = doc_ref.collection("text").document("full").get()
        scores_doc = doc_ref.collection("scores").document("full").get()

    


        if not text_doc.exists or not scores_doc.exists:
            continue

        text_data = text_doc.to_dict()
        scores_data = scores_doc.to_dict()

        text = text_data["text"]
        version_scores = scores_data["scores"]

        if not version_scores:
         continue
            
        scores.extend(version_scores)

        separate_text = text.split()
        separate_text = [word.lower().strip() for word in separate_text]
        w = 0
        while w < len(separate_text):
            if (w + 1 < len(separate_text)) and separate_text[w] == separate_text[w + 1]:
                    number_Stutters += 1
            w += 1
        

    if not scores:
        return jsonify({"Error: No Scores Found"}), 404

    avg_Word_Score = 0 

    for s in scores:
        avg_Word_Score = avg_Word_Score + float(s)

    avg_Word_Score = avg_Word_Score / len(scores)


    separate_text = [word.lower().strip() for word in separate_text]
    w = 0 


    while w < len(separate_text):
        if (w + 1 < len(separate_text)) and separate_text[w] == separate_text[w + 1]:
            number_Stutters += 1

        w += 1

    partial_stutters = 0
    words_stuttered = []
    sentence_words = sentence.split()

    # Do Front/Backend Thing and Partial Report Thursday
    # Debug Sentence ASAP

    for wrd in sentence_words:
        iter_builder = [] 
        lenWrd = len(wrd) - 1 
        for a in range(lenWrd):
            iter_builder.append(wrd[:a + 1]) 

        for pt in iter_builder:
            if pt in separate_text:
                partial_stutters += 1
                

       

    
    if avg_Word_Score <= .400 and number_Stutters == 1:
        stutterLevel = "Minor"

    elif avg_Word_Score <= .300 and (number_Stutters == 2 or number_Stutters == 3):
        stutterLevel = "Average"

    elif avg_Word_Score <= .200 and number_Stutters > 4:
        stutterLevel = "Major"

    else:
        stutterLevel = "No Stutter"

    recordingName = f"{user_id}_v{versions[0]}"


    # Liam - Understand Below  
    doc_data = { 
        "recordingName": recordingName,
        "stutterLevel": stutterLevel

        }

    db.collection("stutters").document(recordingName).set(doc_data)
    return jsonify({
            "success": True,
            "id": recordingName,
            
        }), 201
    
def level(recording_name):
    doc = db.collection("stutters").document(recording_name).get()
    data = doc.to_dict()
    return data.get("stutterLevel")

@app.route("/display-song", methods = ["GET"])
def displaySong():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "userId required"}), 400

    user_folder = get_user_folder(user_id)
    version_num = get_latest_version(user_folder)
    if version_num is None:
        return jsonify({"error": "No previous versions found"}), 400

    severity = level(f"{user_id}_v{version_num}")

    song_ref = db.collection("songs").where("threshold", "==", severity).stream()
    songs = []
    for doc in song_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        songs.append(data)

    if not songs:
        return jsonify({"error": "No matching song found"}), 404

    return jsonify(songs[0]), 200


# Sam Adds Song Rec Display
@app.route("/displaySev", methods = ["GET"])
def displayInfo():
    user_id = request.args.get("userId")
    if not user_id: 
        return jsonify({"error": "userId required"}), 400
    
    user_folder = get_user_folder(user_id)
    last_version = get_latest_version(user_folder)
    if last_version is None:
     return jsonify({"error": "No Previous Versions Found"}), 400
 
    rec_id = f"{user_id}_v{last_version}"
    doc = db.collection("stutters").document(rec_id).get()
    
    if not doc.exists:
        return jsonify({"error": "document not found"}), 404

    data = doc.to_dict()  # turns the document into a normal Python dict
    sL = data.get("stutterLevel")
    
    return jsonify({"StutterLevel": sL})
   

if __name__ == "__main__":
    app.run(port=5001)



# REPORTS WILL BE HOW MANY WORDS REPEATED, EXAMPLES OF IT
# OR: Stutter Level / What Caused It (Full Word, Partial Word or Score) / Examples Found / Song and BPM Reccomendation / Maybe More
# Main Logic Before Sam Makes 3 Recordings Critical, Reports After

# More Specific Song Recs and Numbers Later