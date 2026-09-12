from flask import Blueprint, jsonify
import random
import uuid

from core.state import db

sentences_bp = Blueprint("sentences", __name__, url_prefix="/sentences")

@sentences_bp.route("/get-sentence", methods = ["GET"])
def getSentence():

    randomSentenceNums = random.sample(range(1,30),3)

 
    doc_ref = db.collection("Sentences").document("SkROjYeo8NiV76JyRnfR")
    doc = doc_ref.get()  # fetches the document from Firestore

    if not doc.exists:
        return jsonify({"error": "document not found"}), 404

    data = doc.to_dict()  # turns the document into a normal Python dict
    sentences = [data.get(f"Sentence{n}") for n in randomSentenceNums]

    sentence_rem_id = str(uuid.uuid4())
    db.collection("sentenceRems").document(sentence_rem_id).set({"sentence": sentences})

    return jsonify({"sentence": sentences, "SRI": sentence_rem_id})
