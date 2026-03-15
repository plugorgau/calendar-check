#!/usr/bin/python3

import datetime
import email.message
import os
import pathlib
import smtplib
import sys
import zoneinfo

import jinja2

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


class MergedEvent:
    summary: str
    start: datetime.datetime
    duration: datetime.timedelta
    google: calendar.Event | None
    meetup: calendar.Event | None
    luma: calendar.Event | None

    def __init__(self, g_event: calendar.Event | None,
                 m_event: calendar.Event | None,
                 l_event: calendar.Event | None) -> None:
        ev = next(ev for ev in (g_event, m_event, l_event) if ev is not None)
        self.summary = ev.summary
        self.start = ev.start
        self.duration = ev.duration
        self.google = g_event
        self.meetup = m_event
        self.luma = l_event

    @property
    def has_link(self) -> bool:
        return (self.google and self.google.link or
                self.meetup and self.meetup.link or
                self.luma and self.luma.link)


def get_event_info(start: datetime.datetime, end: datetime.datetime) -> list[MergedEvent]:
    g = ical.GoogleCalendar('president@plug.org.au')
    m = ical.MeetupCalendar('perth-linux-users-group-plug')
    l = ical.LumaCalendar('cal-f66nRr2rNhqzUXD')
    return [
        MergedEvent(g_event, m_event, l_event)
        for (g_event, m_event, l_event) in calendar.match_events([g, m, l], start, end)
    ]


text_template = jinja2.Environment(autoescape=False).from_string('''\
This is an automated email reminder of upcoming PLUG events. Full
details can be found in the PLUG calendar or Meetup.

{% for ev in events -%}
{{ ev.start.strftime('%d %B %Y') }} - {{ ev.summary }}
{%- if ev.google and ev.google.link %}
    Cal:    {{ ev.google.link }}
{%- endif %}
{%- if ev.meetup and ev.meetup.link %}
    Meetup: {{ ev.meetup.link }}
{%- endif %}
{%- if ev.luma and ev.luma.link %}
    Luma:   {{ ev.luma.link }}
{%- endif %}

{% endfor %}
''')

html_template = jinja2.Environment(autoescape=True).from_string('''\
<html>
<body>
<p>This is an automated email reminder of upcoming PLUG events. Full
details can be found in the PLUG calendar or Meetup.</p>
<ul>

{% for ev in events %}
<li>{{ ev.start.strftime('%d %B %Y') }} - {{ ev.summary }}
{%- if ev.has_link %}

[
{%- if ev.google and ev.google.link %}
<a href="{{ ev.google.link }}">Calendar</a>
{%- endif %}
{%- if ev.meetup and ev.meetup.link %}
<a href="{{ ev.meetup.link }}">Meetup</a>
{%- endif %}
{%- if ev.luma and ev.luma.link %}
<a href="{{ ev.luma.link }}">Luma</a>
{%- endif %}
]
{%- endif %}
</li>
{%- endfor %}
</ul>
</body>
</html>
''')


def main(argv: list[str]) -> None:
    tz = localtime()
    start = datetime.datetime.now(tz)
    end = start + datetime.timedelta(days=31)

    events = get_event_info(start, end)
    if not events:
        return

    msg = email.message.EmailMessage()
    msg.set_content(text_template.render(events=events))
    msg.add_alternative(html_template.render(events=events), subtype='html')
    msg['Subject'] = 'PLUG Upcoming Events'
    msg['From'] = 'PLUG Committee <committee@plug.org.au>'
    msg['To'] = 'plug@plug.org.au'
    msg['Reply-To'] = 'plug@plug.org.au'

    smtp = smtplib.SMTP('localhost')
    smtp.send_message(msg)
    smtp.quit()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
