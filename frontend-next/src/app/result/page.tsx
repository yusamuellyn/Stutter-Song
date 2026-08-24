"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export default function ResultPage() {
  const params = useSearchParams();
  const router = useRouter();
  const playerRef = useRef<HTMLDivElement>(null);
  const playerInstance = useRef<any>(null);
  const [playerReady, setPlayerReady] = useState(false);

  const level = params.get("level") ?? "Unknown";
  const youtubeId = params.get("youtubeId") ?? "";
  const songTitle = params.get("songTitle") ?? "";

  useEffect(() => {
    if (!youtubeId) return;

    // Load the IFrame API script once
    if (!window.YT) {
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      document.body.appendChild(tag);
    }

    const createPlayer = () => {
      if (!playerRef.current) return;
      playerInstance.current = new window.YT.Player(playerRef.current, {
        videoId: youtubeId,
        playerVars: { autoplay: 0, rel: 0 },
        events: {
          onReady: () => setPlayerReady(true),
          onStateChange: (event: any) => {
            // event.data === 0 means the video ended
            if (event.data === 0) {
              console.log("Song finished");
            }
          },
        },
      });
    };

    if (window.YT && window.YT.Player) {
      createPlayer();
    } else {
      window.onYouTubeIframeAPIReady = createPlayer;
    }

    return () => {
      playerInstance.current?.destroy?.();
    };
  }, [youtubeId]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4">
      <div className="w-full max-w-md rounded-3xl border border-stone-200 bg-white p-10 text-center shadow-sm">
        <p className="mb-6 font-mono text-xs uppercase tracking-[0.2em] text-[#2E8B57]">
          Results
        </p>

        <p className="font-serif text-lg text-stone-900">
          Stutter Level: <span className="font-semibold">{level}</span>
        </p>

        {songTitle && (
          <p className="mt-4 font-serif text-lg text-stone-900">Song Suggested: {songTitle}</p>
        )}

        {youtubeId && (
          <div className="mt-6 aspect-video w-full overflow-hidden rounded-xl">
            <div ref={playerRef} className="h-full w-full" />
          </div>
        )}

        <button
          onClick={() => router.push("/")}
          className="mt-8 w-40 rounded-full border border-stone-300 px-6 py-3 text-sm font-semibold text-stone-700 transition-colors duration-200 hover:border-[#2E8B57] hover:text-[#2E8B57]"
        >
          Try Again
        </button>
      </div>
    </main>
  );
}