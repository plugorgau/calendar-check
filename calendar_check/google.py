from . import ical

class GoogleCalendar(ical.ICalendar):

    def __init__(self, calendar):
        super().__init__(f'https://calendar.google.com/calendar/ical/{calendar}/public/basic.ics')
