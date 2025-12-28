import glob, json, os, zipfile, csv, io, sys
def load_from_zip(zip_path_glob):
    paths = glob.glob(zip_path_glob)
    if not paths: raise FileNotFoundError(zip_path_glob)
    zpath = paths[0]
    with zipfile.ZipFile(zpath, "r") as z:
        names = [n for n in z.namelist() if n.endswith(".csv") and "de" in n.lower()]
        aliases = {}
        for name in names:
            with z.open(name) as f:
                text = io.TextIOWrapper(f, encoding="utf-8", errors="ignore")
                reader = csv.reader(text, delimiter=";")
                for row in reader:
                    row = [c.strip() for c in row]
                    if not row: continue
                    for c in row[1:]:
                        if c and len(c) > 2:
                            aliases.setdefault(c.lower(), set()).add(row[0])
        aliases = {k: sorted(list(v))[0] for k,v in aliases.items()}
    os.makedirs("data", exist_ok=True)
    outp = "data/esco_alias.json"
    json.dump(aliases, open(outp,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"ESCO-Aliase geschrieben: {outp} (Keys: {len(aliases)})")
if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: python esco_loader.py 'ESCO*.zip'"); sys.exit(1)
    load_from_zip(sys.argv[1])