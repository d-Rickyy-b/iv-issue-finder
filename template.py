# -*- coding: utf-8 -*-
import json
import logging

from pyquery import PyQuery

from issue import Issue
from util import send_request

logger = logging.getLogger(__name__)


class Template(object):

    def __init__(self, creator, url, parse_content, issues=None, domain=None):
        self.creator = creator
        self.url = url
        self.issues = issues or []
        self.parse_content = parse_content
        self.domain = domain

        if parse_content:
            self.parse_issues()

    def add_issue(self, url=None, comment=None, author=None, issue=None, date=None, creator_comment=None, template_creator=None, self_made=False, domain=None):
        if issue is None:
            logger.info("New issue: {} - {}".format(author, url))
            self.issues.append(Issue(url=url, author=author, date=date, comment=comment, creator_comment=creator_comment, template_creator=template_creator or self.creator, self_made=self_made, domain=domain))
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
        if issue_site == "":
            logger.warning("Empty site {}".format(self.url))
            return

        pq = PyQuery(issue_site)

        # get the first header of the site
        issue_header = pq("h3").eq(1)

        # if the header contains "accepted" or "declined" issues, ignore the issues - we only want unprocessed issues
        if len(issue_header(".accepted")) != 0 or len(issue_header(".declined")) != 0 or issue_header.text().lower() == "accepted issues" or issue_header.text().lower() == "declined issues":
            return

        # Get the issue count
        issue_header_count = issue_header(".header-count")

        # If the count does not exist, there are no issues on that domain
        if len(issue_header_count) == 0:
            logger.debug("No issues for template {}".format(self.url))
            return

        header_count_text = issue_header_count.text()
        try:
            issue_amount = int(header_count_text)
        except ValueError:
            logger.warning("Cannot parse int from .header-count: {} - '{}'".format(self.url, header_count_text))
            return

        if issue_amount == 0:
            logger.debug("No open issues @ {} - header name: {}".format(self.url, pq("h3").eq(1).text()))
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
            self.add_issue(author=creator, url="https://instantview.telegram.org{}".format(issue_url), date=date, domain=self.domain)

    def to_dict(self):
        return dict(creator=self.creator, url=self.url, issues=self.issues)

    @staticmethod
    def from_dict(template_dict):
        creator = template_dict.get("creator")
        url = template_dict.get("url")
        issues = template_dict.get("issues")
        domain = template_dict.get("domain")
        template = Template(creator=creator, url=url, parse_content=False, issues=[], domain=domain)

        for issue in issues:
            issue_author = issue.get("author")
            issue_url = issue.get("url")
            issue_comment = issue.get("comment")
            issue_date = issue.get("date")
            creator_comment = issue.get("creator_comment")
            template_creator = issue.get("template_creator")
            self_made = issue.get("self_made")
            domain = issue.get("domain")

            template.add_issue(url=issue_url, author=issue_author, comment=issue_comment, date=issue_date, creator_comment=creator_comment, template_creator=template_creator or creator, self_made=self_made, domain=domain)

        return template

    def __dict__(self):
        return self.to_dict()

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return "{} | {} | {}".format(self.creator, self.url, self.issues)
