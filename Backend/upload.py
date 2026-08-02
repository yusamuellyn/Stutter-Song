"""
bulk_upload.py

Writes each song's metadata (including its YouTube video ID) directly to
Firestore, using the entries defined in songs.py. No local MIDI files or
running Flask server required — lyrics/audio playback are handled via the
YouTube IFrame Player API on the frontend instead.

Setup:
1. Make sure serviceAccountKey.json is in this directory (same one
   server.py uses).

2. Run this script:
     python bulk_upload.py
"""

import firebase_admin
from firebase_admin import credentials, firestore
from songs import songs

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def upload_song(song: dict) -> bool:
    doc_data = {
        "title": song["title"],
        "artist": song["artist"],
        "bpm": song.get("bpm"),
        "threshold": song.get("threshold", 0),
        "tags": song.get("tags", []),
        "youtubeId": song.get("youtube_id", ""),
        "createdAt": firestore.SERVER_TIMESTAMP,
    }

    try:
        db.collection("songs").document(song["id"]).set(doc_data)
        print(f'✅ "{song["title"]}" — uploaded')
        return True
    except Exception as e:
        print(f'❌ "{song["title"]}" — failed ({e})')
        return False


def main():
    print(f"Uploading {len(songs)} songs to Firestore...\n")
    succeeded = 0
    for song in songs:
        if upload_song(song):
            succeeded += 1
    print(f"\nDone. {succeeded}/{len(songs)} uploaded successfully.")


if __name__ == "__main__":
    main()