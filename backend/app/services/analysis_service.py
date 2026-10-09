import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
import httpx
from pydantic import ValidationError

from ..schemas.models import AnalysisResult, Risk, Party, Obligation, Deadline, KeyClause, Evidence
from .verification_service import VerificationService

SYSTEM_PROMPT = """You are ClauseGuard AI, an expert document and contract-analysis assistant.
Analyze ONLY the supplied contract/document text.

Your job is to identify:
1. A concise document summary.
2. Contracting parties and their roles.
3. Detected contract type (e.g. Master Services Agreement, NDA, Commercial Lease, Employment, Vendor).
4. Overall contract risk score (0 to 100, where 0 is completely standard/safe, and 100 is extremely one-sided or hazardous).
5. Potential risks that warrant review (categorized by severity: high, medium, low).
6. Specific obligations and the responsible parties.
7. Explicit calendar dates and operational deadlines.
8. Key clauses (Termination, Indemnification, Liability, Payment, Confidentiality, Governing Law, IP).

CRITICAL RULES:
- Never fabricate clauses, quotations, dates, parties, or page numbers.
- For every risk, obligation, deadline, and key clause, you MUST provide an exact, verbatim quotation from the text in `evidence.quote`.
- Specify the 1-indexed `evidence.page` where the text was found.
- If a deadline cannot be determined from explicit text, state 'Needs verification'.
- This analysis supports human legal review and is not definitive legal advice.

Respond ONLY with a valid JSON object matching this schema:
{
  "document_summary": "string",
  "contract_type": "string",
  "risk_score": 65,
  "parties": [
    {"name": "string", "role": "string", "obligations_count": 0}
  ],
  "risks": [
    {
      "id": "risk-1",
      "title": "string",
      "severity": "high" | "medium" | "low",
      "category": "Liability" | "Termination" | "Payment" | "Compliance" | "IP" | "General",
      "explanation": "string",
      "evidence": {
        "page": 1,
        "quote": "verbatim text snippet"
      },
      "recommended_action": "string",
      "verification_status": "needs_review"
    }
  ],
  "obligations": [
    {
      "id": "ob-1",
      "responsible_party": "string",
      "obligation": "string",
      "evidence": {
        "page": 1,
        "quote": "verbatim text snippet"
      },
      "deadline": "string or Needs verification",
      "is_conditional": false,
      "verification_status": "needs_review"
    }
  ],
  "deadlines": [
    {
      "id": "dl-1",
      "title": "string",
      "date_or_trigger": "string",
      "responsible_party": "string",
      "evidence": {
        "page": 1,
        "quote": "verbatim text snippet"
      },
      "is_explicit_date": true,
      "verification_status": "needs_review"
    }
  ],
  "key_clauses": [
    {
      "id": "kc-1",
      "title": "string",
      "category": "Termination" | "Indemnification" | "Liability" | "Payment" | "Confidentiality" | "Governing Law",
      "summary": "string",
      "evidence": {
        "page": 1,
        "quote": "verbatim text snippet"
      },
      "impact": "string"
    }
  ]
}
"""

