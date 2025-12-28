
from job_mining.pipeline import process_documents, to_jsonl
def test_pipeline_smoke(tmp_path):
    recs = process_documents(["fixtures/anzeigen"])
    assert len(recs) >= 1
    out = tmp_path/"out.jsonl"
    to_jsonl(recs, str(out), "w")
    assert out.exists()
