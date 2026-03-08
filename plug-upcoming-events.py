#!/usr/bin/python3

import datetime
import email.message
import os
import pathlib
import sys
import zoneinfo

from calendar_check import calendar, ical


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


def get_event_info(start: datetime.datetime, end: datetime.datetime) -> str:
    g = ical.GoogleCalendar('president@plug.org.au')
    m = ical.MeetupCalendar('perth-linux-users-group-plug')
    l = ical.LumaCalendar('cal-f66nRr2rNhqzUXD')
    events = []
    for (g_event, m_event, l_event) in calendar.match_events([g, m, l], start, end):
        # Take details from the first non-None event
        ev = next(ev for ev in (g_event, m_event, l_event) if ev is not None)
        output = f'{ev.summary}\n'
        start = ev.start.strftime('%d %B %Y, %I:%M %P')
        duration = f'{round(ev.duration.total_seconds() / 3600)} hours'
        output += f'    {start} ({duration})\n'
        if g_event and g_event.link:
            output += f'    Google: {g_event.link}\n'
        if m_event and m_event.link:
            output += f'    Meetup: {m_event.link}\n'
        if l_event and l_event.link:
            output += f'    Luma:   {l_event.link}\n'
        events.append(output)
    return '\n'.join(events)


def main(argv: list[str]) -> None:
    tz = localtime()
    start = datetime.datetime.now(tz)
    end = start + datetime.timedelta(days=31)

    events = get_event_info(start, end)
    if not events:
        return

    msg = email.message.EmailMessage()
    msg.set_content(events)
    msg['Subject'] = 'PLUG Upcoming Events'
    msg['From'] = 'events-bot@plug.org.au'
    msg['To'] = 'plug@plug.org.au'
    msg['Reply-To'] = 'plug@plug.org.au'
    print(msg)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
