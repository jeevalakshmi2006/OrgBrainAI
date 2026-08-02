"use client";
import { useState, useRef, useEffect } from "react";

/**
 * A text input with an optional microphone button that uses the browser's
 * built-in Web Speech API (SpeechRecognition) to convert speech to text
 * automatically - no external API or key needed. Falls back to typing-only
 * if the browser doesn't support it (e.g. Firefox).
 */
export default function SpeechTextInput({ value, onChange, onSubmit, disabled, placeholder }) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);
    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      onChange(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, [onChange]);

  function toggleListening() {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      onChange("");
      recognitionRef.current.start();
      setListening(true);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex gap-2 items-center">
      <div className="relative flex-1">
        <input
          className="input-field pr-10"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
        />
        {supported && (
          <button
            type="button"
            onClick={toggleListening}
            disabled={disabled}
            title={listening ? "Stop recording" : "Speak your answer"}
            className={`absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full flex items-center justify-center transition-colors ${
              listening ? "bg-red-500 text-white animate-pulse" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
            }`}
          >
            🎤
          </button>
        )}
      </div>
      <button type="submit" disabled={disabled} className="btn-primary whitespace-nowrap">
        {disabled ? "Sending..." : "Send"}
      </button>
    </form>
  );
}
