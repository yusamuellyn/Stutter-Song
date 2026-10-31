from flask import Blueprint, jsonify
import os
from datetime import datetime

from core.state import (
    db,
    model,
    get_user_folder,
    get_latest_version,
    get_version_number,
)

transcription_bp = Blueprint("transcription", __name__, url_prefix="/transcription")

@transcription_bp.route("/transcribe", methods=["POST"])
def detect_stutter(audio_path = None, user_id = None, version_num = None, sentence_text = None, sentence_index = None):
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

    stutter_result = model.analyze(audio_path, hop_seconds=3.0)

    doc = db.collection("transcripts").document(f"{user_id}_v{version_num}")
    doc.set({
        "created_at": datetime.utcnow(),
        "audio_path": audio_path,
        "userId": user_id,
        "sentence": sentence_text,
        "sentenceIndex": int(sentence_index) if sentence_index is not None else None,
    })
    doc.collection("model").document("full").set(stutter_result)

    return {
      "stutter_analysis": stutter_result,
      "version": version_num
      }
