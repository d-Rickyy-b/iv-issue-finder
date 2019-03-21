# -*- coding: utf-8 -*-
import json
import logging

from pyquery import PyQuery

from issue import Issue
from util import send_request

logger = logging.getLogger(__name__)


class Template(object):

    def __init__(self, creator, url, parse_content, issues=None):
        self.creator = creator
        self.url = url
        self.issues = issues or []
        self.parse_content = parse_content

        if parse_content:
            self.parse_issues()

    def add_issue(self, url=None, comment=None, author=None, issue=None, date=None):
        if issue is None:
            logger.info("New issue: {} - {}".format(author, url))
            self.issues.append(Issue(url=url, author=author, date=date, comment=comment))
        else:
            issue.info("New issue: {} - {} - {}".format(issue.author, issue.comment[:20], issue.url))
            self.issues.append(issue)

    def parse_issues(self):
        if len(self.issues) > 0:
            logger.error("There are already issues in here!")
            return

        if self.url is None:
            logger.error("Cannot parse {} - url is None".format(self.url))

        issue_site = send_request(self.url)
        pq = PyQuery(issue_site)

        # get number of issues

        header_count_text = pq("h3").eq(1)(".header-count").text()
        try:
            issue_amount = int(header_count_text)
        except ValueError:
            logger.warning("Cannot parse int from .header-count: {}".format(header_count_text))
            return

        if issue_amount == 0:
            logger.info("No open issues @ {} - header name: {}".format(self.url, pq("h3").eq(1).text()))
            return

        # Only get unhandled issues
        site_issues = pq(".list-group-issues").eq(0)

        for issue in site_issues.items(".list-group-contest-item"):
            creator = issue(".contest-item-author > a").text()
            issue_url = issue(".contest-item-num > a").attr("href")

            if issue_url is None:
                logger.error("issue_url is none for {}".format(self.url))
                continue
            date = issue(".contest-item-date").text()
            self.add_issue(author=creator, url="https://instantview.telegram.org{}".format(issue_url), date=date)

    def to_dict(self):
        return dict(creator=self.creator, url=self.url, issues=self.issues)

    @staticmethod
    def from_dict(template_dict):
        creator = template_dict.get("creator")
        url = template_dict.get("url")
        issues = template_dict.get("issues")
        template = Template(creator=creator, url=url, parse_content=False, issues=[])

        for issue in issues:
            issue_author = issue.get("author")
            issue_url = issue.get("url")
            issue_comment = issue.get("comment")
            issue_date = issue.get("date")

            template.add_issue(url=issue_url, author=issue_author, comment=issue_comment, date=issue_date)

        return template

    def __dict__(self):
        return self.to_dict()

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return "{} | {} | {}".format(self.creator, self.url, self.issues)
