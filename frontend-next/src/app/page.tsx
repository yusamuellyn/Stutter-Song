"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function uploadMemo(blob: Blob, userId:string, SRI:string | null, sentenceIndex: number) {
  const formData = new FormData();
  formData.append("recording", blob, "recording.mp4");
  formData.append("sentenceIndex", String(sentenceIndex))

  if(userId){
    formData.append("userID", userId);
  }
  if(SRI){formData.append("SRI", SRI )}

  const response = await fetch(`${API_URL}/recordings/makeRecording`, {
    method: "POST",
    body: formData,
  });

  return response.json();
}
function getUserId(): string{
  return localStorage.getItem("userId") ?? "";
}

function saveUserId(id: string){
  localStorage.setItem("userId", id);
}

interface RecordingButtonProps{
  sentences: string[];
  currentIndex: number;
  setCurrentIndex: (i: number) => void;
  SRI: string | null;
}
function RecordingButton({ sentences, currentIndex, setCurrentIndex, SRI }: RecordingButtonProps) {
  const router = useRouter();
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [stutterResult, setStutterResult] = useState(null);
  const userIdRef = useRef<string>("");
  const totalSentences = sentences.length;
  const allRecorded = totalSentences > 0 && currentIndex >= totalSentences;
  const queueRef = useRef<{blob: Blob; sentenceIndex: number}[]>([]);
  const processingRef = useRef(false);
  const [pendingCount, setPendingCount] = useState(0);
  const allSaved = allRecorded && pendingCount === 0;


  useEffect(() => {
    userIdRef.current = getUserId(); // empty string on first-ever visit — that's fine
  }, []);
  
  // False or True For Bool / Null For Objects In useState

  const handleRec = async () => {
    setStutterResult(null);
    if (!recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      const sentenceIndexForThisTake = currentIndex;

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        stream.getTracks().forEach((t) => t.stop());
        
        enqueueUpload(blob, sentenceIndexForThisTake);
        setCurrentIndex(sentenceIndexForThisTake + 1);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setRecording(true);
    } else {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      setRecording(false);
    }
  };

  const processQueue = async () => {
    if (processingRef.current) return;
    processingRef.current = true;
  
    while (queueRef.current.length > 0) {
      const next = queueRef.current.shift()!;
      try {
        const result = await uploadMemo(next.blob, userIdRef.current, SRI, next.sentenceIndex);
        if (result?.userId) {
          userIdRef.current = result.userId;
          saveUserId(result.userId);
        }
      } catch (err) {
        console.error("Upload failed for sentence", next.sentenceIndex, err);
      } finally {
        setPendingCount((c) => Math.max(0, c - 1));
      }
    }
  
    processingRef.current = false;
  };
  
  const enqueueUpload = (blob: Blob, sentenceIndex: number) => {
    queueRef.current.push({ blob, sentenceIndex });
    setPendingCount((c) => c + 1);
    processQueue();
  };

  // Liam - Understand This Too
  const analyzeStutter = async () => {
    try {
      const response = await fetch(`${API_URL}/stutter/stutterSeverity?userId=${userIdRef.current}`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error:", errorData);
        return;
      }

      const data = await displayStutter();

      const songRes = await fetch(
        `${API_URL}/songs/display-song?userId=${userIdRef.current}`
      );
      const songData = await songRes.json();

      const params = new URLSearchParams({
        level: String(data.StutterLevel),
        youtubeId: songData.youtubeId ?? "",
        songTitle: songData.title ?? "",
        artist: songData.artist ?? "",
        bpm: songData.bpm ? String(songData.bpm) : "",
        message: songData.message ?? "",
        reason: songData.reason ?? "",
      });
      router.push(`/result?${params.toString()}`);
    } catch (err) {
      console.error("Request failed:", err);
    }
  };

  const displayStutter = async () => {
    const response = await fetch(`${API_URL}/stutter/displaySev?userId=${userIdRef.current}`, {
      method: "GET",
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error:", errorData);
      return;
    }

    const data = await response.json();
    return data;
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {totalSentences > 0 && (
        <p className="font-mono text-xs uppercase tracking-[0.15em] text-stone-500">
          {allRecorded ? "All sentences recorded" : `Sentence ${currentIndex + 1} of ${totalSentences}`}
        </p>
      )}

      {pendingCount > 0 && (
        <p className="font-mono text-xs text-stone-400">
          Saving {pendingCount} recording{pendingCount > 1 ? "s" : ""}...
        </p>
      )}

      <button
        onClick={handleRec}
        disabled={allRecorded}
        className={`w-40 rounded-full px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors duration-200 ${
          recording
            ? "bg-amber-500 hover:bg-amber-600"
            : "bg-[#2E8B57] hover:bg-[#256e46]"
        } disabled:cursor-not-allowed disabled:opacity-50`}
      >
        {recording ? "Stop" : "Record"}
      </button>

      <button
        onClick={analyzeStutter}
        disabled={!allSaved}
        className="w-40 rounded-full border border-stone-300 px-6 py-3 text-sm font-semibold text-stone-700 transition-colors duration-200 hover:border-[#2E8B57] hover:text-[#2E8B57] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {allRecorded && !allSaved ? "Saving..." : "Analyzation Available"}
      </button>

      {stutterResult && (
        <p className="mt-6 font-serif text-lg text-stone-900">
          Result: {stutterResult}
        </p>
      )}
    </div>
  );
}

export default function Home() {
const [sentences, setSentences] = useState<string[]>([]);
const [currentIndex, setCurrentIndex] = useState(0);
  const [SRI, setSRI] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/sentences/get-sentence`)
    .then((res) => res.json())
    .then((data) => {
      setSentences(data.sentence ?? []);
      setSRI(data.SRI);
    });
}, []);

return (
  <main className="flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4">
    <div className="w-full max-w-md rounded-3xl border border-stone-200 bg-white p-10 text-center shadow-sm">
      <p className="mb-6 font-mono text-xs uppercase tracking-[0.2em] text-[#2E8B57]">
        StutterSong
      </p>

      <div role="note" className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-left text-sm text-amber-900">
        <p className="font-semibold">Before you record</p>
        <p className="mt-1">
          You must speak clearly and slowly when reading each sentence. Rushed or mumbled speech
          can make the results inaccurate.
        </p>
      </div>

      <ol className="space-y-4 text-left">
        {sentences.map((s, i) => {
          const isActive = i === currentIndex;
          const isDone = i < currentIndex;
          return (
            <li key={i} className={`font-serif text-2xl leading-snug ${isActive ? "text-stone-900" : isDone ? "text-stone-400 line-through" : "text-stone-300"}`}>
              <span className="mr-2 font-mono text-sm text-[#2E8B57] align-top">{i + 1}.</span>
              {s}
            </li>
          );
        })}
      </ol>

      <div className="my-8 h-px bg-stone-200" />

      <RecordingButton
        sentences={sentences}
        currentIndex={currentIndex}
        setCurrentIndex={setCurrentIndex}
        SRI = {SRI}
      />
    </div>
  </main>
);
}