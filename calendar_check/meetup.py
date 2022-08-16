import datetime
import json
import typing
import urllib.request

from . import calendar


class MeetupCalendar(calendar.Calendar):

    group: str

    def __init__(self, group: str):
        self.group = group

    def _load(self):
        with urllib.request.urlopen(f'https://api.meetup.com/{self.group}/events') as resp:
            return json.load(resp)

    def events(self, start: datetime.datetime, end: datetime.datetime) -> typing.List[calendar.Event]:
        tz = start.tzinfo
        events = []
        for event in self._load():
            dtstart = datetime.datetime.fromtimestamp(event['time'] // 1000).astimezone(tz)
            duration = datetime.timedelta(seconds=event['duration'] // 1000)
            if dtstart < start or dtstart >= end: continue

            events.append(calendar.Event(
                id=event['id'],
                link=event['link'],
                start=dtstart,
                duration=duration,
                summary=event['name'],
                description=event['description']))

        events.sort()
        return events
