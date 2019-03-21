# -*- coding: utf-8 -*-
import json
import logging
import time
from datetime import datetime

from pyquery import PyQuery

from util import send_request

logger = logging.getLogger(__name__)


class Issue(object):

    def __init__(self, url, author, comment=None, date=None, parse_content=False):
        self.url = url
        self.author = author
        self.comment = comment

        if date is not None and not isinstance(date, int):
            tmp_date = datetime.strptime(date, "%b %d at %I:%M %p")
            tmp_date = tmp_date.replace(year=2019)
            self.date = int(time.mktime(tmp_date.timetuple()))
        else:
            self.date = date

        if parse_content or comment is None:
            self.parse_comment()

    def parse_comment(self):
        if self.url is None:
            self.comment = "SOMETHING BAD HAPPENED!!! Please check logs!"
            return
        issue_content = send_request(self.url)
        pq = PyQuery(issue_content)

        content = pq(".issue-comment-text").eq(0)
        self.comment = content.text()
        logger.info(self.comment.replace('\n', ' ')[:20])

    def to_dict(self):
        return dict(author=self.author, url=self.url, comment=self.comment, date=self.date)

    @staticmethod
    def from_dict(issue_dict):
        url = issue_dict.get("url")
        author = issue_dict.get("author")
        comment = issue_dict.get("comment")
        date = issue_dict.get("date")

        return Issue(url=url, author=author, comment=comment, date=date)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __dict__(self):
        return self.to_dict()
