from json import loads;
import itertools
from data import subreddits
import urllib3

http = urllib3.PoolManager()
r = http.request('GET', 'http://berrymotes.com/assets/berrymotes_json_data.json')
data = loads(r.data)
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
