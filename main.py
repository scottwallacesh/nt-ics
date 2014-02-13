#!/usr/bin/env python

"""
Simple POC to see if we can fetch National Trust events and output as ICS-compatible.  Good for Google Calendar, iCal, etc.

Reverse engineered from the Android App: uk.org.nt.android.app1
Original URL: http://old.nationaltrust.org.uk/event-search-2/events/index.json?apiKey=00000001-0002-0003-0004-000000000005&distance=20&period=One+month&latitude=51.47775&longitude=0.0&SortBy=distance&searchType=1
"""

ENDPOINT="http://old.nationaltrust.org.uk/event-search-2/events/index.json"

#===================
# Parameters
#===================
API_KEY="00000001-0002-0003-0004-000000000005" # Fake UUID?
DISTANCE=20 # Miles
PERIOD="One+month"
SORT_BY="distance"
SEARCH_TYPE=1 # Others?

# Greenwich, London UK
# TODO: Location picker
LATITUDE=51.47775
LONGITUDE=0
#===================

# A map of the JSON fields to their ICS equivalent
field_map = { "loc": "LOCATION",
              "desc": "DESCRIPTION",
              "sum": "SUMMARY",
              "uuid": "UID",
              "ci": "ORGANIZER"
            }

import sys
import urllib2
import json
import time

#===================
# Flask stuff for Google App Engine
#===================
from flask import Flask
app = Flask(__name__)
#===================

class Calendar:
    header = "BEGIN:VCALENDAR\nX-WR-CALNAME:National Trust Events\nVERSION:2.0\nPRODID:-//Scott Wallace//NONSGML nt-ics//EN"
    footer = "END:VCALENDAR"

    def __init__(self):
        self.events = []

    def add(self, event):
        # Check it's a valid Event type and the fields are all correct:
        if isinstance(event, Event) and event.check_fields():
            self.events.append(event)

    def __str__(self):
        output = self.header + "\n"
        for event in self.events:
            output += str(event)
        output += self.footer + "\n"

        return output

class Event:
    mandatory_fields = [ "DTSTART", "DTEND", "SUMMARY", "LOCATION", "UID" ]

    header = "BEGIN:VEVENT"
    footer = "END:VEVENT"

    def __init__(self):
        self.fields = {}

    def check_fields(self):
        # Check the mandatory fields exist:
        for field in self.mandatory_fields:
            if field not in self.fields:
                return False

        # Check the time entries are the correct type:
        if not isinstance(self.fields["DTSTART"], time.struct_time) or not isinstance(self.fields["DTEND"], time.struct_time):
            return False

        return True

    def __str__(self):
        # Check the basics exist
        if self.check_fields():
            output = self.header + "\n"

            # Output the fields added
            for key, val in self.fields.iteritems():
                # Format time values correctly
                if isinstance(val, time.struct_time):
                    val = time.strftime("%Y%m%dT%H%M00Z", val)

                output += "%s:%s\n" % (key, val)

            output += "DTSTAMP:%s" % time.strftime("%Y%m%dT%H%M00Z", time.localtime()) + "\n"
            output += self.footer + "\n"

            return output

@app.route("/")
def build_calendar():
    # Fetch the original data
    try:
        orig_data = urllib2.urlopen("%s?apiKey=%s&distance=%s&period=%s&latitude=%s&longitude=%s&SortBy=%s&searchType=%s" % (ENDPOINT, API_KEY, DISTANCE, PERIOD, LATITUDE, LONGITUDE, SORT_BY, SEARCH_TYPE))

        # Fetch the encoding so that we can handle special characters correctly
        encoding = orig_data.headers['content-type'].split('charset=')[-1]
    except urllib2.URLError as errorstring:
        # Exit now
        sys.exit(1)

    try:
        # Convert from JSON into native Python objects
        # -- paying special attention to the encoding
        data = json.loads(orig_data.read().decode(encoding))
    except Exception as errorstring:
        # Exit now
        sys.exit(2)
    else:
        # New calendar
        calendar = Calendar()

        # Loop through the events
        for event in data["Events"]:
            new_event = Event()
            for key,val in event.iteritems():
                # Create usable time objects for formatting into ICS-compatible entries
                if key == "periods":
                    new_event.fields["DTSTART"] = time.localtime(int(val[0]["start"][6:].split("+")[0]) / 1000)
                    new_event.fields["DTEND"] = time.localtime(int(val[0]["end"][6:].split("+")[0]) / 1000)
                # Use the field map to determince which items to add
                try:
                    if val:
                        new_event.fields[field_map[key]] = val.replace("\r\n", "\\n").encode(encoding)
                except AttributeError as errorstring:
                    # Ignore empty values
                    pass
                except KeyError as errorstring:
                    # Ignore entries that aren't in the field map
                    pass

            calendar.add(new_event)

    return str(calendar)
