
import re, datetime
MONTHS_DE = {"januar":1,"jan":1,"februar":2,"feb":2,"märz":3,"maerz":3,"mrz":3,"mar":3,"april":4,"apr":4,"mai":5,"juni":6,"jun":6,"juli":7,"jul":7,"august":8,"aug":8,"september":9,"sept":9,"sep":9,"oktober":10,"okt":10,"oct":10,"november":11,"nov":11,"dezember":12,"dez":12,"dec":12}
def _clamp_year(y:int)->int:
    nowy = datetime.date.today().year
    if y>nowy: return nowy
    if y<1970: return 1970
    return y
def parse_date(text:str, now_utc=None):
    s=(text or "").strip()
    if not s: return (None,None,None)
    t=s.lower().replace(","," ").replace("·"," ").replace("•"," ")
    t=re.sub(r"\s+"," ",t)
    m=re.search(r"\b(20\d{2}|19\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b",t)
    if m:
        y,mn,d=int(m.group(1)),int(m.group(2)),int(m.group(3)); y=_clamp_year(y)
        return (f"{y:04d}-{mn:02d}-{d:02d}","iso","day")
    m=re.search(r"\b(0?[1-9]|[12]\d|3[01])[.\-/](0?[1-9]|1[0-2])[.\-/](\d{4})\b",t)
    if m:
        d,mn,y=int(m.group(1)),int(m.group(2)),int(m.group(3)); y=_clamp_year(y)
        return (f"{y:04d}-{mn:02d}-{d:02d}","dmy","day")
    m=re.search(r"\b([a-zäöü]{3,10})\s+(\d{4})\b",t)
    if m:
        mon=MONTHS_DE.get(m.group(1).replace("ä","ae").replace("ö","oe").replace("ü","ue"))
        y=int(m.group(2))
        if mon: y=_clamp_year(y); return (f"{y:04d}-{mon:02d}-01","montext","month")
    m=re.search(r"\b(20\d{2}|19\d{2})\b",t)
    if m:
        y=_clamp_year(int(m.group(1))); return (f"{y:04d}-06-15","year_fallback","year")
    return (None,None,None)
