
#!/usr/bin/env python3
import os, json, sys, html, collections
CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial,sans-serif;margin:24px;line-height:1.45}
h1,h2,h3{margin:0.6em 0 0.35em}
table{border-collapse:collapse;width:100%;margin:12px 0 24px}
th,td{border:1px solid #ddd;padding:8px;text-align:left}
th{background:#f5f5f5}
.small{color:#555;font-size:0.9em}
.badge{display:inline-block;padding:2px 8px;border:1px solid #ddd;border-radius:999px;margin:2px;font-size:0.85em}
.card{border:1px solid #ddd;border-radius:12px;padding:16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.topbar{display:flex;gap:12px;align-items:center;margin-bottom:16px}
.topbar a{padding:8px 12px;border:1px solid #ddd;border-radius:8px;text-decoration:none;color:#111}
code{background:#f6f8fa;padding:1px 4px;border-radius:4px}
"""
def load_json(p): 
    with open(p,"r",encoding="utf-8") as f: return json.load(f)
def load_jsonl(p):
    rows=[]; 
    if os.path.exists(p):
        for ln in open(p,"r",encoding="utf-8"):
            ln=ln.strip(); 
            if not ln: continue
            rows.append(json.loads(ln))
    return rows
def write(path, html_txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: f.write(html_txt)
def render_company_pages(rows, outdir):
    # build per-company timelines (counts by year) from data
    comp_years = collections.defaultdict(collections.Counter)
    for r in rows:
        comp = r.get("company") or "Unknown"
        y = (r.get("posting_date_iso") or "")[:4]
        if y and y.isdigit(): comp_years[comp][y]+=1
    for comp, years in comp_years.items():
        top_skills = []
        # naive top skills from tools mapped to pseudo ESCO ids (if present)
        html_txt = [f"<html><head><meta charset='utf-8'><title>{html.escape(comp)} – Company</title><style>{CSS}</style></head><body>"]
        html_txt.append(f"<div class='topbar'><a href='../index.html'>← Report</a><h1>{html.escape(comp)}</h1></div>")
        html_txt.append("<div class='grid'>")
        # summary card
        html_txt.append("<div class='card'><h2>Summary</h2><p>Postings by year:</p><div>")
        for y,c in sorted(years.items()):
            html_txt.append(f"<span class='badge'>{y}: {c}</span>")
        html_txt.append("</div></div>")
        # end cards
        html_txt.append("</div></body></html>")
        write(os.path.join(outdir, f"{comp}.html"), "".join(html_txt))
def render_index(out_jsonl, companies_json, industries_json, out_dir):
    rows = load_jsonl(out_jsonl)
    # Compute dataset-level timeline
    timeline = collections.Counter()
    for r in rows:
        y = (r.get("posting_date_iso") or "")[:4]
        if y and y.isdigit(): timeline[y]+=1
    # Build simple company pages
    render_company_pages(rows, os.path.join(out_dir,"companies"))
    # Index
    html_out = [f"<html><head><meta charset='utf-8'><title>Job Mining Report</title><style>{CSS}</style></head><body>"]
    html_out.append("<div class='topbar'><h1>Job Mining – Report</h1><span class='small'>Quelle: <code>out.jsonl</code></span></div>")
    html_out.append("<div class='grid'>")
    # Dataset timeline
    html_out.append("<div class='card'><h2>Timeline (Postings/Jahr)</h2><div>")
    for y,c in sorted(timeline.items()):
        html_out.append(f"<span class='badge'>{y}: {c}</span>")
    html_out.append("</div></div>")
    # Table of latest records
    html_out.append("<div class='card'><h2>Records</h2><table><tr><th>Company</th><th>Title</th><th>City</th><th>Date</th><th>Tools</th></tr>")
    for r in rows[:200]:
        html_out.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(r.get("company") or "")),
            html.escape(str(r.get("title") or "")),
            html.escape(str(r.get("location_city") or "")),
            html.escape(str(r.get("posting_date_iso") or "")),
            html.escape(", ".join(r.get("tools") or []))
        ))
    html_out.append("</table></div>")
    html_out.append("</div>") # grid
    html_out.append("<p class='small'>Dieser Report wurde automatisch erzeugt. Einzelheiten je Firma sind verlinkt (sofern vorhanden).</p></body></html>")
    write(os.path.join(out_dir,"index.html"), "".join(html_out))
def main(argv):
    if len(argv)<4:
        print("Usage: report.py <out.jsonl> <companies.json> <industries.json> [out_dir=report]"); return 2
    out_jsonl, companies_json, industries_json = argv[1], argv[2], argv[3]
    out_dir = argv[4] if len(argv)>4 else "report"
    render_index(out_jsonl, companies_json, industries_json, out_dir)
    print(f"Report generated: {out_dir}/index.html"); return 0
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
