#!/usr/bin/env python

# Reverse engineered from the Android App: uk.org.nt.android.app1
# http://old.nationaltrust.org.uk/event-search-2/events/index.json?apiKey=00000001-0002-0003-0004-000000000005&distance=20&period=One+month&latitude=51.47775&longitude=0.0&SortBy=distance&searchType=1

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

try:
    orig_data = urllib2.urlopen("%s?apiKey=%s&distance=%s&period=%s&latitude=%s&longitude=%s&SortBy=%s&searchType=%s" % (ENDPOINT, API_KEY, DISTANCE, PERIOD, LATITUDE, LONGITUDE, SORT_BY, SEARCH_TYPE))
    encoding = orig_data.headers['content-type'].split('charset=')[-1]
except urllib2.URLError as errorstring:
    pass

try:
    data = json.loads(orig_data.read().decode(encoding))
except Exception as errorstring:
    pass
else:
    print "BEGIN:VCALENDAR"
    print "X-WR-CALNAME:National Trust Events"
    print "VERSION:2.0"
    print "PRODID:-//ABC Corporation//NONSGML My Product//EN"
    for event in data["Events"]:
        print "BEGIN:VEVENT"
        for key,val in event.iteritems():
            if key == "periods":
                time_start = time.localtime(int(val[0]["start"][6:].split("+")[0]) / 1000)
                time_end = time.localtime(int(val[0]["end"][6:].split("+")[0]) / 1000)

                print "DTSTART:%s" % time.strftime("%Y%m%dT%H%M00Z", time_start)
                print "DTEND:%s" % time.strftime("%Y%m%dT%H%M00Z", time_end)
            try:
                print "%s:%s" % (field_map[key], val.replace("\r\n", "\\n").encode(encoding))
            except Exception as errorstring:
                pass
        print "DTSTAMP:%s" % time.strftime("%Y%m%dT%H%M00Z", today)
        print "END:VEVENT"
    print "END:VCALENDAR"

sys.exit(0)
