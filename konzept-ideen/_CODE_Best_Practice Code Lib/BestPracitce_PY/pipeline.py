
import json
from .extract_fields import extract_all
class Post:
    def __init__(self, fields):
        self.fields = fields
        self.company = fields.get("company")
        self.title = fields.get("title")
        self.posting_date_iso = fields.get("posting_date_iso")
        self.source_id = fields.get("id")
def process_documents(docs):
    posts = []
    for d in docs:
        f = extract_all(d["text"], d.get("id"))
        posts.append(Post(f))
    return posts
def to_jsonl(posts):
    return "\n".join(json.dumps(p.fields, ensure_ascii=False) for p in posts) + ("\n" if posts else "")
