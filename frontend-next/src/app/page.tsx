"use client";

import { useEffect, useRef, useState } from "react";


async function uploadMemo(blob: Blob) {
  const formData = new FormData();
  formData.append("recording", blob, "recording.mp4");

  const response = await fetch("http://localhost:5001/makeRecording", {
    method: "POST",
    body: formData,
  });

  return response.json();
}


 function RecordingButton(){
    const [recording, setRecording] = useState(false);
    const [upload, setUpload] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    const handleRec = async () => {
    if (!recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        stream.getTracks().forEach((t) => t.stop());
        await uploadMemo(blob); // Part 2
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

  // Liam - Understand This Too
  const analyzeStutter = async () => {
    
    try {
        const response = await fetch("http://127.0.0.1:5001/stutterSeverity", {
          method: "POST",
        });

        

        if (!response.ok) {
          const errorData = await response.json();
          console.error("Error:", errorData);
          return;
        }

        const data = await response.json();
        console.log("Stutter analysis result:", data);
        // e.g. setStutterResult(data) if you want to display it

    } catch (err) {
        console.error("Request failed:", err);
      }
  };

  return (
    <div className="flex flex-col items-center gap-4">
     <button
       onClick={handleRec}
       className={`w-40 rounded-full px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors duration-200 ${
         recording
           ? "bg-amber-500 hover:bg-amber-600"
           : "bg-[#2E8B57] hover:bg-[#256e46]"
       }`}
     >
       {recording ? "Stop" : "Record"}
     </button>

     <button
       onClick={analyzeStutter}
       className="w-40 rounded-full border border-stone-300 px-6 py-3 text-sm font-semibold text-stone-700 transition-colors duration-200 hover:border-[#2E8B57] hover:text-[#2E8B57]"
     >
      Analyze
     </button>
    </div>
  );
}


export default function Home() {
  const [sentence, setSentence] = useState(null);


  useEffect(() => {
    fetch("http://127.0.0.1:5001/get-sentence")
    // fetch("http://localhost:5001/get-sentence")
      .then((res) => res.json())
      .then((data) => setSentence(data.sentence));
  }, []);

  

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4">
      <div className="w-full max-w-md rounded-3xl border border-stone-200 bg-white p-10 text-center shadow-sm">
        <p className="mb-6 font-mono text-xs uppercase tracking-[0.2em] text-[#2E8B57]">
          StutterSong
        </p>

        <p className="font-serif text-2xl leading-snug text-stone-900"> {sentence} </p>

        <div className="my-8 h-px bg-stone-200" />

        <RecordingButton />
        {/* This Must Return A Button Instead of Putting It Here, Error Fixed */}
      </div>
    </main>
  );
}
