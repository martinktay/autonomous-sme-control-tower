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
  FileText,
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  MessageSquare,
  Lightbulb,
} from "lucide-react";
import {
  getVoiceSummary,
  getVoiceBrief,
  askVoiceQuestion,
} from "@/lib/api";
import { useOrg } from "@/lib/org-context";

interface Message {
  role: "user" | "assistant";
  text: string;
  source?: string;
  timestamp: Date;
}

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [briefLoading, setBriefLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [micSupported, setMicSupported] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
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
      };
      recognition.onerror = () => setListening(false);
      recognition.onend = () => setListening(false);
      recognitionRef.current = recognition;
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

  const sendMessage = useCallback(async (text?: string) => {
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
      
      // Speak the answer using browser TTS
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(answer);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again.", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, orgId]);

  const generateBrief = async () => {
    setBriefLoading(true);
    try {
      const data = await getVoiceSummary(orgId);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.summary || "No summary available.", source: "briefing", timestamp: new Date() },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Failed to generate briefing.", timestamp: new Date() },
      ]);
    } finally {
      setBriefLoading(false);
    }
  };

  const playAudio = async () => {
    setPlaying(true);
    try {
      const data = await getVoiceBrief(orgId);
      const text = data.briefing || "No briefing available.";
      
      // Add briefing to chat
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text, source: "briefing", timestamp: new Date() },
      ]);
      
      // Use browser SpeechSynthesis for TTS
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.onend = () => setPlaying(false);
        utterance.onerror = () => setPlaying(false);
        window.speechSynthesis.speak(utterance);
      } else {
        setPlaying(false);
      }
    } catch {
      setPlaying(false);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Failed to generate audio briefing.", timestamp: new Date() },
      ]);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-3xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-1 flex items-center gap-2">
          <MessageSquare className="h-7 w-7 text-primary" />
          Voice Assistant
        </h1>
        <p className="text-muted-foreground">
          Ask questions about your business using voice or text. Get instant AI-powered answers based on your real data.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Button variant="outline" onClick={generateBrief} disabled={briefLoading} className="gap-2">
          {briefLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
          {briefLoading ? "Generating..." : "Get Business Briefing"}
        </Button>
        <Button variant="outline" onClick={playAudio} disabled={playing} className="gap-2">
          {playing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Volume2 className="h-4 w-4" />}
          {playing ? "Playing..." : "Play Audio Briefing"}
        </Button>
      </div>

      {/* Chat Area */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            Conversation
          </CardTitle>
          <CardDescription>Your questions and AI answers appear here</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="min-h-[300px] max-h-[450px] overflow-y-auto space-y-4 pr-1">
            {messages.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <Bot className="h-10 w-10 mx-auto mb-3 opacity-40" />
                <p className="text-sm font-medium">No messages yet</p>
                <p className="text-xs mt-1">
                  Ask a question below or tap a suggestion to get started.
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] opacity-60">
                      {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                    {msg.source && (
                      <Badge variant="outline" className="text-[9px] px-1 py-0 h-4 opacity-60">
                        {msg.source === "ai" ? "Nova AI" : msg.source === "briefing" ? "Briefing" : "Quick"}
                      </Badge>
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

      {/* Suggestions */}
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

      {/* Input Area */}
      <div className="flex gap-2 items-center">
        {micSupported && (
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
            placeholder={listening ? "Listening..." : "Ask about your business..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading || listening}
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
      {listening && (
        <p className="text-xs text-center text-red-500 mt-2 animate-pulse">
          Listening... speak now
        </p>
      )}
    </div>
  );
}
