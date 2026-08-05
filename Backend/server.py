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

device = "cpu"
audio_path = "audio.mp3"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


app = Flask(__name__)
CORS(app)

model = None

@app.route("/transcribe", methods=["POST"])
def detect_stutter():
    audio_path = "audio.mp3"
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

    return jsonify({"segments": result["segments"], "text_scores": wordScores, "text": textTranscription})


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
    
    
if __name__ == "__main__":
    app.run(port=5001)

