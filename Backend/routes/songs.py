import math
import random

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

BPM_TIERS = ["slowest", "slower", "faster"]

# Song tags that suit each model stutter type (substring match, so "repetitive" also hits "repetitive-chorus")
TYPE_TAG_KEYWORDS = {
    "Repetition": ["repetitive", "repeated", "repetition", "predictable"],
    "Prolong/Block": ["sustained", "slow", "low-lyrical-density", "simple-phrasing", "smooth"],
    "Interjection": ["steady", "strong-beat", "pulse", "rhythmic", "syllable-to-beat", "driving", "groove", "backbeat"],
}

TYPE_REASONS = {
    "Repetition": "You repeated sounds the most, so we picked a song with a predictable, repeating chorus.",
    "Prolong/Block": "You stretched or got stuck on sounds the most, so we picked a song with long, smooth notes.",
    "Interjection": "You used filler sounds the most, so we picked a song with a steady beat to keep pace with.",
}
MIXED_REASON = "You had a mix of stutter types, so we picked a song that fits several of them."

RECENT_SONG_LIMIT = 3

NO_SONG_MESSAGES = {
    "No Stutter": "No stutters were detected, so there's no song to practice with right now.",
    "Warning": "We noticed one possible stutter. No song is needed yet, but keep practicing.",
}

def songs_in_tier(songs, tier):
    # Sort by BPM and split into 3 equal groups: slowest, slower, faster
    ordered = sorted(songs, key=lambda s: s["bpm"])
    size = math.ceil(len(ordered) / len(BPM_TIERS))
    i = BPM_TIERS.index(tier)
    return ordered[i * size:(i + 1) * size]

def matches_type(song, type_name):
    return any(k in tag for k in TYPE_TAG_KEYWORDS.get(type_name, []) for tag in song.get("tags", []))

def dominant_type(type_counts):
    # The type with at least half of all instances and no tie for first; None means a mix
    ranked = sorted(((n, c) for n, c in type_counts.items() if c > 0), key=lambda kv: -kv[1])
    if not ranked:
        return None
    top, count = ranked[0]
    total = sum(c for _, c in ranked)
    if count * 2 >= total and (len(ranked) == 1 or ranked[1][1] < count):
        return top
    return None

def pick_candidates(tier_songs, type_counts):
    main = dominant_type(type_counts)
    if main:
        return [s for s in tier_songs if matches_type(s, main)], TYPE_REASONS[main]

    found = [n for n, c in type_counts.items() if c > 0]
    fits = {s["id"]: sum(matches_type(s, n) for n in found) for s in tier_songs}
    best = max(fits.values(), default=0)
    return [s for s in tier_songs if best and fits[s["id"]] == best], MIXED_REASON

@songs_bp.route("/display-song", methods = ["GET"])
def displaySong():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "userId required"}), 400

    user_folder = get_user_folder(user_id)
    version_num = get_latest_version(user_folder)
    if version_num is None:
        return jsonify({"error": "No previous versions found"}), 400

    stutter_doc = db.collection("stutters").document(f"{user_id}_v{version_num}").get()
    if not stutter_doc.exists:
        return jsonify({"error": "Run /stutter/stutterSeverity first"}), 404

    stutter = stutter_doc.to_dict()
    severity = stutter.get("stutterLevel")
    tier = stutter.get("songTier")

    if tier is None:
        return jsonify({
            "stutterLevel": severity,
            "songTier": None,
            "message": NO_SONG_MESSAGES.get(severity, ""),
        }), 200

    songs = []
    for doc in db.collection("songs").stream():
        data = doc.to_dict()
        if data.get("bpm") is None:
            continue
        data["id"] = doc.id
        data.pop("createdAt", None)
        songs.append(data)

    if not songs:
        return jsonify({"error": "No matching song found"}), 404

    tier_songs = songs_in_tier(songs, tier)
    candidates, reason = pick_candidates(tier_songs, stutter.get("typeCounts", {}))

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    recent = (user_doc.to_dict() or {}).get("recentSongIds", []) if user_doc.exists else []

    # Prefer a matching song the user hasn't just heard, then any fresh song in the tier
    pool = (
        [s for s in candidates if s["id"] not in recent]
        or [s for s in tier_songs if s["id"] not in recent]
        or candidates
        or tier_songs
    )
    choice = random.choice(pool)
    alternatives = random.sample([s for s in pool if s is not choice], k=min(2, len(pool) - 1))

    recent = [choice["id"]] + [i for i in recent if i != choice["id"]]
    user_ref.set({"recentSongIds": recent[:RECENT_SONG_LIMIT]}, merge=True)

    return jsonify({
        **choice,
        "stutterLevel": severity,
        "songTier": tier,
        "reason": reason,
        "alternatives": alternatives,
    }), 200
