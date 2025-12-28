
import os, subprocess, sys, shlex, yaml
BANNER = """
==================== Job Mining Console (v12) ====================
[1] Komplettlauf (sources.yaml)                 -> run_all.py
[2] Pipeline auf beliebige Quellen (mehrzeilig) -> run_from_sources.py
[3] Demo-Run (Fixtures, alle Dateien)           -> run_pipeline.py
[4] Firmen/Branchen-Register bauen              -> (stub)
[5] Tests ausführen                             -> pytest
[6] sources.yaml anzeigen/ändern                
[7] HTML-Report erzeugen (Filter+Timeline)      -> report.py
[8] Umgebungscheck (Libs, Tools, Browser)       -> tools/env_check.py
[9] JS-Smoke-Test (ohne echten Renderer)        -> ingest.read_any(render_js=True)
[10] ESCO-Aliasdaten aus ZIP bauen              -> esco_loader.py
[0] Beenden
==================================================================
"""
def run(cmd:list):
    print("$"," ".join(shlex.quote(c) for c in cmd)); subprocess.run(cmd, check=False)
def show_sources():
    p="sources.yaml"
    if os.path.exists(p): print(open(p,"r",encoding="utf-8").read())
    else:
        cfg={"out":"out.jsonl","mode":"w","render_js":False,"inputs":["fixtures/anzeigen"]}
        open(p,"w",encoding="utf-8").write(yaml.safe_dump(cfg, allow_unicode=True)); print(open(p,"r",encoding="utf-8").read())
def edit_sources_add():
    print('Gib Pfade/URLs **einzeln** ein (Leerzeile beendet).')
    entries=[]
    while True:
        s=input("> ").strip()
        if not s: break
        if s.startswith("--"): continue
        entries.append(s)
    cfg={"out":"out.jsonl","mode":"w","render_js":False,"inputs":["fixtures/anzeigen"]}
    if os.path.exists("sources.yaml"): cfg=yaml.safe_load(open("sources.yaml","r",encoding="utf-8"))
    cfg.setdefault("inputs",[])
    for e in entries:
        if e not in cfg["inputs"]: cfg["inputs"].append(e)
    open("sources.yaml","w",encoding="utf-8").write(yaml.safe_dump(cfg, allow_unicode=True))
    print("sources.yaml aktualisiert.")
def main():
    while True:
        print(BANNER)
        c=input("Auswahl [1] ").strip() or "1"
        if c=="0": print("Bye."); break
        elif c=="1":
            p=input("Pfad zu sources.yaml [sources.yaml] ").strip() or "sources.yaml"
            run([sys.executable,"run_all.py",p])
        elif c=="2":
            edit_sources_add()
            cfg=yaml.safe_load(open("sources.yaml","r",encoding="utf-8"))
            fl=["--render-js"] if cfg.get("render_js") else []
            run([sys.executable,"run_from_sources.py",*fl,*cfg.get("inputs",[]),"--write","--out",cfg.get("out","out.jsonl"),"--mode",cfg.get("mode","w")])
        elif c=="3": run([sys.executable,"run_pipeline.py"])
        elif c=="4": print("Registry written. (stub)")
        elif c=="5": run([sys.executable,"-m","pytest","-q"])
        elif c=="6": show_sources()
        elif c=="7": run([sys.executable,"report.py"])
        elif c=="8": run([sys.executable,"tools/env_check.py"])
        elif c=="9":
            url=input("Test-URL [https://example.com] ").strip() or "https://example.com"
            from job_mining.ingest import read_any
            print(read_any(url, render_js=True)["text"][:300])
        elif c=="10":
            z=input("Pfad zur ESCO-ZIP [ESCO*.zip] ").strip() or "ESCO*.zip"
            run([sys.executable,"esco_loader.py",z])
        else: print("Unbekannte Auswahl.")
if __name__=="__main__": main()
