from bs4 import BeautifulSoup
import urllib2

from mytokens import EMONCMS_WRITE_API_KEY, AURORA_LOCAL_URL

url = AURORA_LOCAL_URL
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

for key in dataset.keys():
    print key, " = ", dataset[key]

