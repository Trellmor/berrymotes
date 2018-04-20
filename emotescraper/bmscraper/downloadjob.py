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

from workerpool import Job
from time import sleep

import logging

logger = logging.getLogger(__name__)


class DownloadJob(Job):
    def __init__(self, requests, url, retry=1, rate_limit_lock=None, callback=None, **callbackargs):
        super(DownloadJob, self).__init__()
        self._url = url
        self._requests = requests

        self._callback = callback
        self._callbackargs = callbackargs
        self._retry = retry
        self.rate_limit_lock = rate_limit_lock

    def run(self):
        try:
            response = None

            while (not response or response.status_code != 200) and self._retry > 0:
                backoff = 0
                try:
                    self._retry -= 1
                    self.rate_limit_lock and self.rate_limit_lock.acquire()
                    response = self._requests.get(self._url)
                    if ("over18" in response.url):
                        response = self._requests.post(response.url, {"over18": "yes"})
                except Exception, e:
                    logger.exception(e)
                    response = None
                finally:
                    if response is not None and response.status_code == 403:
                        logger.error("Error loading {}: Access denied (Code {})".format(self._url, response.status_code))
                        self._retry = 0
                    if response is None or response.status_code != 200:
                        logger.warn("Error loading {} (Code {}), retrying {} more times".format(self._url, response.status_code if response is not None else 0, self._retry))
                        backoff += 10
                        sleep(backoff)

            if self._callback:
                self._callback(response, **self._callbackargs)
        except Exception, e:
            logger.exception(e)
