"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

const YOUTUBE_IFRAME_API_URL = "https://www.youtube.com/iframe_api";
const API_URL = process.env.NEXT_PUBLIC_API_URL;

type RecordingSummary = {
  version: number;
  sentence: string | null;
  duration: number;
  stutters: { type: string; start: number; end: number }[];
};

type Breakdown = {
  instances: number;
  typesFound: string[];
  recordings: RecordingSummary[];
};

// Model class names -> wording shown to users
const STUTTER_TYPES: Record<string, { label: string; description: string; dot: string; tile: string }> = {
  Repetition: {
    label: "Repeating",
    description: "Saying a sound or word more than once",
    dot: "bg-sky-500",
    tile: "bg-sky-50 text-sky-900",
  },
  "Prolong/Block": {
    label: "Stretching or getting stuck",
    description: "Holding a sound too long, or pausing before a word",
    dot: "bg-rose-500",
    tile: "bg-rose-50 text-rose-900",
  },
  Interjection: {
    label: "Filler sounds",
    description: "Extra sounds like \u201cum\u201d or \u201cuh\u201d",
    dot: "bg-amber-500",
    tile: "bg-amber-50 text-amber-900",
  },
};

const typeInfo = (type: string) =>
  STUTTER_TYPES[type] ?? { label: type, description: "", dot: "bg-stone-400", tile: "bg-stone-50 text-stone-900" };

