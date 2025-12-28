# infrastructure/ingestion/parser.py
import fitz # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import os
import re
from typing import Optional
from docx import Document # Für DOCX Handling (aus requirements.txt)

# --- Hilfsfunktion für den OCR-Fallback ---

def _perform_ocr_fallback(file_path: str) -> str:
    """
    Führt OCR auf einer Datei aus, wenn direkte Textextraktion fehlschlägt.
    Wichtig für Screenshots und gescannte PDFs (ML Engineering).
    """
    text = ""
    try:
        # Konvertiert das Dokument/Bild in Bilder (erforderlich für pytesseract)
        images = convert_from_path(file_path)
        for image in images:
            # Tesseract mit deutschem Sprachpaket ('deu')
            text += pytesseract.image_to_string(image, lang='deu')
    except Exception as e:
        print(f"[ERROR] OCR failed for {file_path}: {e}")
        return ""
    return text

# --- Hauptfunktion: Extrahiert Text aus verschiedenen Formaten ---

def extract_text_from_file(file_path: str) -> Optional[str]:
    """
    Extrahiert Text aus PDF, DOCX oder Bilddateien.
    Stellt Robustheit durch den OCR-Fallback sicher.
    """
    text = ""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        try:
            # 1. Direkte Text-Extraktion (schnellste Methode)
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text("text")

            # Fallback, wenn nur wenig Text gefunden wurde (oft bei gescannten PDFs)
            if len(text.strip()) < 100:
                print(f"[WARN] PDF Text minimal, Fallback zu OCR für {file_path}")
                text = _perform_ocr_fallback(file_path)

        except Exception as e:
            # Fallback für korrupte PDFs
            print(f"[ERROR] Fehler in PyMuPDF: {e}. Versuche OCR.")
            text = _perform_ocr_fallback(file_path)

    elif file_extension in ['.jpg', '.jpeg', '.png']:
        # 2. Bilder (Screenshots) nutzen immer OCR
        text = _perform_ocr_fallback(file_path)

    elif file_extension in ['.docx']:
        # 3. Handling für DOCX (mit python-docx)
        try:
            document = Document(file_path)
            # Liest alle Absätze und fügt sie mit Zeilenumbruch zusammen
            text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        except Exception as e:
            print(f"[ERROR] Fehler beim Lesen von DOCX {file_path}: {e}")
            return None

    elif file_extension in ['.doc', '.txt']:
        # 4. Einfache Datei-Einlesung für ältere oder Plain-Text-Formate
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except:
            return None

    else:
        # Unbekanntes Format
        return None

    # Finaler Text wird bereinigt und zurückgegeben
    return text.strip()

# --- Ende von parser.py ---
