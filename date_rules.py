import re
from datetime import datetime, time, timedelta

WEEKDAY_PATTERNS = {
    0: r"\b(?:понедельник[а-я]*|пн)\b",
    1: r"\b(?:вторник[а-я]*|вт)\b",
    2: r"\b(?:сред[а-я]*|ср)\b",
    3: r"\b(?:четверг[а-я]*|чт)\b",
    4: r"\b(?:пятниц[а-я]*|пт)\b",
    5: r"\b(?:суббот[а-я]*|сб)\b",
    6: r"\b(?:воскресень[а-я]*|вс)\b",
}
DEADLINE_HOUR = 18


def fallback_deadline(now: datetime) -> datetime:
    return now + timedelta(hours=24)


def next_weekday_at(now: datetime, target_weekday: int, deadline_time: time = time(DEADLINE_HOUR, 0)) -> datetime:
    days_ahead = (target_weekday - now.weekday()) % 7

    new_deadline = datetime.combine(
        now.date() + timedelta(days=days_ahead),
        deadline_time,
        tzinfo=now.tzinfo
    )

    if new_deadline < now:
        new_deadline += timedelta(days=7)

    return new_deadline


def deadline_from_phrase(due_phrase: str | None, now: datetime) -> datetime:
    if not due_phrase:
        return fallback_deadline(now)

    phrase = due_phrase.strip().lower()

    if phrase in {"срочно", "как можно скорее", "побыстрее"}:
        return fallback_deadline(now)

    if "сегодня" in phrase:
        print(2)

        new_deadline = datetime.combine(
            now.date(),
            time(DEADLINE_HOUR, 0),
            tzinfo=now.tzinfo
        )

        print(f"due_phrase = {due_phrase}; new_deadline = {new_deadline}; now = {now}")

        if new_deadline > now:
            return new_deadline

        return datetime.combine(
            now.date() + timedelta(days=1),
            time(DEADLINE_HOUR, 0),
            tzinfo=now.tzinfo
        )

    if "завтра" in phrase:
        return datetime.combine(
            now.date() + timedelta(days=1),
            time(DEADLINE_HOUR, 0),
            tzinfo=now.tzinfo
        )

    for weekday_index, weekday_name in WEEKDAY_PATTERNS.items():
        if re.search(weekday_name, phrase):
            return next_weekday_at(now, weekday_index)

    match = re.search(r"\bчерез\s+(\d+)\s+(?:день|дня|дней)\b", phrase)
    if match:
        days = int(match.group(1))
        return now + timedelta(days=days)

    return fallback_deadline(now)


if __name__ == "__main__":
    from zoneinfo import ZoneInfo

    test_now = datetime(2026, 10, 6, 17, 0, tzinfo=ZoneInfo("Asia/Yekaterinburg"))

    phrases = [
        "сегодня"
    ]

    for phrase in phrases:
        result = deadline_from_phrase(phrase, test_now)
        print(f"{phrase!r} -> {result.isoformat()}")
