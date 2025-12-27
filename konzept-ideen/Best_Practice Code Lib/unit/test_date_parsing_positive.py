
from job_mining.normalize import parse_date
def test_parse_date_iso():
    iso, src, prec = parse_date("2024-07-15"); assert iso=="2024-07-15" and src=="iso"
def test_parse_date_dmy():
    iso, src, prec = parse_date("15.03.2024"); assert src=="dmy"
def test_parse_date_montext():
    iso, src, prec = parse_date("März 2023"); assert src=="montext"
