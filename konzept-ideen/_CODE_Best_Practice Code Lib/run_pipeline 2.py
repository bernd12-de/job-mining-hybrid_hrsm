import os
from tests.testcases import load_docs
from job_mining.pipeline import process_documents
def main():
    os.makedirs("out", exist_ok=True)
    posts = process_documents(load_docs())
    with open("out.jsonl","w",encoding="utf-8") as f:
        for p in posts: f.write(p.to_json()+"\n")
    print(f"Wrote {len(posts)} records to out.jsonl")
if __name__ == "__main__": main()