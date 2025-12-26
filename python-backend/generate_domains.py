import pypdf
import json
import re
from pathlib import Path

def extract_from_dir(directory: str, output_filename: str):
    print(f"📂 Scanne Verzeichnis: {directory}...")
    keywords = set()
    path = Path(directory)

    if not path.exists():
        print(f"⚠️ Pfad nicht gefunden: {directory}")
        return

    for pdf_file in path.glob("*.pdf"):
        print(f"  📄 Lese {pdf_file.name}...")
        try:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Sucht nach Fachbegriffen (Substantive, Komposita)
                    found = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß-]{3,25}\b', text)
                    keywords.update([f.lower() for f in found])
        except Exception as e:
            print(f"  ❌ Fehler bei {pdf_file.name}: {e}")

    output_path = Path(f"data/job_domains/{output_filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(keywords)), f, ensure_ascii=False, indent=4)
    print(f"✅ Domain gespeichert unter: {output_path} ({len(keywords)} Begriffe)")

if __name__ == "__main__":
    # Ebene 4: Fachbücher (Gharbi, Wolff, Spillner)
    extract_from_dir("data/source_pdfs/fachbuecher", "fachbuch_domain")

    # Ebene 5: Modulhandbücher (Hochschule/Uni)
    extract_from_dir("data/source_pdfs/modulhandbuecher", "academia_domain")
