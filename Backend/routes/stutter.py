from flask import Blueprint, request, jsonify

from core.state import db, get_user_folder, get_last_n_versions, get_latest_version

stutter_bp = Blueprint("stutter", __name__, url_prefix="/stutter")

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
    
    stutterLevel = "None"
    
    scores = []
    number_Stutters = 0
    # existing = [f for f in os.listdir(audio_folder) if f.startswith("most_recent_rec_v")]
    
    # if not existing:
    #     return jsonify({"Error: No Previous Versions Found"}), 400

    # last_file = max(existing, key=get_version_number)
    # version_num = get_version_number(last_file)

    for version_num in versions:
        doc_ref = db.collection("transcripts").document(f"{user_id}_v{version_num}")

        parent_doc = doc_ref.get()
        sentence = None
        if parent_doc.exists:
            sentence = parent_doc.to_dict().get("sentence")

        text_doc = doc_ref.collection("text").document("full").get()
        scores_doc = doc_ref.collection("scores").document("full").get()

    


        if not text_doc.exists or not scores_doc.exists:
            continue

        text_data = text_doc.to_dict()
        scores_data = scores_doc.to_dict()

        text = text_data["text"]
        version_scores = scores_data["scores"]

        if not version_scores:
         continue
            
        scores.extend(version_scores)

        separate_text = text.split()
        separate_text = [word.lower().strip() for word in separate_text]
        w = 0
        while w < len(separate_text):
            if (w + 1 < len(separate_text)) and separate_text[w] == separate_text[w + 1]:
                    number_Stutters += 1
            w += 1
        

    if not scores:
        return jsonify({"Error: No Scores Found"}), 404

    avg_Word_Score = 0 

    for s in scores:
        avg_Word_Score = avg_Word_Score + float(s)

    avg_Word_Score = avg_Word_Score / len(scores)


    separate_text = [word.lower().strip() for word in separate_text]
    w = 0 


    while w < len(separate_text):
        if (w + 1 < len(separate_text)) and separate_text[w] == separate_text[w + 1]:
            number_Stutters += 1

        w += 1

    partial_stutters = 0
    words_stuttered = []
    sentence_words = sentence.split()

    # Do Front/Backend Thing and Partial Report Thursday
    # Debug Sentence ASAP

    for wrd in sentence_words:
        iter_builder = [] 
        lenWrd = len(wrd) - 1 
        for a in range(lenWrd):
            iter_builder.append(wrd[:a + 1]) 

        for pt in iter_builder:
            if pt in separate_text:
                partial_stutters += 1
                

       

    
    if avg_Word_Score <= .400 and number_Stutters == 1:
        stutterLevel = "Minor"

    elif avg_Word_Score <= .300 and (number_Stutters == 2 or number_Stutters == 3):
        stutterLevel = "Average"

    elif avg_Word_Score <= .200 and number_Stutters > 4:
        stutterLevel = "Major"

    else:
        stutterLevel = "No Stutter"

    recordingName = f"{user_id}_v{versions[0]}"


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
    
    return jsonify({"StutterLevel": sL})
