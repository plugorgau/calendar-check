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
        req = urllib.request.Request(self._url)
        req.add_header('User-Agent', 'calendar-check/0')
        with urllib.request.urlopen(req) as resp:
            return icalendar.Calendar.from_ical(resp.read())

    def _make_event(self, dtstart: datetime.datetime, duration: datetime.timedelta, component: icalendar.Component) -> calendar.Event:
        return calendar.Event(
            id=component.get('uid'),
            link=self._event_url(component),
            start=dtstart,
            duration=duration,
            summary=component.get('summary'),
            description=component.get('description'),
        )

    def _event_url(self, component: icalendar.Component) -> str:
        return component.get('url', '')

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


class GoogleCalendar(ICalendar):

    def __init__(self, calendar):
        super().__init__(f'https://calendar.google.com/calendar/ical/{calendar}/public/basic.ics')


class MeetupCalendar(ICalendar):

    def __init__(self, group: str):
        super().__init__(f'https://www.meetup.com/{group}/events/ical/')


class LumaCalendar(ICalendar):

    def __init__(self, calendar: str):
        super().__init__(f'https://api2.luma.com/ics/get?entity=calendar&id={calendar}')

    def _event_url(self, component: icalendar.Component) -> str:
        event_id = component.get('uid').split('@')[0]
        return f'https://luma.com/event/{event_id}'
