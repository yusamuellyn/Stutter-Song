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

# Next Task: Ensure Text, Scores Get Added To Database
# Then: (IMPT) Move Off Of Singular Recordings, Somehow Make Sure Transcribe Get's Most Recent Recordings

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



@app.route("/transcribe", methods=["POST"])
def detect_stutter():
    audio_path = os.path.join(audio_folder, "most_recent_rec.mp4")
    wordScores = []
    textParts = []
    
    audio = whisperx.load_audio(audio_path)
    model = whisperx.load_model("large-v3", device)
    result = model.transcribe(audio, batch_size=16)
    
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device)

    for segment in result['segments']:
        textParts.append(segment['text'].strip())
        for w in segment['words']:
            wordScores.append(w['score'])

    textTranscription = " ".join(textParts)

    doc = db.collection("transcripts").document()
    doc.set({
        "created_at": datetime.utcnow(),
        "audio_path": audio_path
    })
    for i, seg in enumerate(result["segments"]):
        doc.collection("segments").document(str(i)).set(seg)

    doc.collection("text").document("full").set({"text": textTranscription})
    doc.collection("scores").document("full").set({"scores":wordScores})

    return jsonify(
    {"text_scores": wordScores,
      "text": textTranscription,
      "segments": result["segments"]})


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
    filename = f"most_recent_rec.{ext}"
    filepath = os.path.join(audio_folder, filename)

    recording_file.save(filepath)
    # detect_stutter() # Auto-Transcribes Recording

    return jsonify({
    "message": "Voice memo saved",
    "filename": filename,
    "size_kb": round(os.path.getsize(filepath) / 1024, 1)
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
    

@app.route("/stutterSeverity", methods = ["POST", "GET"])
def stutterSeverity():
    doc_ref = db.collection() # Finish When Main Goals Done

    # New Variable: Divide Text Into Array Of Words
    avg_Word_Score = 0 # Avg Score Of Each Item In Scores

    repititon_Present = False 
    number_Stutters = 0 


    # In Separated Version, If A Word Repeats Then Make rP True And Track Amount
    # If Scores Below .400 and 1 Repition Repeated - Minor Stutter
    # If Scores Below .300 and 2-3 Repitions Detected - Stutter
    # If Scores Below .200 and 4+ Repitions Detected - Major Stutter

if __name__ == "__main__":
    app.run(port=5001)

