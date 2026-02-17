import datetime
from typing import List
import urllib.request
import zoneinfo

import icalendar
import dateutil.rrule

from . import calendar


class ICalendar(calendar.Calendar):

    _url: str

    def __init__(self, url):
        self._url = url

    def _load(self) -> icalendar.Calendar:
        with urllib.request.urlopen(self._url) as resp:
            return icalendar.Calendar.from_ical(resp.read())

    def _make_event(self, dtstart: datetime.datetime, duration: datetime.timedelta, component: icalendar.Component) -> calendar.Event:
        return calendar.Event(
            id=component.get('uid'),
            link=component.get('url', ''),
            start=dtstart,
            duration=duration,
            summary=component.get('summary'),
            description=component.get('description'),
        )

    def events(self, start: datetime.datetime, end: datetime.datetime) -> List[calendar.Event]:
        tz = start.tzinfo
        events = []
        for component in self._load().walk():
            if component.name != 'VEVENT': continue
            dtstart = component.decoded('dtstart')
            # skip all-day events
            if not isinstance(dtstart, datetime.datetime): continue
            dtstart = dtstart.astimezone(tz)
            duration = component.decoded('dtend').astimezone(tz) - dtstart

            # Expand component according to recurrence rule
            if component.has_key('rrule'):
                rrule = dateutil.rrule.rrulestr('\n'.join(
                    line for line in component.content_lines()
                    if (line.startswith('RRULE') or
                        line.startswith('RDATE') or
                        line.startswith('EXRULE') or
                        line.startswith('EXDATE') or
                        line.startswith('DTSTART'))
                ), tzids=zoneinfo.ZoneInfo)
                for rep in rrule.between(start, end):
                    events.append(self._make_event(rep, duration, component))
            else:
                if start <= dtstart < end:
                    events.append(self._make_event(dtstart, duration, component))
        events.sort()
        return events


