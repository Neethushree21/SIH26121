import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Search,
  RotateCcw,
  FileText,
  HelpCircle,
  Loader2,
  X,
  ExternalLink
} from "lucide-react";
import { queryRAGChat } from "../../utils/api";
import CitationCard from "./CitationCard";

export default function RAGChat({ selectedWell, onClearWellFilter }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Welcome to the NWIS Knowledge Assistant. Ask technical drilling questions across historical Oil India Daily Drilling Reports (DDRs) and Well Completion Reports (WCRs).",
      citations: []
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const sampleQuestions = [
    "What caused mud loss in Nahorkatiya Tipam Sandstone?",
    "How was the gas kick killed in Baghjan-03?",
    "What mud weight is recommended for Barail Coal?",
    "What pipe-freeing recipe worked for differential sticking?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText = null) => {
    const q = questionText || input;
    if (!q.trim() || loading) return;

    const userMessage = { role: "user", text: q };
    setMessages((prev) => [...prev, userMessage]);
    if (!questionText) setInput("");
    setLoading(true);

    try {
      const wellFilter = selectedWell ? selectedWell.name : null;
      const res = await queryRAGChat(q, wellFilter);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.answer,
          citations: res.citations || [],
          followups: res.suggested_followups || []
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Unable to retrieve technical records from ChromaDB. Please verify the vector store service is running.",
          citations: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([
      {
        role: "assistant",
        text: "Conversation reset. You can ask queries about Assam Basin drilling events, casing designs, or mud weights.",
        citations: []
      }
    ]);
  };

  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-xl shadow-xl flex flex-col h-full overflow-hidden">
      
      {/* Pinned Chat Header */}
      <div className="bg-slate-950 px-3.5 py-2.5 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-slate-100 uppercase tracking-wider flex items-center gap-1.5">
              <span>WCR / DDR RAG Assistant</span>
            </h2>
            <p className="text-[10px] text-slate-400 font-mono">
              ChromaDB Semantic Vector Index
            </p>
          </div>
        </div>

        {/* Clear chat button */}
        <button
          onClick={handleClearHistory}
          title="Reset chat conversation"
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Focus Well Context Badge if active */}
      {selectedWell && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-3 py-1.5 flex items-center justify-between text-[11px] text-amber-300">
          <div className="flex items-center space-x-1.5 truncate">
            <span className="font-semibold">Context Filter:</span>
            <span className="font-mono text-white font-bold truncate">{selectedWell.name}</span>
          </div>
          {onClearWellFilter && (
            <button
              onClick={onClearWellFilter}
              className="text-amber-400 hover:text-white p-0.5"
              title="Clear well focus"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Suggested Technical Prompts */}
      <div className="bg-slate-950/50 px-2.5 py-1.5 border-b border-slate-800/80 flex items-center space-x-1.5 overflow-x-auto text-[10px] shrink-0">
        <span className="text-slate-500 font-semibold uppercase whitespace-nowrap pl-1">
          Prompts:
        </span>
        {sampleQuestions.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            className="whitespace-nowrap px-2 py-0.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition text-[10px]"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Scrollable Message History Box (Internal Vertical Scrolling Only) */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3.5 min-h-[350px]">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${
              msg.role === "user" ? "items-end" : "items-start"
            }`}
          >
            {/* Sender identity */}
            <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 mb-1 px-1">
              {msg.role === "user" ? (
                <>
                  <span className="font-semibold text-amber-400">Drilling Engineer</span>
                  <User className="w-3 h-3 text-amber-400" />
                </>
              ) : (
                <>
                  <Bot className="w-3 h-3 text-sky-400" />
                  <span className="font-semibold text-sky-400">NWIS Intelligence Core</span>
                </>
              )}
            </div>

            {/* Bubble */}
            <div
              className={`rounded-xl px-3.5 py-2.5 max-w-[95%] text-xs leading-relaxed ${
                msg.role === "user"
                  ? "bg-amber-500/15 border border-amber-500/30 text-amber-100 rounded-tr-none"
                  : "bg-slate-950/80 border border-slate-800 text-slate-200 rounded-tl-none shadow-sm"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>

              {/* Citations Preview Cards if present */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-800/80 space-y-2">
                  <div className="text-[10px] font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    <span>Report Citations ({msg.citations.length})</span>
                  </div>
                  <div className="space-y-1.5">
                    {msg.citations.map((c, cIdx) => (
                      <CitationCard key={cIdx} citation={c} index={cIdx} />
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Followups */}
              {msg.followups && msg.followups.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-800/80 flex flex-wrap gap-1.5">
                  {msg.followups.map((f, fIdx) => (
                    <button
                      key={fIdx}
                      onClick={() => handleSend(f)}
                      className="text-[10px] px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 text-sky-400 border border-slate-700 transition"
                    >
                      → {f}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-sky-400 p-2 bg-slate-950/60 rounded-lg border border-slate-800 w-fit">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
            <span className="font-mono text-[11px]">Searching ChromaDB vector store & synthesizing response...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Pinned Input Form Bar at Bottom */}
      <div className="p-2.5 bg-slate-950 border-t border-slate-800 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            placeholder="Ask about offset well logs, kicks, losses..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/80 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-40 disabled:hover:bg-amber-500 text-black font-bold text-xs flex items-center space-x-1.5 transition shadow-sm"
          >
            <span>Send</span>
            <Send className="w-3 h-3" />
          </button>
        </form>
        <div className="mt-1 flex items-center justify-between text-[10px] text-slate-500 font-mono px-1">
          <span>Targeting Assam Basin DDRs / WCRs</span>
          <span>Press Enter ↵</span>
        </div>
      </div>

    </div>
  );
}
