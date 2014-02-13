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

today = time.localtime()

# Fetch the original data
try:
    orig_data = urllib2.urlopen("%s?apiKey=%s&distance=%s&period=%s&latitude=%s&longitude=%s&SortBy=%s&searchType=%s" % (ENDPOINT, API_KEY, DISTANCE, PERIOD, LATITUDE, LONGITUDE, SORT_BY, SEARCH_TYPE))

    # Fetch the encoding so that we can handle special characters correctly
    encoding = orig_data.headers['content-type'].split('charset=')[-1]
except urllib2.URLError as errorstring:
    # Ignore errors as there's no mechanism to report errors in ICS
    # -- perhaps create a calendar item for "now" with the error??
    pass

try:
    # Convert from JSON into native Python objects
    # -- paying special attention to the encoding
    data = json.loads(orig_data.read().decode(encoding))
except Exception as errorstring:
    # Ignore errors as there's no mechanism to report errors in ICS
    pass
else:
    # Begin calendar output
    print "BEGIN:VCALENDAR"
    print "X-WR-CALNAME:National Trust Events"
    print "VERSION:2.0"
    print "PRODID:-//ABC Corporation//NONSGML My Product//EN"

    # Loop through the events
    for event in data["Events"]:
        print "BEGIN:VEVENT"
        for key,val in event.iteritems():
            # Create usable time objects for formatting into ICS-compatible entries
            if key == "periods":
                time_start = time.localtime(int(val[0]["start"][6:].split("+")[0]) / 1000)
                time_end = time.localtime(int(val[0]["end"][6:].split("+")[0]) / 1000)

                print "DTSTART:%s" % time.strftime("%Y%m%dT%H%M00Z", time_start)
                print "DTEND:%s" % time.strftime("%Y%m%dT%H%M00Z", time_end)

            # Use the field map to determince which items to displa
            try:
                # Replace CRLF with '\n' and re-encode with the original encoding used
                print "%s:%s" % (field_map[key], val.replace("\r\n", "\\n").encode(encoding))
            except Exception as errorstring:
                # Ignore entries that aren't in the field map
                pass

        # DTSTAMP field is required.  Set to 'now' (-ish).
        print "DTSTAMP:%s" % time.strftime("%Y%m%dT%H%M00Z", today)
        print "END:VEVENT"
    print "END:VCALENDAR"

sys.exit(0)
