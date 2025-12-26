import os
from typing import BinaryIO
from pypdf import PdfReader
from docx import Document

# Korrekter Import des Interfaces
from app.interfaces.interfaces import ITextExtractor

class AdvancedTextExtractor(ITextExtractor):
    """
    Liest rohe Bytes (PDF, DOCX, TXT) und wandelt sie in einen sauberen String um.
    Kennt keine Business-Logik, nur Dateiformate.
    """

    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Hauptmethode: Entscheidet anhand der Dateiendung, welcher Parser genutzt wird.
        """
        # Sicherheitsnetz: Stream auf Anfang setzen
        file_stream.seek(0)

        # Dateiendung normalisieren (kleingeschrieben)
        file_ext = os.path.splitext(filename)[1].lower()

        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_stream)
            elif file_ext == '.docx':
                return self._extract_from_docx(file_stream)
            elif file_ext in ['.txt', '.csv', '.rtf', '.md']:
                # Fallback: Text decodieren, Fehlerzeichen ignorieren
                return file_stream.read().decode('utf-8', errors='ignore')
            else:
                print(f"⚠️ Warnung: Unbekanntes Format '{file_ext}' bei {filename}. Versuche Text-Lesen.")
                return file_stream.read().decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"❌ Kritischer Fehler beim Lesen von {filename}: {e}")
            return ""

    def _extract_from_pdf(self, file_stream: BinaryIO) -> str:
        text_parts = []
        try:
            reader = PdfReader(file_stream)
            for page in reader.pages:
                # Extrahiert Text oder leeren String (falls Seite leer/Bild)
                content = page.extract_text()
                if content:
                    text_parts.append(content)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"❌ PDF-Parsing Fehler: {e}")
            return ""

    def _extract_from_docx(self, file_stream: BinaryIO) -> str:
        text_parts = []
        try:
            document = Document(file_stream)
            for para in document.paragraphs:
                if para.text:
                    text_parts.append(para.text)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"❌ DOCX-Parsing Fehler: {e}")
            return ""
