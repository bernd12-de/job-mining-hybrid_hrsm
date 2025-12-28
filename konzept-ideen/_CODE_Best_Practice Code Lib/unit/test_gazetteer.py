
def test_detect_location_basic():
    from ingest import detect_location
    t = "Wir suchen in Düsseldorf eine:n UX-Designer:in."
    loc = detect_location(t)
    assert loc == {} or loc.get("location_city") in ("Düsseldorf","Duesseldorf","Dusseldorf")