const cleanSentence = (s: string) => s.replace(/^["\u201c\u201d']+|["\u201c\u201d']+$/g, "").trim();

const timeRange = (start: number, end: number) => `${Math.round(start)}\u2013${Math.round(end)}s`;

function groupByType(stutters: RecordingSummary["stutters"]) {
  const groups: Record<string, string[]> = {};
  for (const s of stutters) {
    (groups[s.type] ??= []).push(timeRange(s.start, s.end));
  }
  return Object.entries(groups);
}

export default function ResultPage() {
  return (
    <Suspense fallback={
      <main className="flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4 py-10">
        <p role="status" className="text-stone-600">Loading results…</p>
      </main>
    }>
      <ResultContent />
    </Suspense>
  );
}

function ResultContent() {
  const params = useSearchParams();
  const router = useRouter();
  const playerRef = useRef<HTMLDivElement>(null);
  const playerInstance = useRef<any>(null);
  const [playerReady, setPlayerReady] = useState(false);

  const level = params.get("level") ?? "Unknown";
  const youtubeId = params.get("youtubeId") ?? "";
  const songTitle = params.get("songTitle") ?? "";
  const artist = params.get("artist") ?? "";
  const bpm = params.get("bpm") ?? "";
  const message = params.get("message") ?? "";
  const reason = params.get("reason") ?? "";
  const [breakdown, setBreakdown] = useState<Breakdown | null>(null);

  useEffect(() => {
    const userId = localStorage.getItem("userId");
    if (!userId) return;
    fetch(`${API_URL}/stutter/displaySev?userId=${userId}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!data) return;
        setBreakdown({
          instances: data.instances ?? 0,
          typesFound: data.typesFound ?? [],
          recordings: data.recordings ?? [],
        });
      })
      .catch((err) => console.error("Breakdown request failed:", err));
  }, []);

  useEffect(() => {
    if (!youtubeId) return;

    // Load the IFrame API script once
    if (!window.YT) {
      const tag = document.createElement("script");
      tag.src = YOUTUBE_IFRAME_API_URL;
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

  const typeCounts: Record<string, number> = {};
  for (const rec of breakdown?.recordings ?? []) {
    for (const s of rec.stutters) typeCounts[s.type] = (typeCounts[s.type] ?? 0) + 1;
  }
  const hasBreakdown = !!breakdown && breakdown.recordings.length > 0;

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4 py-10">
      <div className="w-full max-w-5xl rounded-3xl border border-stone-200 bg-white p-8 shadow-sm md:p-10">
        <p className="mb-8 text-center font-mono text-xs uppercase tracking-[0.2em] text-[#2E8B57]">
          Results
        </p>

        <div className="grid gap-8 md:grid-cols-2">
          <section className="text-center md:text-left">
            <p className="font-serif text-lg text-stone-900">
              Stutter Level: <span className="font-semibold">{level}</span>
            </p>

            {songTitle && (
              <p className="mt-4 font-serif text-lg text-stone-900">Song Suggested: {songTitle}</p>
            )}

            {songTitle && (artist || bpm) && (
              <p className="mt-1 text-sm text-stone-500">
                {[artist, bpm && `${bpm} BPM`].filter(Boolean).join(" · ")}
              </p>
            )}

            {songTitle && reason && (
              <p className="mt-3 text-sm text-stone-600">{reason}</p>
            )}

            {!songTitle && message && (
              <p className="mt-4 text-sm text-stone-600">{message}</p>
            )}

            {youtubeId && (
              <div className="mt-6 aspect-video w-full overflow-hidden rounded-xl">
                <div ref={playerRef} className="h-full w-full" />
              </div>
            )}
          </section>

          {hasBreakdown && (
            <section>
              <p className="font-serif text-lg text-stone-900">What we heard</p>
              <p className="mt-1 text-sm text-stone-500">
                {breakdown.instances} possible stutter{breakdown.instances === 1 ? "" : "s"} across{" "}
                {breakdown.recordings.length} recording{breakdown.recordings.length === 1 ? "" : "s"}
              </p>

              <div className="mt-4 grid gap-3">
                {Object.keys(STUTTER_TYPES).map((type) => {
                  const info = typeInfo(type);
                  return (
                    <div key={type} className={`flex items-center gap-4 rounded-xl px-4 py-3 ${info.tile}`}>
                      <span className="w-8 text-center font-serif text-2xl">{typeCounts[type] ?? 0}</span>
                      <div>
                        <p className="text-sm font-semibold">{info.label}</p>
                        <p className="text-xs opacity-75">{info.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}
        </div>

        {hasBreakdown && (
          <>
            <div className="my-8 h-px bg-stone-200" />

            <ol className="grid gap-4 md:grid-cols-3">
              {breakdown.recordings.map((rec, i) => (
                <li key={rec.version} className="rounded-xl border border-stone-200 p-4">
                  <p className="font-mono text-xs uppercase tracking-[0.15em] text-[#2E8B57]">
                    Recording {i + 1}
                  </p>
                  {rec.sentence && (
                    <p className="mt-1 font-serif text-sm leading-snug text-stone-900">
                      &ldquo;{cleanSentence(rec.sentence)}&rdquo;
                    </p>
                  )}
                  {rec.stutters.length === 0 ? (
                    <p className="mt-3 text-sm text-stone-500">Sounded smooth, nothing flagged</p>
                  ) : (
                    <ul className="mt-3 space-y-2 text-sm text-stone-700">
                      {groupByType(rec.stutters).map(([type, times]) => (
                        <li key={type} className="flex items-start gap-2">
                          <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${typeInfo(type).dot}`} />
                          <span>
                            {typeInfo(type).label}
                            <span className="text-stone-500">
                              {" · "}
                              {times.map((t, k) => (
                                <span key={k} className="whitespace-nowrap">
                                  {t}{k < times.length - 1 ? ", " : ""}
                                </span>
                              ))}
                            </span>
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ol>

            <p className="mt-4 text-center text-xs text-stone-400">
              Results might not be accurate. Times are approximate. This is practice feedback, not a diagnosis.
            </p>
          </>
        )}

        <div className="mt-8 flex justify-center">
          <button
            onClick={() => router.push("/")}
            className="w-40 rounded-full border border-stone-300 px-6 py-3 text-sm font-semibold text-stone-700 transition-colors duration-200 hover:border-[#2E8B57] hover:text-[#2E8B57]"
          >
            Try Again
          </button>
        </div>
      </div>
    </main>
  );
}
