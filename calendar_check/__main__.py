import datetime
import os
import pathlib
import sys
import typing
import zoneinfo

from . import meetup


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

def main(argv: typing.List[str]) -> None:
    tz = localtime()
    start = datetime.datetime.now(tz)
    end = start + datetime.timedelta(days=62)

    cal = meetup.MeetupCalendar('perth-linux-users-group-plug')
    for event in cal.events(start, end):
        print(event.id)
        print(event.link)
        print(event.start)
        print(event.duration)
        print(event.summary)
        print()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
