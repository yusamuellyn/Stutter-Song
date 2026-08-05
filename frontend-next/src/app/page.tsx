"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [sentence, setSentence] = useState(null);


  useEffect(() => {
    fetch("http://localhost:5001/get-sentence")
      .then((res) => res.json())
      .then((data) => setSentence(data.sentence));
  }, []);

  return (
    <p> {sentence} </p>
  );
}
