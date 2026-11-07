from datetime import date, time, timedelta
from agent.clinic import Clinic, normalize_phone, parse_day, spoken_time


def weekday(offset: int = 1) -> date:
    d = date.today() + timedelta(days=offset)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def test_phone_normalisation():
    assert normalize_phone("0151 234 5678") == "+491512345678"
    assert normalize_phone("0049 151 2345678") == "+491512345678"
    assert normalize_phone("12") is None


def test_offers_at_most_three_slots_and_no_weekends():
    c = Clinic()
    assert len(c.free_slots(weekday(), "physio")) == 3
    sat = date.today() + timedelta(days=(5 - date.today().weekday()) % 7 or 7)
    assert c.free_slots(sat, "physio") == []


def test_booking_and_double_booking():
    c, d = Clinic(), weekday()
    assert c.book(d, time(9), "physio", "Max", "0151 2345678").startswith("Gebucht")
    assert "nicht mehr frei" in c.book(d, time(9), "physio", "Eva", "0151 2345678")


def test_bad_phone_is_rejected_before_booking():
    c = Clinic()
    assert "unvollständig" in c.book(weekday(), time(10), "physio", "Max", "123")
    assert not c.booked


def test_parse_day_and_speech():
    today = date(2026, 11, 9)
    assert parse_day("morgen", today) == date(2026, 11, 10)
    assert parse_day("14.11.", today) == date(2026, 11, 14)
    assert spoken_time(time(14, 30)) == "14 Uhr 30"


def test_agent_registers_tools():
    from agent.receptionist import Receptionist
    assert {t.id for t in Receptionist(Clinic()).tools} == {"find_slots", "book", "request_callback"}


def test_long_service_blocks_following_slot():
    c, d = Clinic(), weekday()
    assert c.book(d, time(9), "massage", "Max", "0151 2345678").startswith("Gebucht")
    assert time(9, 30) not in c.free_slots(d, "physio", limit=50)
    assert time(16, 30) not in c.free_slots(d, "massage", limit=50)  # would end after closing
