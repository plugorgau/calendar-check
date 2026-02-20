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
    cal1_events = cal1.events(start, end)
    for ev2 in cal2.events(start, end):
        ev1 = None
        while len(cal1_events) > 0:
            ev1 = cal1_events[0]
            if ev1.overlaps(ev2):
                # ev2 matches ev1
                del cal1_events[0]
                break
            elif ev1 < ev2:
                # ev1 is before ev2, so can't have a match
                del cal1_events[0]
                yield (ev1, None)
                ev1 = None
            else:
                # ev1 is after ev2, so may match future event
                ev1 = None
                break
        yield (ev1, ev2)
    for ev1 in cal1_events:
        yield (ev1, None)
