import logging
from typing import List

import arrow
import requests
from arrow import Arrow
from cachetools import cached, TTLCache
from ics import Calendar, Event

from config import EVENTS_CACHE_SECONDS


@cached(cache=TTLCache(maxsize=1, ttl=EVENTS_CACHE_SECONDS))
def get_events(url: str, max_results: int, max_days: int) -> List[Event]:
    if max_results < 1:
        raise ValueError("Events max results should be greater than 0")

    logging.info(f"Loading calendar from {url}")

    calendar = Calendar(requests.get(url).text)
    events: List[Event] = list(calendar.timeline)

    now: arrow = Arrow.now()

    items = []
    for index, event in enumerate(events):
        if event.end < now:
            continue
        if index >= max_results or (0 < max_days < days_between(now, event.begin)):
            break
        items.append(event)

    return items


def days_between(first_date: Arrow, second_date: Arrow) -> int:
    difference = second_date - first_date
    return difference.days
