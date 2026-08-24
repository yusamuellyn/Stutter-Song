"use client";

import { useSearchParams, useRouter } from "next/navigation";

export default function ResultPage(){
    const params = useSearchParams();
    const router = useRouter();

    const level = params.get("level"); 

    return (
        <main className = "flex min-h-screen items-center justify-center bg-[#F4FAF7] px-4">
            <div className = "w-full max-w-md rounded-3xl border border-stone-200 bg-white p-10 text-center shadow-sm">
                <p className = "mb-6 font-mono text-xs uppercase tracking-[0.2em] text-[#2E8B57]">
                    Results
                </p>

                <p className = "font-serif text-lg text-stone-900">
                    Stutter Level: <span className="font-semibold">{level}</span>
                </p>

            </div>
        </main>
    )
}