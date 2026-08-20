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


device = "cpu"

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
def detect_stutter(audio_path = None):
    
    wordScores = []
    textParts = []
    # Understand Database Assurance Code
    existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]

    if audio_path == None: # Changed To Allow For Ease Of Running
        if not existing:
            return jsonify({"Error: No Previous Versions Found"}), 400

        

        latest_file = max(existing, key=get_version_number)
        audio_path = os.path.join(audio_folder, latest_file)
    
    
    audio = whisperx.load_audio(audio_path)
    model = whisperx.load_model("large-v3", device)
    result = model.transcribe(audio, batch_size=16)

    base_filename = os.path.basename(audio_path)
    version_num = get_version_number(base_filename)
    
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device)

    for segment in result['segments']:
        textParts.append(segment['text'].strip())
        for w in segment['words']:
            wordScores.append(w['score'])

    textTranscription = " ".join(textParts)

    doc = db.collection("transcripts").document(f"Recording_v{version_num}")
    doc.set({
        "created_at": datetime.utcnow(),
        "audio_path": audio_path
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

    randomSentenceNum = random.randrange(1,16)

 
    doc_ref = db.collection("Sentences").document("SkROjYeo8NiV76JyRnfR")
    doc = doc_ref.get()  # fetches the document from Firestore

    if not doc.exists:
        return jsonify({"error": "document not found"}), 404

    data = doc.to_dict()  # turns the document into a normal Python dict
    sentence = data.get(f"Sentence{randomSentenceNum}")

    return jsonify({"sentence": sentence})


@app.route("/makeRecording", methods = ["POST"])
def makeRecording():
    if "recording" not in request.files: 
        return jsonify({"error": "No Recording Found"}), 400

    recording_file = request.files["recording"]

    if recording_file.filename == "":
     return jsonify({"error": "No filename found"}), 400

    if not allowed_file(recording_file.filename):
      return jsonify({"error": "Not correct file type"}), 400

    ext = recording_file.filename.rsplit(".", 1)[1].lower()
    


    existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]
    version = len(existing) + 1
    filename = f"most_recent_rec_v{version}.mp4"
    filepath = os.path.join(audio_folder, filename)

    recording_file.save(filepath)

    transcribe_file = detect_stutter(filepath)

    return jsonify({
    "message": "Voice memo saved",
    "filename": filename,
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
    threshold = request.form.get("threshold", type = int)

 
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
        # "lyricsFound": len(lyrics), - Lyrics Not In Function Otherwise
    }), 201
    
# Need To Call This Endpoint When Done, Do Most By Self
@app.route("/stutterSeverity", methods = ["POST", "GET"])
def stutterSeverity():

    stutterLevel = "None"
    existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]
    
    if not existing:
        return jsonify({"Error: No Previous Versions Found"}), 400

    last_file = max(existing, key=get_version_number)
    version_num = get_version_number(last_file)
    
    doc_ref = db.collection("transcripts").document(f"Recording_v{version_num}")

    text_doc = doc_ref.collection("text").document("full").get()
    scores_doc = doc_ref.collection("scores").document("full").get()


    if not text_doc.exists or not scores_doc.exists:
     return jsonify({"Error": "Transcript or scores not found"}), 404

    text_data = text_doc.to_dict()
    scores_data = scores_doc.to_dict()

    text = text_data["text"]
    scores = scores_data["scores"]

    if not scores:
        return jsonify({"Error: No Scores Found"}), 404

    separate_text = text.split() # New Variable: Divide Text Into Array Of Words
    avg_Word_Score = 0 # Avg Score Of Each Item In Scores

    number_Stutters = 0 

    for s in scores:
        avg_Word_Score = avg_Word_Score + float(s)

    avg_Word_Score = avg_Word_Score / len(scores)


    separate_text = [word.lower().strip() for word in separate_text]
    w = 0 

    while w < len(separate_text):
        if (w + 1 < len(separate_text)) and separate_text[w] == separate_text[w + 1]:
            number_Stutters += 1

        w += 1

    
    if avg_Word_Score <= .400 and number_Stutters == 1:
        stutterLevel = "Minor"

    elif avg_Word_Score <= .300 and (number_Stutters == 2 or number_Stutters == 3):
        stutterLevel = "Average"

    elif avg_Word_Score <= .200 and number_Stutters > 4:
        stutterLevel = "Major"

    else:
        stutterLevel = "No Stutter"

    recordingName = f"Recording_v{version_num}"


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
    recording_name = request.args.get("recordingName")
    severity = level(recording_name)
    
    song_ref = db.collection("songs").where("threshold", "==", severity).stream()
    songs = []
    for doc in song_ref: 
        data = doc.to_dict()
        data["id"] = data.id
        songs.append(data)
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return jsonify(data), 200

# 60 - 87 bpm = Major Stutter 
# 87 - 113 bpm = Average Stutter 
# 113 - 140 bpm = Minor Stutter 
# 140+ = No Stutter 




   

if __name__ == "__main__":
    app.run(port=5001)

