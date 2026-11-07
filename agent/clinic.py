"""Business logic of the receptionist, independent from the voice stack so it can be unit-tested."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
import re

OPENING = [time(h, m) for h in range(8, 17) for m in (0, 30)]
SERVICES = {"physio": 30, "massage": 60, "consultation": 30}


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"[^\d+]", "", raw)
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if digits.startswith("0"):
        digits = "+49" + digits[1:]
    return digits if re.fullmatch(r"\+\d{8,15}", digits) else None


def spoken_time(t: time) -> str:
    """Times are read out, so '14:30' becomes 'half past two in the afternoon' style German phrasing."""
    return f"{t.hour} Uhr" if t.minute == 0 else f"{t.hour} Uhr {t.minute}"


@dataclass
class Clinic:
    booked: dict[tuple[date, time], str] = field(default_factory=dict)
    callbacks: list[dict] = field(default_factory=list)

    def free_slots(self, day: date, service: str, limit: int = 3) -> list[time]:
        if service not in SERVICES or day.weekday() >= 5 or day < date.today():
            return []
        free = [t for t in OPENING if (day, t) not in self.booked]
        return free[:limit]

    def book(self, day: date, start: time, service: str, name: str, phone: str) -> str:
        p = normalize_phone(phone)
        if p is None:
            return "Die Telefonnummer ist unvollständig. Bitte noch einmal langsam nennen."
        if start not in self.free_slots(day, service, limit=len(OPENING)):
            return "Dieser Termin ist leider nicht mehr frei."
        self.booked[(day, start)] = f"{name} {p} {service}"
        return f"Gebucht: {service} am {day:%d.%m.} um {spoken_time(start)}."

    def callback(self, name: str, phone: str, topic: str) -> str:
        p = normalize_phone(phone)
        if p is None:
            return "Die Telefonnummer ist unvollständig. Bitte noch einmal langsam nennen."
        self.callbacks.append({"name": name, "phone": p, "topic": topic[:200],
                               "at": datetime.now().isoformat(timespec="minutes")})
        return "Notiert. Wir rufen Sie heute noch zurück."


def parse_day(text: str, today: date | None = None) -> date | None:
    today = today or date.today()
    t = text.lower().strip()
    if t in ("heute", "today"):
        return today
    if t in ("morgen", "tomorrow"):
        return today + timedelta(days=1)
    if t in ("übermorgen",):
        return today + timedelta(days=2)
    if re.fullmatch(r"\d{1,2}\.\d{1,2}\.", t):
        t = f"{t}{today.year}"
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(t, fmt).date()
        except ValueError:
            pass
    return None
