# -*- coding: utf-8 -*-
import json
import logging
import time
import re
import html
from datetime import datetime
from enum import Enum

from pyquery import PyQuery

from backend.util import send_request

logger = logging.getLogger(__name__)


class Issue(object):

    def __init__(self, url, author, template_creator=None, comment=None, date=None, parse_content=False, creator_comment="", self_made=False, domain=None, status=None):
        self.url = url
        self.template_creator = template_creator
        self.author = author
        self.comment = comment
        self.creator_comment = creator_comment or ""
        self.self_made = self_made
        self.domain = domain
        self.status = status or IssueType.UNPROCESSED

        if date is not None and not isinstance(date, int):
            try:
                tmp_date = datetime.strptime(date, "%b %d at %I:%M %p")
                tmp_date = tmp_date.replace(year=2019)
                self.date = int(time.mktime(tmp_date.timetuple()))
            except ValueError:
                # probably some timestamp cannot be parsed -> year in timestamp
                tmp_date = datetime.strptime(date, "%b %d, %Y at %I:%M %p")
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
        self.comment = html.escape(content.text())
        logger.info(self.comment.replace('\n', ' ')[:20])

        try:
            if self.creator_comment is None or self.creator_comment == "":
                template_creator_answer = pq(".issue-info-row-owner")("dd").text()
                if template_creator_answer is None:
                    self.creator_comment = ""
                else:
                    self.creator_comment = html.escape(template_creator_answer)
                if "Type of issue IV" in self.creator_comment:
                    logger.exception("ERROR!!! {}".format(template_creator_answer))
        except Exception as e:
            logger.exception(e)

        try:
            if self.template_creator is None or self.template_creator == "":
                logger.warning("Template creator is None or empty: {}".format(self.url))
                template_creator_field = pq(".input-group-addon")("li").eq(3).text()
                regex = re.compile(r"Template #[0-9]{1,4} \(by (.*?)\)")
                template_creator = regex.match(template_creator_field).group(1)

                self.template_creator = template_creator or ""
        except Exception as e:
            logger.exception(e)

        try:
            logger.info("Names: {} - {}".format(self.template_creator, self.author))
            if self.template_creator == self.author:
                logger.info("Self made issue!")
                self.self_made = True
        except Exception as e:
            logger.exception(e)

    def to_dict(self):
        return dict(author=self.author,
                    url=self.url,
                    comment=self.comment,
                    date=self.date,
                    template_creator=self.template_creator,
                    creator_comment=self.creator_comment,
                    self_made=self.self_made,
                    domain=self.domain,
                    status=self.status.value)

    @staticmethod
    def from_dict(issue_dict):
        url = issue_dict.get("url")
        author = issue_dict.get("author")
        comment = issue_dict.get("comment")
        date = issue_dict.get("date")
        creator_comment = issue_dict.get("creator_comment")
        template_creator = issue_dict.get("template_creator")
        self_made = issue_dict.get("self_made")
        domain = issue_dict.get("domain")
        status = IssueType(issue_dict.get("status"))

        return Issue(url=url, author=author, template_creator=template_creator, comment=comment, date=date, creator_comment=creator_comment, self_made=self_made, domain=domain, status=status)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __dict__(self):
        return self.to_dict()


class IssueType(Enum):
    UNPROCESSED = 0
    ACCEPTED = 1
    DECLINED = 2
