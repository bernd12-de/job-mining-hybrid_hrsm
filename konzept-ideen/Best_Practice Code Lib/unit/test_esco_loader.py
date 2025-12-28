
def test_esco_fallback_present():
    from ingest import ESCO_ALIASES
    assert "docker" in ESCO_ALIASES
