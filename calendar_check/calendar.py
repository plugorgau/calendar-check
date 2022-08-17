import datetime
from typing import Iterator, List, Optional, Tuple


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


def match_events(cal1: Calendar, cal2: Calendar, start: datetime.datetime, end: datetime.datetime) -> Iterator[Tuple[Optional[Event], Optional[Event]]]:
    cal2_events = cal2.events(start, end)
    for ev1 in cal1.events(start, end):
        ev2 = None
        while len(cal2_events) > 0:
            ev2 = cal2_events[0]
            if ev1.overlaps(ev2):
                # ev2 matches ev1
                del cal2_events[0]
                break
            elif ev2 < ev1:
                # ev2 is before ev1, so can't have a match
                del cal2_events[0]
                yield (None, ev2)
            else:
                # ev2 is after ev1, so may match future event
                ev2 = None
                break
        yield (ev1, ev2)
    for ev2 in cal2_events:
        yield (None, ev2)
