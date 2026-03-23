/**
 * @file Voice Assistant page — dual-mode AI business Q&A.
 *
 * Two interaction modes:
 * - Text mode (default): type questions, get text-only answers. No audio.
 * - Voice mode: speech-to-text input via Web Speech API, browser TTS reads
 *   the answer aloud. Toggle with the mode switch.
 *
 * Both modes hit the same /api/voice/{org_id}/ask endpoint.
 */
"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  FileText,
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  MessageSquare,
  Lightbulb,
  Type,
} from "lucide-react";
import {
  getVoiceSummary,
  getVoiceBrief,
  askVoiceQuestion,
} from "@/lib/api";
import { useOrg } from "@/lib/org-context";

/** A single chat message (user or assistant). */
interface Message {
  role: "user" | "assistant";
  text: string;
  source?: string;
  timestamp: Date;
}

/** Suggested starter questions for new users. */
const SUGGESTIONS = [
  "How is my business doing?",
  "What are my overdue invoices?",
  "What are my top risks?",
  "How much revenue have I made?",
  "What is my tax position?",
  "What should I focus on this week?",
];

export default function VoicePage() {
  const { orgId } = useOrg();

  // --- Chat state ---
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // --- Mode state: "text" (default) or "voice" ---
  const [mode, setMode] = useState<"text" | "voice">("text");

  // --- Voice-specific state ---
  const [listening, setListening] = useState(false);
  const [briefLoading, setBriefLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [micSupported, setMicSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  // --- Initialise Web Speech API (speech-to-text) if available ---
  useEffect(() => {
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    setMicSupported(!!SR);
    if (SR) {
      const recognition = new SR();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setListening(false);
        // In voice mode, auto-send after transcription
        if (transcript.trim()) {
          setTimeout(() => sendMessage(transcript), 200);
        }
      };
      recognition.onerror = () => setListening(false);
      recognition.onend = () => setListening(false);
      recognitionRef.current = recognition;
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // --- Auto-scroll chat to bottom ---
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- Stop any ongoing TTS when switching to text mode ---
  const handleModeSwitch = (newMode: "text" | "voice") => {
    if (newMode === "text" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
    }
    setMode(newMode);
  };

  // --- Mic toggle (voice mode only) ---
  const toggleMic = useCallback(() => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  }, [listening]);

  // --- Stop TTS playback ---
  const stopSpeaking = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  };

  // --- Send a question to the backend ---
  const sendMessage = useCallback(
    async (text?: string) => {
      const q = (text || input).trim();
      if (!q || loading) return;
      setInput("");

      const userMsg: Message = { role: "user", text: q, timestamp: new Date() };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      try {
        const res = await askVoiceQuestion(orgId, q);
        const answer = res.answer || "I could not generate an answer.";
        const botMsg: Message = {
          role: "assistant",
          text: answer,
          source: res.source,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);

        // In voice mode, read the answer aloud via browser TTS
        if (mode === "voice" && "speechSynthesis" in window) {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(answer);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          utterance.onstart = () => setSpeaking(true);
          utterance.onend = () => setSpeaking(false);
          utterance.onerror = () => setSpeaking(false);
          window.speechSynthesis.speak(utterance);
        }
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "Sorry, something went wrong. Please try again.",
            timestamp: new Date(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [input, loading, orgId, mode],
  );

  // --- Generate text briefing (both modes) ---
  const generateBrief = async () => {
    setBriefLoading(true);
    try {
      const data = await getVoiceSummary(orgId);
      const text = data.summary || "No summary available.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text, source: "briefing", timestamp: new Date() },
      ]);

      // In voice mode, also read it aloud
      if (mode === "voice" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.onstart = () => setSpeaking(true);
        utterance.onend = () => setSpeaking(false);
        utterance.onerror = () => setSpeaking(false);
        window.speechSynthesis.speak(utterance);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Failed to generate briefing.", timestamp: new Date() },
      ]);
    } finally {
      setBriefLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-3xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-1 flex items-center gap-2">
          <MessageSquare className="h-7 w-7 text-primary" />
          AI Business Assistant
        </h1>
        <p className="text-muted-foreground">
          Ask questions about your business. Switch between text and voice mode.
        </p>
      </div>

      {/* Mode toggle + quick actions */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        {/* Mode toggle */}
        <div className="inline-flex rounded-lg border p-0.5 bg-muted/50">
          <button
            onClick={() => handleModeSwitch("text")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors ${
              mode === "text"
                ? "bg-background shadow-sm font-medium"
                : "text-muted-foreground hover:text-foreground"
            }`}
            aria-label="Switch to text mode"
          >
            <Type className="h-3.5 w-3.5" />
            Text
          </button>
          <button
            onClick={() => handleModeSwitch("voice")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors ${
              mode === "voice"
                ? "bg-background shadow-sm font-medium"
                : "text-muted-foreground hover:text-foreground"
            }`}
            aria-label="Switch to voice mode"
          >
            <Mic className="h-3.5 w-3.5" />
            Voice
          </button>
        </div>

        {/* Quick actions */}
        <div className="flex gap-2 flex-1">
          <Button
            variant="outline"
            size="sm"
            onClick={generateBrief}
            disabled={briefLoading}
            className="gap-1.5"
          >
            {briefLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <FileText className="h-3.5 w-3.5" />
            )}
            {briefLoading ? "Generating…" : "Business Briefing"}
          </Button>
          {speaking && (
            <Button variant="outline" size="sm" onClick={stopSpeaking} className="gap-1.5">
              <VolumeX className="h-3.5 w-3.5" />
              Stop Speaking
            </Button>
          )}
        </div>
      </div>

      {/* Chat area */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            Conversation
            <Badge variant="outline" className="text-[10px] ml-auto">
              {mode === "voice" ? "Voice Mode" : "Text Mode"}
            </Badge>
          </CardTitle>
          <CardDescription>
            {mode === "text"
              ? "Type your questions below — answers appear as text"
              : "Tap the mic to speak — answers are read aloud"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="min-h-[300px] max-h-[450px] overflow-y-auto space-y-4 pr-1">
            {messages.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Bot className="h-10 w-10 mx-auto mb-3 opacity-40" />
                <p className="text-sm font-medium">No messages yet</p>
                <p className="text-xs mt-1">
                  {mode === "text"
                    ? "Type a question below or tap a suggestion."
                    : "Tap the microphone to ask a question."}
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] opacity-60">
                      {msg.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    {msg.source && (
                      <Badge
                        variant="outline"
                        className="text-[9px] px-1 py-0 h-4 opacity-60"
                      >
                        {msg.source === "ai"
                          ? "Nova AI"
                          : msg.source === "briefing"
                          ? "Briefing"
                          : "Quick"}
                      </Badge>
                    )}
                    {/* Per-message speak button in text mode */}
                    {msg.role === "assistant" && mode === "text" && "speechSynthesis" in window && (
                      <button
                        onClick={() => {
                          window.speechSynthesis.cancel();
                          const u = new SpeechSynthesisUtterance(msg.text);
                          u.rate = 1.0;
                          window.speechSynthesis.speak(u);
                        }}
                        className="opacity-40 hover:opacity-100 transition-opacity"
                        aria-label="Read aloud"
                        title="Read aloud"
                      >
                        <Volume2 className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                </div>
                {msg.role === "user" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted rounded-lg px-4 py-3">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </CardContent>
      </Card>

      {/* Suggestions (shown when conversation is short) */}
      {messages.length < 2 && (
        <div className="mb-4">
          <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
            <Lightbulb className="h-3 w-3" /> Try asking:
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                disabled={loading}
                className="text-xs rounded-full border px-3 py-1.5 hover:bg-muted transition-colors disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="flex gap-2 items-center">
        {/* Mic button — shown in voice mode when browser supports it */}
        {mode === "voice" && micSupported && (
          <Button
            variant={listening ? "destructive" : "outline"}
            size="icon"
            onClick={toggleMic}
            aria-label={listening ? "Stop listening" : "Start voice input"}
            className="shrink-0"
          >
            {listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
        )}
        <div className="relative flex-1">
          <input
            className="w-full rounded-lg border bg-background px-4 py-2.5 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder={
              mode === "voice" && listening
                ? "Listening… speak now"
                : "Ask about your business…"
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading || listening}
            aria-label="Question input"
          />
          <Button
            size="icon"
            variant="ghost"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Listening indicator */}
      {listening && (
        <p className="text-xs text-center text-red-500 mt-2 animate-pulse">
          Listening… speak now
        </p>
      )}

      {/* Mode hint */}
      <p className="text-xs text-center text-muted-foreground mt-3">
        {mode === "text"
          ? "Text mode — responses are text only. Click the speaker icon on any message to hear it."
          : "Voice mode — tap the mic to speak. Answers are read aloud automatically."}
      </p>
    </div>
  );
}
