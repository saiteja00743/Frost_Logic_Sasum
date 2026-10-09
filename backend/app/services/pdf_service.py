import pymupdf
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

class PDFProcessingError(Exception):
    pass

class PDFService:
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract text page-by-page from PDF bytes.
        Returns:
            (pages_list, summary_metadata)
        """
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise PDFProcessingError(f"Could not open PDF file. The file may be corrupted or encrypted: {str(e)}")

        total_pages = len(doc)
        if total_pages == 0:
            raise PDFProcessingError("The uploaded PDF has 0 pages.")

        pages_data = []
        total_words = 0
        total_chars = 0
        has_text_layer = False

        for page_idx in range(total_pages):
            page = doc[page_idx]
            text = page.get_text("text") or ""
            # Clean up excessive null bytes or weird control chars while preserving formatting
            cleaned_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
            words = len(cleaned_text.split())
            chars = len(cleaned_text)

            total_words += words
            total_chars += chars

            if chars > 20:
                has_text_layer = True

            pages_data.append({
                "page_number": page_idx + 1,
                "text": cleaned_text,
                "word_count": words,
                "char_count": chars,
            })

        doc.close()

        # Detect scanned/empty PDFs
        is_scanned = not has_text_layer or (total_words / max(total_pages, 1) < 15)

        metadata = {
            "total_pages": total_pages,
            "total_words": total_words,
            "total_chars": total_chars,
            "is_scanned_or_empty": is_scanned,
            "has_extractable_text": has_text_layer,
        }

        return pages_data, metadata

    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        with open(file_path, "rb") as f:
            return PDFService.extract_text_from_bytes(f.read())
