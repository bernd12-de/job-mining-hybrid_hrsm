
import os, re, zipfile, subprocess, html

def _clean(s: str) -> str:
    if not s: return ""
    s = s.replace("\u00ad","").replace("\u2011","-")
    s = re.sub(r"[ \t]+"," ", s)
    s = re.sub(r"\s+\n","\n", s)
    s = re.sub(r"\n{3,}","\n\n", s)
    return s.strip()

def read_txt(p):
    return open(p,"r",encoding="utf-8",errors="ignore").read()

def read_docx(p):
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8","ignore")
    xml = re.sub(r"</w:p>","\n", xml)
    xml = re.sub(r"<w:br[^>]*>","\n", xml)
    text = re.sub(r"<[^>]+>","", xml)
    return html.unescape(text)

def _pdf_with_pypdf2(p):
    try:
        import PyPDF2
        text = []
        with open(p, "rb") as fh:
            reader = PyPDF2.PdfReader(fh)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception:
        return None

def _pdf_with_pdfminer(p):
    try:
        from pdfminer_high_level import extract_text   # try alt name first
    except Exception:
        try:
            from pdfminer.high_level import extract_text
        except Exception:
            return None
    try:
        return extract_text(p)
    except Exception:
        return None

def _pdf_with_pdftotext(p):
    out = p + ".txt"
    try:
        subprocess.run(["pdftotext","-layout",p,out], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return open(out,"r",encoding="utf-8",errors="ignore").read()
    except Exception:
        return None
    finally:
        try: os.remove(out)
        except Exception: pass

def _pdf_with_ocr(p):
    try:
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
    except Exception:
        return None
    try:
        pages = convert_from_path(p, dpi=200)
        txt = []
        for im in pages[:10]:
            txt.append(pytesseract.image_to_string(im))
        return "\n".join(txt)
    except Exception:
        return None

def read_pdf(p):
    for fn in (_pdf_with_pypdf2, _pdf_with_pdfminer, _pdf_with_pdftotext, _pdf_with_ocr):
        txt = fn(p)
        if txt and txt.strip():
            return txt
    print(f"[WARN] PDF konnte nicht extrahiert werden (fehlende Tools/Bibliotheken): {p}")
    return ""

def _is_url(x: str) -> bool:
    return x.startswith("http://") or x.startswith("https://")

def _read_url(url: str) -> str:
    try:
        import requests, bs4
        r = requests.get(url, timeout=25, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","noscript","svg"]): tag.decompose()
        return soup.get_text("\n")
    except Exception as e:
        print(f"[WARN] URL konnte nicht geladen werden: {url} ({e})")
        return ""

def read_any(x):
    # strip surrounding quotes if present
    if isinstance(x,str) and len(x)>=2 and ((x[0]==x[-1]=='"') or (x[0]==x[-1]=="'")):
        x = x[1:-1]
    if _is_url(x):
        t = _read_url(x); return {"id": x, "text": _clean(t)}
    ext = os.path.splitext(x)[1].lower()
    if ext in (".txt",".md"): t = read_txt(x)
    elif ext == ".docx": t = read_docx(x)
    elif ext == ".pdf": t = read_pdf(x)
    else:
        if os.path.isdir(x):
            # collapse directory into many files (txt/docx/pdf)
            toks = []
            for root,_,files in os.walk(x):
                for fn in files:
                    if fn.lower().endswith((".txt",".docx",".pdf")):
                        try:
                            toks.append(read_any(os.path.join(root,fn))["text"])
                        except Exception: pass
            return {"id": x, "text": _clean("\n\n".join(toks))}
        try: t = read_txt(x)
        except Exception: raise FileNotFoundError(x)
    return {"id": os.path.basename(x), "text": _clean(t)}
