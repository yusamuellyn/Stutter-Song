from flask import Blueprint, request, jsonify

from core.state import db, get_user_folder, get_last_n_versions, get_latest_version

stutter_bp = Blueprint("stutter", __name__, url_prefix="/stutter")

LEVELS = ["No Stutter", "Warning", "Minor", "Average", "Major"]
SONG_TIERS = {"Minor": "faster", "Average": "slower", "Major": "slowest"}

# Warning:      1 type / 1 instance              (no song)
# Faster song:  1 or 2 types AND 2-3 instances   -> Minor
# Slower song:  2 or 3 types AND 4-5 instances   -> Average
# Slowest song: all types AND 6+ instances       -> Major
# Instances set the level; the number of types caps or raises it into the allowed range.
def level_from_counts(instances, num_types):
    if instances == 0:
        return "No Stutter"
    if instances == 1:
        level = 1
    elif instances <= 3:
        level = 2
    elif instances <= 5:
        level = 3
    else:
        level = 4
    low, high = {1: (1, 2), 2: (2, 3)}.get(num_types, (3, 4))
    return LEVELS[min(max(level, low), high)]

def sentence_for(transcript_doc):
    # "sentence" holds every sentence in the session; "sentenceIndex" picks the one read
    if not transcript_doc.exists:
        return None
    data = transcript_doc.to_dict()
    sentence, idx = data.get("sentence"), data.get("sentenceIndex")
    if isinstance(sentence, list):
        return sentence[idx] if idx is not None and 0 <= idx < len(sentence) else None
    return sentence

# Organize Endpoint
@stutter_bp.route("/stutterSeverity", methods = ["POST", "GET"])
def stutterSeverity():
    user_id = request.args.get("userId") or request.form.get("userId")
    if not user_id:
        return jsonify({"error": "userId required"}), 400
    
    user_folder = get_user_folder(user_id)
    versions= get_last_n_versions(user_folder, 3)
    if not versions:
        return jsonify({"error": "No previous versions found"}), 400
    
    # StutterSongModel.pt results saved per recording in transcription.detect_stutter
    type_counts = {}
    recordings = []

    for version_num in sorted(versions):
        doc_ref = db.collection("transcripts").document(f"{user_id}_v{version_num}")
        model_doc = doc_ref.collection("model").document("full").get()

        if not model_doc.exists:
            continue

        model_data = model_doc.to_dict()
        stutters = []
        for name, t in model_data["types"].items():
            type_counts[name] = type_counts.get(name, 0) + t["num_segments"]
            for seg in t["segments"]:
                stutters.append({"type": name, "start": seg["start"], "end": seg["end"]})

        recordings.append({
            "version": version_num,
            "sentence": sentence_for(doc_ref.get()),
            "duration": model_data["duration_s"],
            "stutters": sorted(stutters, key=lambda s: s["start"]),
        })

    if not recordings:
        return jsonify({"Error: No Model Results Found"}), 404

    instances = sum(type_counts.values())
    types_found = [name for name, count in type_counts.items() if count > 0]
    stutterLevel = level_from_counts(instances, len(types_found))

    recordingName = f"{user_id}_v{versions[0]}"


    # Liam - Understand Below  
    doc_data = { 
        "recordingName": recordingName,
        "stutterLevel": stutterLevel,
        "songTier": SONG_TIERS.get(stutterLevel),
        "instances": instances,
        "typesFound": types_found,
        "typeCounts": type_counts,
        "recordings": recordings,
        }

    db.collection("stutters").document(recordingName).set(doc_data)
    return jsonify({
            "success": True,
            "id": recordingName,
            "stutterLevel": stutterLevel,
            "instances": instances,
            "typesFound": types_found,
        }), 201

@stutter_bp.route("/displaySev", methods = ["GET"])
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
    
    return jsonify({
        "StutterLevel": sL,
        "instances": data.get("instances", 0),
        "typesFound": data.get("typesFound", []),
        "recordings": data.get("recordings", []),
    })
