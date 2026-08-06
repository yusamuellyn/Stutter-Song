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

  return (
    <button onClick={handleRec}>
      {recording ? "Stop" : "Record"}
    </button>
  );
}


export default function Home() {
  const [sentence, setSentence] = useState(null);


  useEffect(() => {
    fetch("http://localhost:5001/get-sentence")
      .then((res) => res.json())
      .then((data) => setSentence(data.sentence));
  }, []);

  

  return (
    <div>
    <p> {sentence} </p>
    
    <RecordingButton /> 
    {/* This Must Return A Button Instead of Putting It Here, Error Fixed */}
    </div>
  );
}