class AnalysisService:
    @classmethod
    async def analyze_document(
        cls,
        doc_id: str,
        filename: str,
        pages_data: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        provider: Optional[str] = "auto",
        custom_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes document pages using either configured LLM or Intelligent Heuristic Engine,
        then verifies all quotations against extracted text.
        """
        # Determine if an API key is available
        resolved_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        analysis_dict = None
        engine_label = "Intelligent Legal Analysis Engine (Local Heuristic)"

        if resolved_key and len(resolved_key.strip()) > 5:
            try:
                analysis_dict, engine_label = await cls._analyze_with_llm(
                    pages_data=pages_data,
                    api_key=resolved_key,
                    provider=provider or "auto",
                    custom_model=custom_model
                )
            except Exception as e:
                print(f"[AnalysisService] LLM call failed: {e}. Falling back to Heuristic Engine.")
                analysis_dict = None

        if not analysis_dict:
            analysis_dict = cls._analyze_heuristic(filename, pages_data)
            engine_label = "ClauseGuard Intelligent Legal Engine (Rule & Heuristic)"

        # Set document-level attributes
        analysis_dict["document_id"] = doc_id
        analysis_dict["document_name"] = filename
        analysis_dict["total_pages"] = len(pages_data)
        analysis_dict["word_count"] = sum(p.get("word_count", 0) for p in pages_data)
        analysis_dict["engine_used"] = engine_label

        # Run Evidence Verification Service
        analysis_dict = VerificationService.verify_analysis_findings(analysis_dict, pages_data)

        return analysis_dict

    @classmethod
    async def _analyze_with_llm(
        cls,
        pages_data: List[Dict[str, Any]],
        api_key: str,
        provider: str,
        custom_model: Optional[str]
    ) -> Tuple[Dict[str, Any], str]:
        """Call external LLM API (OpenRouter or OpenAI) with page-tagged content."""
        # Construct document text with page markers
        formatted_pages = []
        for p in pages_data[:20]:  # limit to first 20 pages to protect context limits
            formatted_pages.append(f"--- PAGE {p['page_number']} ---\n{p['text']}\n")
        full_content = "\n".join(formatted_pages)

        # Decide endpoint and model
        if provider == "openai" or api_key.startswith("sk-") and not api_key.startswith("sk-or-"):
            url = "https://api.openai.com/v1/chat/completions"
            model = custom_model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            engine_name = f"OpenAI ({model})"
        else:
            # Default to OpenRouter
            url = "https://openrouter.ai/api/v1/chat/completions"
            model = custom_model or os.getenv("LLM_MODEL") or "google/gemini-2.0-flash-001"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://clauseguard.ai",
                "X-Title": "ClauseGuard AI"
            }
            engine_name = f"OpenRouter ({model})"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this contract thoroughly:\n\n{full_content}"}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            # Parse json
            parsed = json.loads(raw_content)
            return parsed, engine_name

    @classmethod
    def _analyze_heuristic(cls, filename: str, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Deterministic, robust legal analysis engine.
        Parses parties, risks, key clauses, obligations, and deadlines with real quotes and page numbers.
        """
        combined_text = "\n".join([p["text"] for p in pages_data])
        
        # 1. Detect Contract Type
        contract_type = "Commercial Agreement"
        title_lower = (filename + " " + combined_text[:1000]).lower()
        if "master services" in title_lower or "msa" in title_lower or "services agreement" in title_lower:
            contract_type = "Master Services Agreement (MSA)"
        elif "non-disclosure" in title_lower or "nda" in title_lower or "confidentiality agreement" in title_lower:
            contract_type = "Non-Disclosure Agreement (NDA)"
        elif "lease" in title_lower or "tenancy" in title_lower or "landlord" in title_lower:
            contract_type = "Commercial Lease Agreement"
        elif "employment" in title_lower or "employee" in title_lower:
            contract_type = "Employment Agreement"
        elif "license" in title_lower or "software license" in title_lower:
            contract_type = "Software License Agreement"
        elif "vendor" in title_lower or "supplier" in title_lower:
            contract_type = "Vendor & Supply Agreement"

        # 2. Extract Parties
        parties = []
        party_patterns = [
            r'between\s+([A-Z][A-Za-z0-9\s,\.\(\)]+?)(?:,\s*(?:a|an)\s+[^\n]+?)?\s+and\s+([A-Z][A-Za-z0-9\s,\.\(\)]+?)(?:,\s*(?:a|an)\s+[^\n]+?)?\s*(?:\.|\n|\()',
            r'by and between\s+([^\n,]+)(?:.*?)\s+and\s+([^\n,]+)',
        ]
        found_parties = []
        for pat in party_patterns:
            m = re.search(pat, combined_text, re.IGNORECASE)
            if m:
                p1 = m.group(1).strip().strip('"').strip("'")
                p2 = m.group(2).strip().strip('"').strip("'")
                if len(p1) < 60 and len(p2) < 60:
                    found_parties = [p1, p2]
                    break

        if found_parties:
            parties.append({"name": found_parties[0], "role": "Primary Party / Discloser / Provider", "obligations_count": 0})
            parties.append({"name": found_parties[1], "role": "Counterparty / Recipient / Client", "obligations_count": 0})
        else:
            # Fallback party detection
            if "lease" in contract_type.lower():
                parties = [
                    {"name": "Landlord / Lessor", "role": "Property Owner", "obligations_count": 0},
                    {"name": "Tenant / Lessee", "role": "Commercial Occupant", "obligations_count": 0}
                ]
            elif "nda" in contract_type.lower():
                parties = [
                    {"name": "Disclosing Party", "role": "Owner of Confidential Information", "obligations_count": 0},
                    {"name": "Receiving Party", "role": "Recipient bound by confidentiality", "obligations_count": 0}
                ]
            else:
                parties = [
                    {"name": "Service Provider / Licensor", "role": "Solution Provider", "obligations_count": 0},
                    {"name": "Customer / Client", "role": "Commercial Customer", "obligations_count": 0}
                ]

        # 3. Scan for Clauses, Risks, Obligations, Deadlines across pages
        risks = []
        obligations = []
        deadlines = []
        key_clauses = []

        # Helper to find quote snippet in page
        def find_snippet_in_pages(regex_pattern: str, max_matches: int = 1):
            matches = []
            for page in pages_data:
                p_num = page["page_number"]
                p_text = page["text"]
                for match in re.finditer(regex_pattern, p_text, re.IGNORECASE):
                    start = max(0, match.start() - 15)
                    end = min(len(p_text), match.end() + 150)
                    # Expand to sentence boundaries
                    snippet = p_text[start:end].replace("\n", " ").strip()
                    # Clean up
                    snippet = re.sub(r"\s+", " ", snippet)
                    matches.append((snippet, p_num))
                    if len(matches) >= max_matches:
                        return matches
            return matches

        # -- High Risk 1: Uncapped or Asymmetric Indemnification --
        indem_matches = find_snippet_in_pages(r"(indemnify|indemnification|hold harmless|defend,? indemnify)")
        if indem_matches:
            snip, pg = indem_matches[0]
            risks.append({
                "id": "risk-indemnity",
                "title": "Broad or Asymmetric Indemnification Obligation",
                "severity": "high",
                "category": "Liability & Indemnity",
                "explanation": "Clause imposes broad indemnity duty ('defend and hold harmless'), which could shift third-party liabilities, attorney fees, and uncapped financial exposures.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "recommended_action": "Negotiate mutual indemnification, cap exposure to aggregate contract value, and carve out gross negligence or willful misconduct.",
                "verification_status": "needs_review"
            })
            key_clauses.append({
                "id": "kc-indemnity",
                "title": "Indemnification",
                "category": "Indemnification",
                "summary": "Defines duty to defend, indemnify, and hold counterparties harmless from third-party claims.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "impact": "Shifts legal defense costs and liabilities."
            })

        # -- High/Med Risk 2: Uncapped Liability or Aggregate Cap Limitations --
        liab_matches = find_snippet_in_pages(r"(limitation of liability|in no event shall|aggregate liability|consequential damages)")
        if liab_matches:
            snip, pg = liab_matches[0]
            risks.append({
                "id": "risk-liability",
                "title": "Strict Limitation of Liability & Consequential Damages Waiver",
                "severity": "medium",
                "category": "Liability",
                "explanation": "Limits monetary recovery to fees paid in recent months or waives indirect and consequential damages.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "recommended_action": "Verify whether the liability cap covers critical breach scenarios (e.g., data breach, IP infringement, confidentiality violations).",
                "verification_status": "needs_review"
            })
            key_clauses.append({
                "id": "kc-liability",
                "title": "Limitation of Liability",
                "category": "Liability",
                "summary": "Caps total financial liability and excludes consequential or indirect damages.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "impact": "Restricts maximum financial recovery in event of material breach."
            })

        # -- High/Med Risk 3: Automatic Renewal / Short Non-Renewal Window --
        renew_matches = find_snippet_in_pages(r"(automatically renew|automatic renewal|prior written notice of at least|successive periods of)")
        if renew_matches:
            snip, pg = renew_matches[0]
            risks.append({
                "id": "risk-auto-renew",
                "title": "Auto-Renewal with Mandatory Advance Written Notice",
                "severity": "high",
                "category": "Termination",
                "explanation": "Agreement automatically extends for successive terms unless written opt-out notice is served prior to the deadline window. Missed deadlines cause lock-in.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "recommended_action": "Calendar renewal deadline at least 90 days in advance and request 30-day notice requirement instead of 60+ days.",
                "verification_status": "needs_review"
            })

        # -- Risk 4: Termination for Convenience or Immediate Default --
        term_matches = find_snippet_in_pages(r"(termination for cause|terminate this agreement|immediate termination|cure period of)")
        if term_matches:
            snip, pg = term_matches[0]
            risks.append({
                "id": "risk-termination",
                "title": "Termination Provisions and Default Cure Windows",
                "severity": "medium",
                "category": "Termination",
                "explanation": "Governs how and when either party can terminate, notice requirements, and cure windows for material default.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "recommended_action": "Ensure cure periods are at least 30 calendar days for remediable breaches.",
                "verification_status": "needs_review"
            })
            key_clauses.append({
                "id": "kc-term",
                "title": "Term and Termination",
                "category": "Termination",
                "summary": "Details agreement duration, renewal cycles, and unilateral or cause-based termination mechanisms.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "impact": "Determines contract lifecycle and exit flexibility."
            })

        # -- Risk 5: Penalties, Interest or Forfeiture --
        penalty_matches = find_snippet_in_pages(r"(late fee|interest rate of|forfeiture|penalty|liquidated damages)")
        if penalty_matches:
            snip, pg = penalty_matches[0]
            risks.append({
                "id": "risk-penalties",
                "title": "Financial Penalties or Late Payment Surcharges",
                "severity": "low",
                "category": "Payment",
                "explanation": "Specifies monetary charges or accrued interest on overdue balances or contractual delays.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "recommended_action": "Check whether late interest rates comply with local usury ceilings and request a 5-day grace period.",
                "verification_status": "needs_review"
            })

        # -- Key Clause: Confidentiality --
        conf_matches = find_snippet_in_pages(r"(confidential information|nondisclosure|proprietary information)")
        if conf_matches:
            snip, pg = conf_matches[0]
            key_clauses.append({
                "id": "kc-confidentiality",
                "title": "Confidentiality & Non-Disclosure",
                "category": "Confidentiality",
                "summary": "Requires strict non-disclosure and standard of care for proprietary business information.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "impact": "Protects trade secrets and proprietary data."
            })

        # -- Key Clause: Governing Law --
        gov_matches = find_snippet_in_pages(r"(governed by the laws of|jurisdiction of the courts of|venue shall lie)")
        if gov_matches:
            snip, pg = gov_matches[0]
            key_clauses.append({
                "id": "kc-governing-law",
                "title": "Governing Law and Jurisdiction",
                "category": "Governing Law",
                "summary": "Designates legal jurisdiction and prevailing court venues for dispute resolution.",
                "evidence": {"page": pg, "quote": snip[:180]},
                "impact": "Dictates legal jurisdiction and cost of litigation."
            })

        # 4. Extract Obligations (Sentences with shall / agrees to / must)
        ob_counter = 1
        for page in pages_data:
            p_num = page["page_number"]
            p_text = page["text"]
            sentences = re.split(r"(?<=[.!?])\s+", p_text)
            for s in sentences:
                s_clean = s.strip().replace("\n", " ")
                if len(s_clean) > 40 and len(s_clean) < 260:
                    if re.search(r"\b(shall|must|agrees to|is required to|undertakes to)\b", s_clean, re.IGNORECASE):
                        # Determine responsible party
                        resp_party = parties[0]["name"]
                        if re.search(r"\b(customer|client|tenant|receiving party|licensee)\b", s_clean, re.IGNORECASE):
                            resp_party = parties[1]["name"] if len(parties) > 1 else "Counterparty"

                        # Check for deadline hint
                        deadline_str = "Needs verification"
                        d_match = re.search(r"\b(within \d+ days?|net \d+|prior to [^\.,]+|\d+ business days?)\b", s_clean, re.IGNORECASE)
                        if d_match:
                            deadline_str = d_match.group(1)

                        obligations.append({
                            "id": f"ob-{ob_counter}",
                            "responsible_party": resp_party,
                            "obligation": s_clean[:140],
                            "evidence": {"page": p_num, "quote": s_clean},
                            "deadline": deadline_str,
                            "is_conditional": "if " in s_clean.lower() or "upon " in s_clean.lower(),
                            "verification_status": "needs_review"
                        })
                        ob_counter += 1
                        if len(obligations) >= 7:
                            break
            if len(obligations) >= 7:
                break

        # 5. Extract Explicit Deadlines & Calendar Dates
        dl_counter = 1
        date_patterns = [
            (r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b", True),
            (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", True),
            (r"\bwithin\s+(\d+)\s+(?:calendar\s+|business\s+)?days?\b", False),
            (r"\bat least\s+(\d+)\s+days?\s+prior\s+to\b", False),
            (r"\bNet\s+(\d+)\s+days?\b", False),
        ]
        seen_dates = set()
        for page in pages_data:
            p_num = page["page_number"]
            p_text = page["text"]
            for pat, is_explicit in date_patterns:
                for match in re.finditer(pat, p_text, re.IGNORECASE):
                    matched_date = match.group(0).strip()
                    if matched_date.lower() in seen_dates:
                        continue
                    seen_dates.add(matched_date.lower())

                    # Context snippet
                    start = max(0, match.start() - 30)
                    end = min(len(p_text), match.end() + 70)
                    ctx = p_text[start:end].replace("\n", " ").strip()
                    ctx = re.sub(r"\s+", " ", ctx)

                    title = f"Milestone / Notice Window: {matched_date}"
                    if "renew" in ctx.lower():
                        title = f"Renewal Notice Deadline ({matched_date})"
                    elif "payment" in ctx.lower() or "pay" in ctx.lower() or "invoice" in ctx.lower():
                        title = f"Payment Settlement Window ({matched_date})"
                    elif "cure" in ctx.lower() or "default" in ctx.lower():
                        title = f"Breach Cure Period ({matched_date})"

                    deadlines.append({
                        "id": f"dl-{dl_counter}",
                        "title": title,
                        "date_or_trigger": matched_date,
                        "responsible_party": parties[0]["name"] if dl_counter % 2 == 1 else (parties[1]["name"] if len(parties) > 1 else "All Parties"),
                        "evidence": {"page": p_num, "quote": ctx},
                        "is_explicit_date": is_explicit,
                        "verification_status": "needs_review"
                    })
                    dl_counter += 1
                    if len(deadlines) >= 6:
                        break
                if len(deadlines) >= 6:
                    break
            if len(deadlines) >= 6:
                break

        # Calculate Risk Score
        high_risks = len([r for r in risks if r["severity"] == "high"])
        med_risks = len([r for r in risks if r["severity"] == "medium"])
        low_risks = len([r for r in risks if r["severity"] == "low"])
        calculated_score = min(100, max(25, (high_risks * 25) + (med_risks * 12) + (low_risks * 5)))

        # Update party obligation counts
        for p in parties:
            p["obligations_count"] = len([o for o in obligations if p["name"] in o["responsible_party"]])

        # Summary text
        summary = (
            f"This {contract_type} establishes binding terms and conditions between {parties[0]['name']} and "
            f"{parties[1]['name'] if len(parties) > 1 else 'counterparties'}. "
            f"The agreement contains {len(risks)} notable risk factors, including key provisions on indemnification, "
            f"liability limitations, and strict termination or renewal windows. Total length is {len(pages_data)} page(s) "
            f"comprising {sum(p.get('word_count', 0) for p in pages_data):,} words."
        )

        return {
            "document_summary": summary,
            "contract_type": contract_type,
            "risk_score": calculated_score,
            "parties": parties,
            "risks": risks,
            "obligations": obligations,
            "deadlines": deadlines,
            "key_clauses": key_clauses,
        }
