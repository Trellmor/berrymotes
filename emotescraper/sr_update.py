from json import loads;
import itertools
from data import subreddits
import requests


r = requests.get('http://berrymotes.com/assets/berrymotes_json_data.json')
data = loads(r.text)
key_func = lambda e: e['sr']
sr_new = []
for sr, group in itertools.groupby(sorted(data, key=key_func), key_func):
    sr_new.append(sr.encode('ascii', 'ignore'));

sr_banned = [
        "arborus",
        "BTMoonlitNSFW",
        "clopclop",
        "clopmotes",
        "multihoofdrinking",
        "mylittleaprilfools",
        "mylittlensfw",
        "spaceclop",
        "themirishponies"
        ]

sr_new = list(set(sr_new) - set(subreddits))
sr_new = list(set(sr_new) - set(sr_banned))

for sr in sr_new:
    print '    "' + sr + '",'
