# --------------------------------------------------------------------
#
# Copyright (C) 2013 Daniel Triendl <daniel@pew.cc>
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# COPYING for more details.
#
# --------------------------------------------------------------------

import logging
logger = logging.basicConfig(level=logging.WARN)

from bmscraper import BMScraper, AndroidEmotesProcessorFactory
from bmscraper.ratelimiter import TokenBucket
from data import *
from json import dumps
import os
import gzip

factory = AndroidEmotesProcessorFactory(single_emotes_filename=os.path.join( '..', 'single_emotes', '{}', '{}.png'))
scraper = BMScraper(factory)
scraper.user = 'ponymoteharvester'
scraper.password = 'berry_punch'
scraper.subreddits = subreddits
scraper.user_agent = 'linux:Ponymote harvester:v2.1 (by /u/Trellmor)'
scraper.image_blacklist = image_blacklist_android
scraper.emote_info = emote_info
scraper.rate_limit_lock = TokenBucket(15, 30)

scraper.scrape()

def save_if_new(filename, data):
    data_old = ''
    if (os.path.exists(filename)):
        f = gzip.open(filename, 'r')
        data_old = f.read()
        f.close()

    if data != data_old:
        f = gzip.open(filename, 'wb')
        f.write(data)
        f.close()

def sum_size(emotes):
    total = 0
    for image in [emote["image"] for emote in emotes]:
        filename = os.path.join('..', 'single_emotes', image)
        total += os.path.getsize(filename)
    return total


def save_subreddit(subreddit):
    subreddit_emotes = [x for x in factory.emotes if x['sr'] == subreddit['name']]
    subreddit_emotes = sorted(subreddit_emotes, key = lambda x: x['image'])
    emotes_file = os.path.join('..', 'single_emotes', subreddit['name'], 'emotes.json.gz')
    if not os.path.exists(os.path.dirname(emotes_file)):
        os.makedirs(os.path.dirname(emotes_file))

    emotes_data = dumps(subreddit_emotes, separators=(',', ': '))
    save_if_new(emotes_file, emotes_data)
    subreddit["size"] = sum_size(subreddit_emotes)


for subreddit in subreddit_data:
    save_subreddit(subreddit)

subreddit_data = dumps(subreddit_data, separators=(',', ': '))
subreddit_file = os.path.join('..', 'single_emotes', 'subreddits.json.gz')
save_if_new(subreddit_file, subreddit_data)
