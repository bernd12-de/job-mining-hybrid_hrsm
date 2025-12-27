from interfaces import ITextExtractor
from typing import BinaryIO
from pypdf import PdfReader
from docx import Document
import os

class AdvancedTextExtractor(ITextExtractor):
    """
    Implementierung des ITextExtractor Interfaces.
    Verarbeitet PDF, DOCX und Plain Text, mit Fokus auf Robustheit.
    """

    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        """Extrahiert den bereinigten Text aus dem Dateistream."""

        # Sicherstellen, dass der Stream am Anfang steht
        file_stream.seek(0)

        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == '.pdf':
            return self._extract_from_pdf(file_stream)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_stream)
        elif file_ext in ['.txt', '.csv']:
            # Für einfache Textdateien
            return file_stream.read().decode('utf-8', errors='ignore')
        else:
            # Hier würde später ein OCR-Fallback erfolgen (TO DO: Phase 3)
            print(f"⚠️ FEHLER: Unbekannter Dateityp '{file_ext}'. Versuche Text zu lesen...")
            try:
                return file_stream.read().decode('utf-8', errors='ignore')
            except Exception:
                return ""


    def _extract_from_pdf(self, file_stream: BinaryIO) -> str:
        text = []
        try:
            reader = PdfReader(file_stream)
            for page in reader.pages:
                text.append(page.extract_text() or "") # Sicherstellen, dass keine None-Werte hinzugefügt werden
            return "\n".join(text)
        except Exception as e:
            print(f"❌ PDF-Extraktion fehlgeschlagen: {e}")
            return ""

    def _extract_from_docx(self, file_stream: BinaryIO) -> str:
        text = []
        try:
            document = Document(file_stream)
            for para in document.paragraphs:
                text.append(para.text)
            return "\n".join(text)
        except Exception as e:
            print(f"❌ DOCX-Extraktion fehlgeschlagen: {e}")
            return ""
