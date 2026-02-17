from . import ical


class MeetupCalendar(ical.ICalendar):

    def __init__(self, group: str):
        super().__init__(f'https://www.meetup.com/{group}/events/ical/')
