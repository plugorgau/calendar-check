import datetime
from typing import List


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


class Calendar:

    def events(self, start: datetime.datetime, end: datetime.datetime) -> List[Event]:
        raise NotImplementedError
