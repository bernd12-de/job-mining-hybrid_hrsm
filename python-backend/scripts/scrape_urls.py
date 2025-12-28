import sys
import os
import json

# Ensure app modules are importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from app.infrastructure.crawling.web_scraper import WebScraper


def main(urls):
    ws = WebScraper(use_playwright=True)
    results = []
    for u in urls:
        try:
            r = ws.scrape(u)
            results.append({
                "url": u,
                "canonical": r.canonical_url,
                "engine": r.render_engine,
                "status": r.http_status,
                "text_len": len(r.text),
                "title": r.title,
                "warnings": r.warnings[:3],
            })
        except Exception as e:
            results.append({"url": u, "error": str(e)})
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # Accept URLs via CLI args; default to sample set if none provided
    args = sys.argv[1:]
    if not args:
        args = [
            "https://kind.softgarden.io/job/41199812?utm_source=jobspreader&utm_medium=referral&utm_campaign=jobspreader_premium&utm_content=P1M&utm_term=cc_k6kdr_8kqxd&l=de",
            "https://escape.jobs.personio.com/job/742758?language=de&display=de",
            "https://www.strauss.com/de/de/Unternehmen/Karriere/Jobangebote/Developer_mwd?utm_source=google&utm_medium=cpc&utm_campaign=DE%20-%20Karriere%20-%20IT&gad_source=1&gad_campaignid=13788646287&gbraid=0AAAAADwj_ZsksUq5EHE9u0TxPzlPdFPSx&gclid=Cj0KCQiAgbnKBhDgARIsAGCDdlf_Do5ThwTuCSy4nxnLCNVNRpi7q9XLiirkNkZ4WXHEMgGhNZ99-VoaAhKBEALw_wcB",
        ]
    main(args)
