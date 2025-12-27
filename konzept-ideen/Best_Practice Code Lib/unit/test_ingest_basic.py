
def test_title_regex_no_crash():
    from ingest import safe_title_from_head
    head = "HR-Manager (m/w/d) – Onboarding – Digitalisierung – Standort (Berlin)"
    t = safe_title_from_head(head, "doc.txt")
    assert isinstance(t, str) and len(t) >= 5

def test_future_date_guard():
    from ingest import guard_future_year
    import datetime
    assert guard_future_year(datetime.date(2408,7,24)) is None
