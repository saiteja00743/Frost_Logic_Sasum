import re
import difflib
from typing import List, Dict, Any, Tuple, Optional

class VerificationService:
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for robust comparison:
        - Collapses whitespace
        - Standardizes unicode quotes and dashes
        - Strips leading/trailing punctuation
        """
        if not text:
            return ""
        # Standardize quotes and hyphens
        s = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
        s = s.replace("—", "-").replace("–", "-")
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @classmethod
    def verify_quote(
        cls, quote: str, claimed_page: Optional[int], pages_data: List[Dict[str, Any]]
    ) -> Tuple[str, Optional[int], Optional[str], float]:
        """
        Verifies a quote against document pages.
        Returns:
            (status: 'verified' | 'unverified', actual_page, matched_excerpt, confidence)
        """
        if not quote or len(quote.strip()) < 5:
            return "unverified", claimed_page, None, 0.0

        clean_quote = cls.normalize_text(quote)
        clean_quote_lower = clean_quote.lower()

        # Build normalized text map for all pages
        normalized_pages = []
        for p in pages_data:
            p_num = p["page_number"]
            p_raw = p.get("text", "")
            p_norm = cls.normalize_text(p_raw)
            normalized_pages.append((p_num, p_norm, p_raw))

        # 1. Exact match on claimed page (case-insensitive)
        if claimed_page is not None:
            for p_num, p_norm, p_raw in normalized_pages:
                if p_num == claimed_page:
                    idx = p_norm.lower().find(clean_quote_lower)
                    if idx != -1:
                        # Extract excerpt
                        start = max(0, idx - 40)
                        end = min(len(p_norm), idx + len(clean_quote) + 40)
                        matched = p_norm[start:end]
                        return "verified", claimed_page, matched, 1.0

        # 2. Exact match across any other page
        for p_num, p_norm, p_raw in normalized_pages:
            idx = p_norm.lower().find(clean_quote_lower)
            if idx != -1:
                start = max(0, idx - 40)
                end = min(len(p_norm), idx + len(clean_quote) + 40)
                matched = p_norm[start:end]
                return "verified", p_num, matched, 0.95

        # 3. Substring / N-gram sliding window fuzzy matching
        # If the quote is long, check if a 6-word or 8-word sequence exists
        quote_words = clean_quote_lower.split()
        if len(quote_words) >= 4:
            # Take core snippet (up to first 8 words)
            sub_snippet = " ".join(quote_words[:min(len(quote_words), 8)])
            for p_num, p_norm, p_raw in normalized_pages:
                if sub_snippet in p_norm.lower():
                    # Calculate similarity against local segment
                    idx = p_norm.lower().find(sub_snippet)
                    window_len = len(clean_quote) + 80
                    segment = p_norm[max(0, idx - 20) : min(len(p_norm), idx + window_len)]
                    sim = difflib.SequenceMatcher(None, clean_quote_lower, segment.lower()).ratio()
                    if sim >= 0.65:
                        return "verified", p_num, segment[:250], round(sim, 2)

        # 4. Longest common substring fallback
        best_ratio = 0.0
        best_page = claimed_page
        best_snippet = None

        for p_num, p_norm, _ in normalized_pages:
            # Check ratio against sentences in page
            sentences = re.split(r"(?<=[.!?])\s+", p_norm)
            for sent in sentences:
                if len(sent) > 20:
                    ratio = difflib.SequenceMatcher(None, clean_quote_lower, sent.lower()).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_page = p_num
                        best_snippet = sent

        if best_ratio >= 0.82:
            return "verified", best_page, best_snippet, round(best_ratio, 2)

        return "unverified", claimed_page, None, 0.0

    @classmethod
    def verify_analysis_findings(cls, analysis_data: Dict[str, Any], pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs verification over risks, obligations, deadlines, and key clauses.
        Enriches each item with verification_status and corrected page references.
        Returns updated analysis_data with verification_summary.
        """
        total_items = 0
        verified_items = 0
        unverified_items = 0

        # Helper to verify a list of items with an 'evidence' field
        def process_items(items_list):
            nonlocal total_items, verified_items, unverified_items
            for item in items_list:
                total_items += 1
                evidence = item.get("evidence", {})
                quote = evidence.get("quote", "")
                claimed_page = evidence.get("page")

                status, verified_page, matched_excerpt, confidence = cls.verify_quote(
                    quote, claimed_page, pages_data
                )

                item["verification_status"] = status
                evidence["page"] = verified_page
                evidence["confidence"] = confidence
                if matched_excerpt:
                    evidence["matched_text"] = matched_excerpt

                if status == "verified":
                    verified_items += 1
                else:
                    unverified_items += 1

        if "risks" in analysis_data:
            process_items(analysis_data["risks"])
        if "obligations" in analysis_data:
            process_items(analysis_data["obligations"])
        if "deadlines" in analysis_data:
            process_items(analysis_data["deadlines"])
        if "key_clauses" in analysis_data:
            process_items(analysis_data["key_clauses"])

        rate = round((verified_items / max(total_items, 1)) * 100, 1)

        analysis_data["verification_summary"] = {
            "total_items_checked": total_items,
            "verified_count": verified_items,
            "unverified_count": unverified_items,
            "verification_rate_percent": rate,
            "audit_passed": rate >= 70.0
        }

        return analysis_data
