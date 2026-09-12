from flask import Blueprint, request, jsonify
import os
import uuid

from core.state import (
    db,
    allowed_file,
    get_user_folder,
    get_next_version,
)
from routes.transcription import detect_stutter

recordings_bp = Blueprint("recordings", __name__, url_prefix="/recordings")

@recordings_bp.route("/makeRecording", methods = ["POST"])
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
