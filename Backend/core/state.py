import os
import whisperx
import firebase_admin
from firebase_admin import credentials, firestore

def get_next_version(user_folder):
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return 1
    return max(get_version_number(f) for f in existing) + 1

def get_latest_version(user_folder):
    if not os.path.isdir(user_folder):
        return None
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return None
    return max(get_version_number(f) for f in existing)

def get_user_folder(user_id):
    folder = os.path.join(audio_folder, user_id)
    os.makedirs(folder, exist_ok=True)
    return folder

def get_last_n_versions(user_folder, n=3):
    if not os.path.isdir(user_folder):
        return []
    existing = [f for f in os.listdir(user_folder) if f.startswith("rec_v")]
    if not existing:
        return []
    versions = sorted({get_version_number(f) for f in existing}, reverse=True)
    return versions[:n]

device = "cpu"
ts_model = whisperx.load_model("large-v3", device)

audio_folder = "recordings"
os.makedirs(audio_folder, exist_ok= True)

audio_path = os.path.join(audio_folder, "most_recent_rec.mp4")

recording_extensions = {"mp4", "wav", "webm"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in recording_extensions

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

model = None

def get_version_number(filename):
    return int(filename.split("_v")[1].split(".")[0])
