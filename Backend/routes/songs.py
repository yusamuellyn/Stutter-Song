from flask import Blueprint, request, jsonify
from firebase_admin import firestore

from core.state import db, get_user_folder, get_latest_version

songs_bp = Blueprint("songs", __name__, url_prefix="/songs")

@songs_bp.route("/upload-song", methods=["POST"])
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

def level(recording_name):
    doc = db.collection("stutters").document(recording_name).get()
    data = doc.to_dict()
    return data.get("stutterLevel")

@songs_bp.route("/display-song", methods = ["GET"])
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
