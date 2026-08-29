# songs.py
#
# threshold is categorized using the application's BPM thresholds:
# 60 - 86 BPM   = "major"
# 87 - 112 BPM  = "average"
# 113 - 140 BPM = "minor"
# 140+ BPM      = "none"
#
# NOTE:
# These thresholds are application-specific and should not be interpreted
# as clinical diagnostic criteria for stuttering.
#
# YouTube IDs point to songs on YouTube. Use the YouTube IFrame Player API
# rather than downloading or rehosting audio.

songs = [
    # ============================================================
    # MAJOR STUTTER — 60-86 BPM
    # ============================================================

    {
        "id": "lean-on-me",
        "title": "Lean on Me",
        "artist": "Bill Withers",
        "bpm": 74,
        "threshold": "major",
        "tags": ["slow-start", "repetitive", "familiar"],
        "youtube_id": "Nx_D0VTHBag",
    },
    {
        "id": "somewhere-over-the-rainbow",
        "title": "Somewhere Over the Rainbow",
        "artist": "Israel Kamakawiwoʻole",
        "bpm": 84,
        "threshold": "major",
        "tags": ["slow", "sustained-notes", "familiar"],
        "youtube_id": "1TLANYvPGPE",
    },
    {
        "id": "let-it-be",
        "title": "Let It Be",
        "artist": "The Beatles",
        "bpm": 73,
        "threshold": "major",
        "tags": ["slow-start", "repetitive-title"],
        "youtube_id": "dSSqHhAqxrk",
    },
    {
        "id": "perfect",
        "title": "Perfect",
        "artist": "Ed Sheeran",
        "bpm": 63,
        "threshold": "major",
        "tags": ["slow", "familiar", "sustained-phrasing"],
        "youtube_id": "kPhpHvnnn0Q",
    },
    {
        "id": "three-little-birds",
        "title": "Three Little Birds",
        "artist": "Bob Marley",
        "bpm": 76,
        "threshold": "major",
        "tags": ["repetitive", "reggae-backbeat", "predictable"],
        "youtube_id": "4MBzzJFsF2A",
    },
    {
        "id": "what-a-wonderful-world",
        "title": "What a Wonderful World",
        "artist": "Louis Armstrong",
        "bpm": 84,
        "threshold": "major",
        "tags": ["slow-moderate", "iconic", "low-lyrical-density"],
        "youtube_id": "1Z0Y7hY6jSY",
    },
    {
        "id": "hallelujah",
        "title": "Hallelujah",
        "artist": "Leonard Cohen",
        "bpm": 56,
        "threshold": "major",
        "tags": ["slow", "repetitive-hook", "sustained-notes"],
        "youtube_id": "YrLk4vdY28Q",
    },
    {
        "id": "take-me-home-country-roads",
        "title": "Take Me Home, Country Roads",
        "artist": "John Denver",
        "bpm": 82,
        "threshold": "major",
        "tags": ["steady", "repetitive-chorus", "familiar"],
        "youtube_id": "1vrEljMfXYo",
    },


    # ============================================================
    # AVERAGE STUTTER — 87-112 BPM
    # ============================================================

    {
        "id": "stand-by-me",
        "title": "Stand By Me",
        "artist": "Ben E. King",
        "bpm": 118,
        "threshold": "minor",
        "tags": ["iconic", "predictable-melody"],
        "youtube_id": "7rZyI7kPZMI",
    },
    {
        "id": "shape-of-you",
        "title": "Shape of You",
        "artist": "Ed Sheeran",
        "bpm": 96,
        "threshold": "average",
        "tags": ["repetitive-hooks", "strong-beat"],
        "youtube_id": "liTfD88dbCo",
    },
    {
        "id": "yellow",
        "title": "Yellow",
        "artist": "Coldplay",
        "bpm": 87,
        "threshold": "average",
        "tags": ["steady", "repetitive", "familiar"],
        "youtube_id": "yKNxeF4KMsY",
    },
    {
        "id": "ho-hey",
        "title": "Ho Hey",
        "artist": "The Lumineers",
        "bpm": 83,
        "threshold": "major",
        "tags": ["repetitive-chorus", "simple-phrasing"],
        "youtube_id": "zvCBSSwgtg4",
    },
    {
        "id": "somebody-that-i-used-to-know",
        "title": "Somebody That I Used To Know",
        "artist": "Gotye",
        "bpm": 129,
        "threshold": "minor",
        "tags": ["repetitive", "strong-pulse", "phrase-repetition"],
        "youtube_id": "8UVNT4wvIGY",
    },
    {
        "id": "just-the-two-of-us",
        "title": "Just the Two of Us",
        "artist": "Grover Washington Jr.",
        "bpm": 95,
        "threshold": "average",
        "tags": ["steady-groove", "repetitive-hook", "smooth"],
        "youtube_id": "6POZlJAZsok",
    },


    # ============================================================
    # MINOR STUTTER — 113-140 BPM
    # ============================================================

    {
        "id": "count-on-me",
        "title": "Count on Me",
        "artist": "Bruno Mars",
        "bpm": 122,
        "threshold": "minor",
        "tags": ["steady-tempo", "repetitive-hook"],
        "youtube_id": "6k8cpUkKK4c",
    },
    {
        "id": "im-yours",
        "title": "I'm Yours",
        "artist": "Jason Mraz",
        "bpm": 137,
        "threshold": "minor",
        "tags": ["laid-back-groove", "repeated-phrasing"],
        "youtube_id": "w5qOYi41WiA",
    },
    {
        "id": "dont-stop-believin",
        "title": "Don't Stop Believin'",
        "artist": "Journey",
        "bpm": 119,
        "threshold": "minor",
        "tags": ["driving-rhythm", "well-known", "phrase-repetition"],
        "youtube_id": "Pze8Dyqiky8",
    },
    {
        "id": "livin-on-a-prayer",
        "title": "Livin' on a Prayer",
        "artist": "Bon Jovi",
        "bpm": 122,
        "threshold": "minor",
        "tags": ["anthemic", "strong-rhythmic-pulse"],
        "youtube_id": "ohFtQIPqGSo",
    },
    {
        "id": "uptown-funk",
        "title": "Uptown Funk",
        "artist": "Bruno Mars",
        "bpm": 115,
        "threshold": "minor",
        "tags": ["highly-rhythmic", "syllable-to-beat-mapping"],
        "youtube_id": "W8FUmkw3a4U",
    },
    {
        "id": "i-want-it-that-way",
        "title": "I Want It That Way",
        "artist": "Backstreet Boys",
        "bpm": 99,
        "threshold": "average",
        "tags": ["repetitive-chorus", "predictable", "familiar"],
        "youtube_id": "4fndeDfaWCg",
    },


    # ============================================================
    # NO STUTTER — 140+ BPM
    # ============================================================

    {
        "id": "happy",
        "title": "Happy",
        "artist": "Pharrell Williams",
        "bpm": 160,
        "threshold": "none",
        "tags": ["driving", "repetitive-chorus", "upbeat"],
        "youtube_id": "ZbZSe6N_BXs",
    },
    {
        "id": "shake-it-off",
        "title": "Shake It Off",
        "artist": "Taylor Swift",
        "bpm": 160,
        "threshold": "none",
        "tags": ["fast", "repetitive-chorus", "strong-beat"],
        "youtube_id": "nfWlot6h_JM",
    },
    {
        "id": "firework",
        "title": "Firework",
        "artist": "Katy Perry",
        "bpm": 124,
        "threshold": "minor",
        "tags": ["anthemic", "strong-beat", "repetitive-hook"],
        "youtube_id": "QGJuMBdaqIw",
    },
    {
        "id": "blinding-lights",
        "title": "Blinding Lights",
        "artist": "The Weeknd",
        "bpm": 171,
        "threshold": "none",
        "tags": ["fast", "driving", "repetitive"],
        "youtube_id": "4NRXx6U8ABQ",
    },
    {
        "id": "cant-stop-the-feeling",
        "title": "Can't Stop the Feeling!",
        "artist": "Justin Timberlake",
        "bpm": 113,
        "threshold": "minor",
        "tags": ["upbeat", "repetitive-hook", "danceable"],
        "youtube_id": "ru0K8uYEZWw",
    },
]