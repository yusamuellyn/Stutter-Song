# songs.py
# youtube_id points to each song's official video/audio upload on YouTube.
# Embed these with the YouTube IFrame Player API rather than downloading
# or rehosting the audio yourself.
#
# threshold: placeholder set to 0 for all songs for now — update later
#            once severity matching logic is finalized.
#
# NOTE: "Home" is excluded since it wasn't in the original midi/ folder.
# NOTE: "Leon-On-Me.mid" from the original file list is assumed to be a
#       typo for "Lean On Me" (Bill Withers).

songs = [
    {
        "id": "lean-on-me",
        "title": "Lean on Me",
        "artist": "Bill Withers",
        "bpm": 74,
        "threshold": 0,
        "tags": ["slow-start", "repetitive", "familiar"],
        "youtube_id": "Nx_D0VTHBag",
    },
    {
        "id": "stand-by-me",
        "title": "Stand By Me",
        "artist": "Ben E. King",
        "bpm": 118,
        "threshold": 0,
        "tags": ["slow-start", "iconic", "predictable-melody"],
        "youtube_id": "7rZyI7kPZMI",
    },
    {
        "id": "somewhere-over-the-rainbow",
        "title": "Somewhere Over the Rainbow",
        "artist": "Israel Kamakawiwoʻole",
        "bpm": 84,
        "threshold": 0,
        "tags": ["slow", "sustained-notes", "familiar"],
        "youtube_id": "1TLANYvPGPE",
    },
    {
        "id": "let-it-be",
        "title": "Let It Be",
        "artist": "The Beatles",
        "bpm": 73,
        "threshold": 0,
        "tags": ["slow-start", "repetitive-title"],
        "youtube_id": "dSSqHhAqxrk",
    },
    {
        "id": "count-on-me",
        "title": "Count on Me",
        "artist": "Bruno Mars",
        "bpm": 122,
        "threshold": 0,
        "tags": ["steady-tempo", "repetitive-hook"],
        "youtube_id": "6k8cpUkKK4c",
    },
    {
        "id": "perfect",
        "title": "Perfect",
        "artist": "Ed Sheeran",
        "bpm": 63,
        "threshold": 0,
        "tags": ["moderate-pace", "familiar"],
        "youtube_id": "kPhpHvnnn0Q",
    },
    {
        "id": "three-little-birds",
        "title": "Three Little Birds",
        "artist": "Bob Marley",
        "bpm": 76,
        "threshold": 0,
        "tags": ["very-repetitive", "reggae-backbeat"],
        "youtube_id": "4MBzzJFsF2A",
    },
    {
        "id": "im-yours",
        "title": "I'm Yours",
        "artist": "Jason Mraz",
        "bpm": 137,
        "threshold": 0,
        "tags": ["laid-back-groove", "repeated-phrasing"],
        "youtube_id": "w5qOYi41WiA",
    },
    {
        "id": "what-a-wonderful-world",
        "title": "What a Wonderful World",
        "artist": "Louis Armstrong",
        "bpm": 84,
        "threshold": 0,
        "tags": ["slow-moderate", "iconic", "low-lyrical-density"],
        "youtube_id": "1Z0Y7hY6jSY",
    },
    {
        "id": "dont-stop-believin",
        "title": "Don't Stop Believin'",
        "artist": "Journey",
        "bpm": 119,
        "threshold": 0,
        "tags": ["driving-rhythm", "well-known", "phrase-repetition"],
        "youtube_id": "Pze8Dyqiky8",
    },
    {
        "id": "shape-of-you",
        "title": "Shape of You",
        "artist": "Ed Sheeran",
        "bpm": 96,
        "threshold": 0,
        "tags": ["repetitive-hooks", "strong-beat"],
        "youtube_id": "liTfD88dbCo",
    },
    {
        "id": "uptown-funk",
        "title": "Uptown Funk",
        "artist": "Bruno Mars",
        "bpm": 115,
        "threshold": 0,
        "tags": ["highly-rhythmic", "syllable-to-beat-mapping"],
        "youtube_id": "W8FUmkw3a4U",
    },
    {
        "id": "happy",
        "title": "Happy",
        "artist": "Pharrell Williams",
        "bpm": 160,
        "threshold": 0,
        "tags": ["driving", "repetitive-chorus", "upbeat"],
        "youtube_id": "KmAbeMvjBmk",
    },
    {
        "id": "livin-on-a-prayer",
        "title": "Livin' on a Prayer",
        "artist": "Bon Jovi",
        "bpm": 122,
        "threshold": 0,
        "tags": ["anthemic", "strong-rhythmic-pulse"],
        "youtube_id": "ohFtQIPqGSo",
    },
]