
import re
def parse_date(text: str):
    t = text or ""
    m = re.search(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", t)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}", "iso", "day"
    m = re.search(r"\b(0?[1-9]|[12]\d|3[01])[.\/](0?[1-9]|1[0-2])[.\/](\d{4})\b", t)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}", "dmy", "day"
    m = re.search(r"(?:stand|veröffentlicht am|as of)[: ]+\s*(0?[1-9]|1[0-2])[/-](\d{2,4})", t, re.I)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        if y < 100: y = 2000 + y
        return f"{y:04d}-{mo:02d}-15", "as_of", "month"
    m = re.search(r"(jan|feb|mär|mae|mar|apr|mai|jun|jul|aug|sep|okt|nov|dez)[a-z]*\s+(\d{4})", t, re.I)
    if m:
        pref = m.group(1).lower()[:3]
        norm = {"mär":"mar","mae":"mar"}.get(pref, pref)
        idx = ["jan","feb","mar","apr","mai","jun","jul","aug","sep","okt","nov","dez"].index(norm)
        mo = idx+1
        y = int(m.group(2))
        return f"{y:04d}-{mo:02d}-15", "month_text", "month"
    return None, None, None
