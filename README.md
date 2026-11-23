# BrainWave / Stutter-Song

BrainWave is a speech-practice prototype that analyzes short recordings and recommends songs with lyric videos. The frontend uses Next.js and React; the backend uses Flask, PyTorch, Wav2Vec2, and Firebase Firestore.

## How it works

1. The app retrieves three practice sentences from Firestore.
2. The user records each sentence in the browser.
3. The backend saves the recordings and analyzes them for interjections, repetitions, and prolongations/blocks.
4. The app combines results from the user's latest three recordings into an application-defined severity level.
5. When a song is recommended, the results page displays a YouTube lyric video. Recommendations consider tempo, song tags, and recently recommended songs.

## Requirements

- Python 3.12 (used in the local setup).
- Node.js 20.9 or newer (the installed Next.js package's minimum), and npm.
- FFmpeg available on your `PATH`.
- A Firebase project with Firestore enabled and a service account with access to the database.
- Internet access for Firestore, YouTube, and the initial speech-model download.

On macOS with Homebrew, install FFmpeg with:

```bash
brew install ffmpeg
```

## Backend setup

Run these commands from the repository root:

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install flask flask-cors firebase-admin numpy torch transformers
```

Python dependencies are not currently pinned in a requirements file.

Place your Firebase service-account credentials at `Backend/serviceAccountKey.json`. This file is ignored by Git. Keep the included model checkpoint, `Backend/StutterSongModel.pt`, in the same directory.

For a new Firestore database, create the document `Sentences/SkROjYeo8NiV76JyRnfR` with string fields `Sentence1` through `Sentence29`. The sentence route currently reads this specific document and randomly selects three of those fields. Upload the song catalog using the instructions below.

Start the backend from inside `Backend`:

```bash
source .venv/bin/activate
python server.py
```

The API runs at [http://localhost:5001](http://localhost:5001). The root URL returns 404 because no `/` route is defined. Keep this terminal running.

Startup loads the checkpoint and the `facebook/wav2vec2-base` backbone. The first run may download the backbone; subsequent runs can use its local cache. The backend currently uses the CPU. Run from `Backend` because credential, model, and recording paths are relative to the working directory.

## Frontend setup

In a second terminal, start from the repository root:

```bash
cd frontend-next
npm ci
```

Create or update `frontend-next/.env.local` with:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:5001
```

Start the frontend:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and allow microphone access. Restart the frontend after changing `.env.local`.

Other frontend commands, run inside `frontend-next`:

```bash
npm run lint
npm run build
npm start
```

`npm start` serves an existing production build, so run `npm run build` first.

## Lyric-video song catalog

The seed catalog lives in `Backend/songs.py`. It contains 25 songs with YouTube lyric-video IDs, BPM values, legacy threshold labels, and descriptive tags.

From `Backend`, with the virtual environment active, preview and validate the catalog:

```bash
python upload.py
```

This checks each video's YouTube oEmbed metadata and requires its title to identify it as a lyric video. It does not write to Firestore or guarantee playback in every region.

To apply the catalog to Firestore:

```bash
python upload.py --apply
```

The uploader validates the full catalog, backs up existing song documents to a JSON file in the system temporary directory, applies one atomic batch, and reads back the records to verify them. It prints the backup path. Existing creation timestamps and unrelated fields are preserved. If the database contains song IDs absent from the seed catalog, the upload stops for review instead of deleting them.

Each song record includes `youtubeId`, `youtubeUrl`, `youtubeTitle`, `youtubeChannel`, `videoType: "lyric"`, `bpm`, `songTier`, `threshold`, and `tags`.

### Tempo categories

The current recommendation route sorts the catalog by BPM and divides it into three groups. The uploader stores matching `songTier` values:

| Song tier | Current count | Recommended for |
| --- | ---: | --- |
| `slowest` | 9 | Major |
| `slower` | 9 | Average |
| `faster` | 7 | Minor |

These are relative groups within the catalog, not fixed BPM ranges. Counts and boundaries can change as songs are added. The older `threshold` field is retained for compatibility; the recommendation route uses the three tempo groups and song tags. No song is recommended for the `No Stutter` or `Warning` levels.

## Project layout

```text
Backend/
  server.py             Flask entry point
  core/state.py         Firebase and model initialization
  core/stutter_model.py Audio decoding and model inference
  routes/               Recording, sentence, analysis, and song endpoints
  StutterSongModel.pt    Trained classifier checkpoint
  recordings/           Local recordings grouped by user ID
frontend-next/
  src/app/page.tsx        Sentence recording flow
  src/app/result/         Analysis results and YouTube player
```

Firestore stores practice sentences, session sentence references, recording analysis, severity summaries, songs, and recent song choices. Audio files are stored locally in `Backend/recordings`; the browser keeps its user ID in local storage.

