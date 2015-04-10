#!/usr/bin/python

#
# 1) Scrape Aurora converter data from local Aurora Weblog page
# 2) publish "Aktuelle Leistung" to emoncms via get(url)
#    - via try/except for web accesses
#    - transmitting "no response" to emoncms if local aurora page hangs
#
# 150410 first stable 1.0 version.
#

STARTUP_MESSAGE_VERSION = '150410 aurora_to_emoncms 1.0'

from bs4 import BeautifulSoup
import urllib2, time, requests

from mytokens import EMONCMS_WRITE_API_KEY, AURORA_LOCAL_URL

emoncms_url_init = 'http://emoncms.org/input/post.json?apikey=' + EMONCMS_WRITE_API_KEY


def aurora_scrape(url):
    try:
        content = urllib2.urlopen(url).read()
        soup = BeautifulSoup(content)
        # strip texts from webpage content
        list = []
        for string in soup.stripped_strings:
            list.append((repr(string)))

        # extract converter values
        dataset = dict([
            ("Aktuelle Leistung", list[27][2:-1]),
            ("Aktuelle Monatsenergie", list[30][2:-1]),
            ("Aktuelle Tagesenergie", list[33][2:-1]),
            ("Aktuelle Jahresenergie", list[36][2:-1]),
            ("Tagesenergie Vortag", list[39][2:-1]),
            ("Gesamtenergie", list[42][2:-1])])

    except:
        dataset = dict([
            ("Aktuelle Leistung", "no response"),
            ("Aktuelle Monatsenergie", "no response"),
            ("Aktuelle Tagesenergie", "no response"),
            ("Aktuelle Jahresenergie", "no response"),
            ("Tagesenergie Vortag", "no response"),
            ("Gesamtenergie", "no response")])

    return dataset


print '###'
print '###'
print '### ' + STARTUP_MESSAGE_VERSION
print '###'
print '###'
print

while True:
    dataset = aurora_scrape(AURORA_LOCAL_URL)

    for key in dataset.keys():
        print key, " = ", dataset[key]

    # construct URL
    emoncms_url = emoncms_url_init + '&node=30' + '&csv=' + dataset["Aktuelle Leistung"]
    print emoncms_url

    # send data to emoncms & handle exceptions.
    # Use requests instead of urllib2 to catch exceptions.
    try:
        response = requests.get(emoncms_url, timeout=15)
    except requests.ConnectionError as e:
        print e
        response = 'ConnectionError execption: No response'
    except:
        response = 'Unidentified exception ...'

    print response
    print
    time.sleep(20)
