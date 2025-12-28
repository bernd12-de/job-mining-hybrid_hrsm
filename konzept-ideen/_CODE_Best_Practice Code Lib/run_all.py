
import sys, yaml
from job_mining.pipeline import process_documents, to_jsonl, enrich_with_esco, load_esco_alias
def main(argv=None):
    cfg_path=(argv or sys.argv)[1] if len(argv or sys.argv)>1 else "sources.yaml"
    cfg=yaml.safe_load(open(cfg_path,"r",encoding="utf-8"))
    recs=process_documents(cfg.get("inputs",[]), render_js=bool(cfg.get("render_js",False)))
    recs=enrich_with_esco(recs, load_esco_alias())
    to_jsonl(recs, cfg.get("out","out.jsonl"), mode=cfg.get("mode","w"))
    print(f"Wrote {len(recs)} records to {cfg.get('out','out.jsonl')}")
    return 0
if __name__=="__main__": import sys; raise SystemExit(main(sys.argv))
