import React, { useState } from "react";
import { Send, Bot, User, Sparkles, BookOpen, ChevronDown, ChevronUp, Search, RefreshCw } from "lucide-react";
import { queryRAGChat } from "../../utils/api";

export default function RAGChat({ selectedWell }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Welcome to the NWIS Knowledge Assistant. Ask technical drilling questions across historical Oil India Daily Drilling Reports (DDRs) and Well Completion Reports (WCRs).",
      citations: []
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState({});

  const sampleQuestions = [
    "What caused the severe mud losses in Nahorkatiya Tipam Sandstone?",
    "How was the high pressure gas kick killed in Baghjan-03?",
    "What mud weight is recommended for Barail Coal-Shale?",
    "What pipe-freeing recipe worked for differential sticking in Moran?"
  ];

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
          text: "Error retrieving knowledge records. Please ensure backend is running.",
          citations: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleCitation = (msgIndex, citIndex) => {
    const key = `${msgIndex}-${citIndex}`;
    setExpandedCitations((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-oil-border rounded-xl shadow-xl overflow-hidden">
      
      {/* Chat Header */}
      <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <span>WCR / DDR Knowledge Assistant</span>
            </h3>
            <p className="text-[11px] text-slate-400">
              RAG Vector Search over Historical Oil India Reports
            </p>
          </div>
        </div>
        {selectedWell && (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Focus: {selectedWell.name}
          </span>
        )}
      </div>

      {/* Suggested Prompts Bar */}
      <div className="bg-slate-950/40 px-3 py-2 border-b border-slate-800/80 flex items-center space-x-1.5 overflow-x-auto text-[11px]">
        <span className="text-slate-500 font-semibold uppercase text-[10px] whitespace-nowrap pl-1">Suggested:</span>
        {sampleQuestions.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            className="whitespace-nowrap px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition text-[11px]"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
          >
            <div className="flex items-start space-x-2 max-w-[92%]">
              {m.role === "assistant" && (
                <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center flex-shrink-0 mt-0.5 border border-sky-500/30">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`p-3 rounded-xl text-xs leading-relaxed ${
                  m.role === "user"
                    ? "bg-amber-500 text-black font-medium rounded-tr-none shadow-md shadow-amber-500/10"
                    : "bg-slate-800/90 text-slate-200 border border-slate-700/80 rounded-tl-none shadow-md"
                }`}
              >
                <div className="whitespace-pre-line">{m.text}</div>

                {/* Citations block for Assistant responses */}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-700/80 space-y-1.5">
                    <div className="flex items-center space-x-1 text-[11px] font-bold text-sky-400">
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>Referenced Documents & Technical Citations ({m.citations.length}):</span>
                    </div>

                    <div className="space-y-1.5">
                      {m.citations.map((c, cIdx) => {
                        const key = `${idx}-${cIdx}`;
                        const isExpanded = !!expandedCitations[key];
                        return (
                          <div
                            key={cIdx}
                            className="bg-slate-900/90 border border-slate-700/60 rounded-lg p-2 text-[11px]"
                          >
                            <div
                              onClick={() => toggleCitation(idx, cIdx)}
                              className="flex items-center justify-between cursor-pointer text-slate-300 hover:text-white"
                            >
                              <div className="flex items-center space-x-1.5 font-semibold">
                                <span className="text-amber-400">{c.document_name}</span>
                                <span className="text-slate-500">•</span>
                                <span className="text-slate-400">{c.well_name}</span>
                              </div>
                              <div className="flex items-center space-x-1 text-[10px] text-slate-400">
                                <span className="px-1.5 py-0.2 rounded bg-slate-800 text-emerald-400 font-mono">
                                  {Math.round(c.score * 100)}% match
                                </span>
                                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                              </div>
                            </div>

                            {isExpanded && (
                              <div className="mt-2 pt-2 border-t border-slate-800 text-slate-400 space-y-1">
                                <div className="text-[10px] text-slate-500 font-mono">
                                  Formation: {c.formation} | Interval: {c.depth_interval}
                                </div>
                                <blockquote className="pl-2 border-l-2 border-amber-500/50 text-slate-300 italic text-[11px] bg-slate-950/50 p-1.5 rounded-r">
                                  "{c.snippet}"
                                </blockquote>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
              {m.role === "user" && (
                <div className="w-7 h-7 rounded-lg bg-amber-500 text-black flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 animate-pulse">
            <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
            <span>Searching vector database across DDRs & WCRs...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3 bg-slate-950 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about offset kicks, mud weight, loss zones, or lithology..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-black font-bold p-2.5 rounded-xl transition duration-150 shadow-md shadow-amber-500/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
}
