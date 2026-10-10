import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, ArrowRight, Sparkles, ShieldCheck, Clock, FileCheck } from 'lucide-react';

export default function HeroUpload({
  onFileUpload,
  onSelectSample,
  isLoading,
  loadingMessage,
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please upload a valid PDF document.');
      return;
    }
    setSelectedFile(file);
    onFileUpload(file);
  };

  const sampleAgreements = [
    {
      key: 'saas_msa',
      title: 'CloudScale Enterprise SaaS MSA',
      badge: 'High Risk • 4 Pages',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      description: 'Features aggressive 60-day auto-renewal, unilateral customer indemnity, and uncapped liability exposures.',
    },
    {
      key: 'commercial_lease',
      title: 'MetroTower Commercial Office Lease',
      badge: 'Medium Risk • 3 Pages',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
      description: 'Contains security deposit forfeiture on 5-day default, tenant HVAC maintenance, and commercial liability covenants.',
    },
    {
      key: 'mutual_nda',
      title: 'Apex Innovations Mutual NDA',
      badge: 'Standard Risk • 2 Pages',
      badgeColor: 'text-teal-400 bg-teal-500/10 border-teal-500/20',
      description: 'Mutual non-disclosure with 5-year survival term, 14-day data return mandate, and 12-month non-solicitation.',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
      {/* Hero Headline */}
      <div className="text-center max-w-3xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs font-semibold mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Evidence-Linked Contract Risk Auditing</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight sm:leading-tight mb-4">
          Understand Every Clause.{' '}
          <span className="bg-gradient-to-r from-teal-400 via-sky-400 to-indigo-400 bg-clip-text text-transparent">
            Spot Risks Before They Cost You.
          </span>
        </h1>
        <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
          Analyze business agreements, identify potential risks, track obligations, and generate evidence-backed reports with page-level verification.
        </p>
      </div>

      {/* Main Upload Box */}
      <div className="max-w-2xl mx-auto mb-12">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !isLoading && fileInputRef.current?.click()}
          className={`relative rounded-2xl border-2 border-dashed p-6 sm:p-10 lg:p-12 text-center transition cursor-pointer ${
            isDragOver
              ? 'border-teal-400 bg-teal-500/10 shadow-xl shadow-teal-500/10'
              : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/90'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleFileChange}
            disabled={isLoading}
          />

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-4">
              <div className="w-14 h-14 rounded-full border-4 border-teal-500/20 border-t-teal-400 animate-spin mb-4" />
              <h3 className="text-lg font-semibold text-white mb-1">
                {loadingMessage || 'Processing Contract...'}
              </h3>
              <p className="text-xs text-slate-400 max-w-sm">
                Extracting text page-by-page, identifying high-risk clauses, and verifying quotations against source text.
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center">
              <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 mb-4 shadow-lg shadow-teal-500/5">
                <UploadCloud className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Drop your contract PDF here, or <span className="text-teal-400 underline underline-offset-4">browse files</span>
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Supports standard text-based PDF contracts up to 25MB (MSA, NDA, Leases, Vendor Agreements)
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Zero Hallucination Mode: Every quote verified against source pages</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick-Launch Pre-Analyzed Sample Agreements */}
      <div className="mb-14">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <h2 className="text-base sm:text-lg font-bold text-white">
              Try Prepared Sample Agreements (1-Click Demo)
            </h2>
          </div>
          <span className="text-xs text-slate-400 hidden sm:block">Pre-configured for instant audit</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {sampleAgreements.map((sample) => (
            <div
              key={sample.key}
              onClick={() => !isLoading && onSelectSample(sample.key)}
              className="group glass-card rounded-xl p-5 border border-slate-800 hover:border-teal-500/40 hover:bg-slate-900/90 transition cursor-pointer relative overflow-hidden"
            >
              <div className="flex items-start justify-between mb-3">
                <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${sample.badgeColor}`}>
                  {sample.badge}
                </span>
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-teal-400 group-hover:translate-x-1 transition" />
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-teal-300 transition mb-2">
                {sample.title}
              </h3>
              <p className="text-xs text-slate-400 line-clamp-3 mb-4 leading-relaxed">
                {sample.description}
              </p>
              <div className="flex items-center gap-1.5 text-xs font-medium text-teal-400">
                <span>Run Instant Audit</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Product Pillars / Differentiators */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-6 border-t border-slate-800/80">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 mt-1">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white mb-1">Evidence-Linked Verification</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every identified risk and obligation is quoted verbatim and matched directly against document page text.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 mt-1">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white mb-1">Obligations & Deadlines</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Extracts responsible parties, renewal notice windows, payment terms, and flags unverified dates honestly.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 mt-1">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white mb-1">Downloadable PDF Reports</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Export an executive-ready ReportLab PDF complete with findings, risk matrices, and source citations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
