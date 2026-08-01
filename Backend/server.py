from flask import Flask, request, jsonify 
import os
import whisperx
import gc 
from whisperx.diarize import DiarizationPipeline
import json 
import firebase_admin 
from firebase_admin import credentials, firestore
from datetime import datetime 


device = "cpu"
audio_path = "audio.mp3"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


app = Flask(__name__)

model = None

@app.route("/transcribe", methods=["POST"])
def detect_stutter():
    audio_path = "audio.mp3"
    
    audio = whisperx.load_audio(audio_path)
    model = whisperx.load_model("large-v3", device)
    result = model.transcribe(audio, batch_size=16)
    
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device)
    
    doc = db.collection("transcripts").document()
    doc.set({
        "created_at": datetime.utcnow(),
        "audio_path": audio_path
    })
    for i, seg in enumerate(result["segments"]):
        doc.collection("segments").document(str(i)).set(seg)
    return jsonify(result["segments"])
        
    
    
if __name__ == "__main__":
    app.run(port=5001)
