import sys, yaml, json
from ingest import read_any
def main(argv):
    cfg_path = argv[1] if len(argv)>1 else "sources.yaml"
    cfg = yaml.safe_load(open(cfg_path,"r",encoding="utf-8"))
    out = cfg.get("out","out.jsonl"); mode = cfg.get("mode","w"); render_js = cfg.get("render_js", False)
    inputs = cfg.get("inputs", [])
    allrecs = []
    for x in inputs:
        try:
            rec = read_any(x, render_js=render_js)
            if isinstance(rec, list): allrecs.extend(rec)
            else: allrecs.append(rec)
        except Exception as e:
            print("[WARN]", x, ":", str(e))
    with open(out, mode, encoding="utf-8") as f:
        for r in allrecs: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    print(f"Wrote {len(allrecs)} records to {out}")
if __name__ == "__main__": raise SystemExit(main(sys.argv))