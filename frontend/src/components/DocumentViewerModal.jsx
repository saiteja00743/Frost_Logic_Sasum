import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Search, FileText, CheckCircle2 } from 'lucide-react';

export default function DocumentViewerModal({
  isOpen,
  onClose,
  documentData,
  highlightQuote = null,
  targetPage = 1,
}) {
  const [currentPage, setCurrentPage] = useState(targetPage || 1);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (targetPage && targetPage > 0) {
      setCurrentPage(targetPage);
    }
  }, [targetPage]);

  if (!isOpen || !documentData) return null;

  const pages = documentData.pages || [];
  const totalPages = pages.length;
  const activePageObj = pages.find((p) => p.page_number === currentPage) || pages[0] || { text: '' };

  // Highlight helper
  const renderHighlightedContent = (rawText) => {
    if (!rawText) return <p className="text-slate-500 italic">No text extracted on this page.</p>;

    const quoteToHighlight = highlightQuote ? highlightQuote.trim() : '';

    if (!quoteToHighlight && !searchTerm) {
      return (
        <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
          {rawText}
        </pre>
      );
    }

    const term = (searchTerm || quoteToHighlight).trim();
    if (!term) {
      return (
        <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
          {rawText}
        </pre>
      );
    }

    // Try progressively shorter slices of the quote if the full string has punctuation mismatch
    const candidateTerms = [term];
    if (term.length > 40) {
      // Add first 30 chars and first 5 words as candidate
      const words = term.split(/\s+/);
      if (words.length >= 4) {
        candidateTerms.push(words.slice(0, 5).join(' '));
      }
    }

    let matchTerm = null;
    for (const cand of candidateTerms) {
      if (rawText.toLowerCase().includes(cand.toLowerCase())) {
        matchTerm = cand;
        break;
      }
    }

    if (!matchTerm) {
      return (
        <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
          {rawText}
        </pre>
      );
    }

    try {
      const escaped = matchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`(${escaped})`, 'gi');
      const parts = rawText.split(regex);

      return (
        <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
          {parts.map((part, i) =>
            regex.test(part) ? (
              <mark
                key={i}
                className="bg-teal-400/40 text-teal-100 border-b-2 border-teal-400 font-semibold px-1 py-0.5 rounded shadow-sm"
              >
                {part}
              </mark>
            ) : (
              part
            )
          )}
        </pre>
      );
    } catch {
      return (
        <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
          {rawText}
        </pre>
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full max-w-4xl h-[88vh] rounded-2xl glass-panel border border-slate-700/80 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-slate-800 bg-slate-900/80">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <div className="p-1.5 sm:p-2 rounded-lg bg-teal-500/10 text-teal-400 shrink-0">
                <FileText className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <div className="min-w-0">
                <h3 className="text-xs sm:text-sm font-bold text-white truncate">
                  {documentData.filename || 'Extracted Document Text'}
                </h3>
                <p className="text-[10px] sm:text-xs text-slate-400">
                  Page {currentPage} of {totalPages}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
              {/* Page navigation controls */}
              <div className="flex items-center bg-slate-800/80 rounded-lg p-1 border border-slate-700">
                <button
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Previous Page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs font-semibold px-2 text-slate-200">
                  {currentPage} / {totalPages}
                </span>
                <button
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  className="p-1 rounded text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Next Page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition"
                title="Close Viewer"
              >
                <X className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Highlight Alert Banner if an active quote was clicked */}
        {highlightQuote && (
          <div className="px-6 py-2.5 bg-teal-500/10 border-b border-teal-500/20 flex items-center justify-between text-xs text-teal-300">
            <div className="flex items-center gap-2 truncate">
              <CheckCircle2 className="w-4 h-4 text-teal-400 shrink-0" />
              <span className="truncate">
                Highlighting quotation from Page {targetPage}: <span className="italic font-mono">"{highlightQuote}"</span>
              </span>
            </div>
            <button
              onClick={() => setSearchTerm('')}
              className="text-slate-400 hover:text-white text-[11px] underline ml-2 shrink-0"
            >
              Clear
            </button>
          </div>
        )}

        {/* Page Content Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-950/70 select-text">
          <div className="max-w-3xl mx-auto rounded-xl p-4 sm:p-6 lg:p-8 bg-slate-900/40 border border-slate-800/80 shadow-inner">
            <div className="text-[11px] font-mono text-slate-400 pb-4 mb-4 border-b border-slate-800 flex items-center justify-between">
              <span>PAGE {currentPage} OF {totalPages}</span>
              <span>{activePageObj.word_count || 0} WORDS</span>
            </div>
            {renderHighlightedContent(activePageObj.text)}
          </div>
        </div>

        {/* Footer Page Selector Bar */}
        <div className="px-4 sm:px-6 py-3 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between text-xs text-slate-400 gap-3">
          <div className="flex items-center gap-1.5 overflow-x-auto flex-1 pb-0.5">
            <span className="shrink-0">Jump:</span>
            {pages.map((p) => (
              <button
                key={p.page_number}
                onClick={() => setCurrentPage(p.page_number)}
                className={`px-2 py-0.5 rounded text-xs font-semibold shrink-0 ${
                  currentPage === p.page_number
                    ? 'bg-teal-500 text-slate-950'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                P{p.page_number}
              </button>
            ))}
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700 text-xs font-medium shrink-0"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
