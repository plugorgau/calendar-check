# PLUG Calendar Checker

This repository contains a script intended to help manage PLUG's
events calendar.

PLUG publishes events to two locations: a public Google Calendar and a
Meetup group. Occasionally the two get out of sync, so it'd be good to
know if we forgot to publish an event somewhere.

This script does so by downloading the two sets of events (from the
Google iCalendar feed and Meetup REST API respectively), and tries to
match events from each calendar.

## Dependencies

The script is written in Python. On a recent Ubuntu or Debian system,
the following command should ensure the required dependencies are
available:

```sh
sudo apt install python3 python3-dateutil python3-icalendar
```

## Invocation

Currently all the configuration is hard coded. The script can be run
from a checkout with:

```sh
python3 -m calendar_check
```

This will go through the events for the next 2 months and indicate
which ones are only in Google, only in Meetup, or are available in
both.

## Future

* Check if event summaries and descriptions for matching events are in sync
* Figure out how to provide links to Google events
