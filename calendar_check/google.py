import datetime
from typing import List
import urllib.request
import zoneinfo

import icalendar
import dateutil.rrule

from . import calendar

class GoogleCalendar(calendar.Calendar):

    calendar: str

    def __init__(self, calendar):
        self.calendar = calendar

    def _load(self):
        with urllib.request.urlopen(f'https://calendar.google.com/calendar/ical/{self.calendar}/public/basic.ics') as resp:
            return icalendar.Calendar.from_ical(resp.read())

    def _make_event(self, dtstart, duration, component):
        return calendar.Event(
            id=component.get('uid'),
            link='',
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
