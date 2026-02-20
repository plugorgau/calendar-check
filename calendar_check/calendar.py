import datetime
from typing import Iterator, List, Optional, Sequence, Tuple


class Event:
    id: str
    link: str
    start: datetime.datetime
    duration: datetime.timedelta
    summary: str
    description: str

    def __init__(self, id, link, start, duration, summary, description):
        self.id = id
        self.link = link
        self.start = start
        self.duration = duration
        self.summary = summary
        self.description = description

    def __lt__(self, other: 'Event') -> bool:
        return self.start < other.start or (self.start == other.start and self.duration < other.duration)

    def overlaps(self, other: 'Event') -> bool:
        # Zero length events can't overlap
        if self.duration == datetime.timedelta(0) or other.duration == datetime.timedelta(0):
            return False
        if self.start <= other.start:
            return self.start + self.duration > other.start
        else:
            return other.start + other.duration > self.start


class Calendar:

    def events(self, start: datetime.datetime, end: datetime.datetime) -> List[Event]:
        raise NotImplementedError


def match_events(calendars: Sequence[Calendar], start: datetime.datetime, end: datetime.datetime) -> Iterator[Tuple[Optional[Event], ...]]:
    if len(calendars) == 0:
        return
    cal1_events = calendars[0].events(start, end)
    for evt_match in match_events(calendars[1:], start, end):
        ev1 = None
        other = next((ev for ev in evt_match if ev is not None), None)
        while len(cal1_events) > 0:
            ev1 = cal1_events[0]
            if ev1.overlaps(other):
                # ev2 matches ev1
                del cal1_events[0]
                break
            elif ev1 < other:
                # ev1 is before other, so can't have a match
                del cal1_events[0]
                yield (ev1,) + (None,) * len(evt_match)
                ev1 = None
            else:
                # ev1 is after ev2, so may match future event
                ev1 = None
                break
        yield (ev1,) + evt_match
    for ev1 in cal1_events:
        yield (ev1,) + (None,) * (len(calendars) - 1)
