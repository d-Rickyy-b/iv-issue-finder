# -*- coding: utf-8 -*-
import logging
import html
import urllib.request
import urllib
from json import JSONEncoder
from threading import Thread, current_thread, Event


useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) " \
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 " \
            "Safari/537.36"

logger = logging.getLogger(__name__)


def send_request(url):
    logger.debug("Requesting url '{}'!".format(url))

    req = urllib.request.Request(
        url,
        data=None,
        headers={'User-Agent': useragent}
    )

    f = urllib.request.urlopen(req)

    html_str = f.read().decode('utf-8')
    html_str = html.unescape(html_str)
    return html_str


class DataEncoder(JSONEncoder):
        def default(self, o):
            return o.to_dict()
