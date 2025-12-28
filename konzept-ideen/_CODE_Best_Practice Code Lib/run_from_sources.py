
import argparse
from job_mining.pipeline import process_documents, to_jsonl, enrich_with_esco, load_esco_alias
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--render-js", action="store_true", default=False)
    p.add_argument("--write", action="store_true", default=False)
    p.add_argument("--mode", choices=["w","a"], default="w")
    p.add_argument("--out", default="out.jsonl")
    p.add_argument("inputs", nargs="*")
    args=p.parse_args(argv)
    recs=process_documents(args.inputs, render_js=args.render_js)
    recs=enrich_with_esco(recs, load_esco_alias())
    if args.write: to_jsonl(recs, args.out, mode=args.mode)
    if args.write: print(f"Wrote {len(recs)} records to {args.out}")
    else: print(f"Records: {len(recs)}")
    return 0
if __name__=="__main__": import sys; raise SystemExit(main(sys.argv))
