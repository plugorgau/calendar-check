import datetime
import os
import pathlib
import sys
from typing import List
import zoneinfo

from . import calendar, ical


def localtime() -> zoneinfo.ZoneInfo:
    """Get a tzinfo object representing the local time zone."""
    # First check the environment
    tzname = os.environ.get('TZ')
    # Then check if /etc/localtime is a symlink
    if tzname is None:
        localtime = pathlib.Path('/etc/localtime').resolve()
        for dir in zoneinfo.TZPATH:
            if localtime.is_relative_to(dir):
                tzname = str(localtime.relative_to(dir))
                break
    # Finally try the contents of the /etc/timezone file
    if tzname is None:
        with open('/etc/timezone', 'r') as fp:
            tzname = fp.read().strip()
    return zoneinfo.ZoneInfo(tzname)


def print_event(event: calendar.Event) -> None:
    print(f'  ID:       {event.id}')
    if event.link:
        print(f'  URL:      {event.link}')
    print(f'  Start:    {event.start}')
    print(f'  Duration: {event.duration}')
    print(f'  Summary:  {event.summary}')


def main(argv: List[str]) -> None:
    tz = localtime()
    start = datetime.datetime.now(tz)
    end = start + datetime.timedelta(days=62)

    g = ical.GoogleCalendar('president@plug.org.au')
    m = ical.MeetupCalendar('perth-linux-users-group-plug')
    l = ical.LumaCalendar('cal-f66nRr2rNhqzUXD')
    for (g_event, m_event, l_event) in calendar.match_events([g, m, l], start, end):
        if g_event is not None:
            print('Google:')
            print_event(g_event)
        if m_event is not None:
            print('Meetup:')
            print_event(m_event)
        if l_event is not None:
            print('Luma:')
            print_event(l_event)
        print('---')
        print()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
