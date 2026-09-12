from flask import Blueprint, jsonify
import os
import whisperx
from datetime import datetime

from core.state import (
    db,
    device,
    ts_model,
    get_user_folder,
    get_latest_version,
    get_version_number,
)

transcription_bp = Blueprint("transcription", __name__, url_prefix="/transcription")

@transcription_bp.route("/transcribe", methods=["POST"])
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
