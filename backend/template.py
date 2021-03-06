# -*- coding: utf-8 -*-
import json
import logging

from pyquery import PyQuery

from backend.issue import Issue, IssueType
from backend.util import send_request

logger = logging.getLogger(__name__)


class Template(object):

    def __init__(self, creator, url, parse_content, issues=None, unprocessed_issues=None, accepted_issues=None, declined_issues=None, domain=None, only_unprocessed=True):
        self.creator = creator
        self.url = url
        self.issues = issues or []
        self.unprocessed_issues = unprocessed_issues or []
        self.accepted_issues = accepted_issues or []
        self.declined_issues = declined_issues or []
        self.parse_content = parse_content
        self.domain = domain
        self.only_unprocessed = only_unprocessed

        if parse_content:
            self.parse_issues()

    @property
    def all_issues(self):
        return self.issues + self.unprocessed_issues + self.accepted_issues + self.declined_issues

    def add_issue(self, url=None, comment=None, author=None, issue=None, date=None, creator_comment=None, template_creator=None, self_made=False, domain=None, status=None):
        if issue is None:
            logger.info("New issue: {} - {}".format(author, url))
            issue_o = Issue(url=url,
                            author=author,
                            date=date,
                            comment=comment,
                            creator_comment=creator_comment,
                            template_creator=template_creator or self.creator,
                            self_made=self_made,
                            domain=domain,
                            status=status)
        else:
            issue.info("New issue: {} - {} - {}".format(issue.author, issue.comment[:20], issue.url))
            issue_o = issue

        if status == IssueType.UNPROCESSED:
            self.unprocessed_issues.append(issue_o)
        elif status == IssueType.ACCEPTED:
            self.accepted_issues.append(issue_o)
        elif status == IssueType.DECLINED:
            self.declined_issues.append(issue_o)

    def parse_issues(self):
        if len(self.issues) > 0 or len(self.accepted_issues) > 0 or len(self.declined_issues) > 0 or len(self.unprocessed_issues) > 0:
            logger.error("There are already issues in here!")
            return

        if self.url is None:
            logger.error("Cannot parse {} - url is None".format(self.domain))

        issue_site = send_request(self.url)
        if issue_site == "":
            logger.warning("Empty site {}".format(self.url))
            return

        pq = PyQuery(issue_site)

        # get the first header of the site
        unhandled_issue_header = pq("h3").not_(".accepted").not_(".declined").eq(1)
        accepted_issue_header = pq("h3.accepted").eq(0)
        third_issue_header = pq("h3.declined").eq(0)

        headers = [unhandled_issue_header, accepted_issue_header, third_issue_header]

        # Iterate over all the headers ("reported", "accepted", "declined") and select the issues from them
        for issue_header in headers:
            # Skip non existent headers
            if len(issue_header) == 0:
                logger.debug("Ignoring empty header")
                continue

            status = IssueType.UNPROCESSED

            if self.only_unprocessed:
                # if the header contains "accepted" or "declined" issues, ignore the issues - we only want unprocessed issues
                if len(issue_header(".accepted")) != 0 or len(issue_header(".declined")) != 0 or issue_header.text().lower() == "accepted issues" or issue_header.text().lower() == "declined issues":
                    logger.debug("Issue already processed for template '{}'".format(self.url))
                    continue
            else:
                # Also parse accepted & declined issues
                if len(issue_header(".accepted")) != 0 or issue_header.text().lower() == "accepted issues":
                    status = IssueType.ACCEPTED
                elif len(issue_header(".declined")) != 0 or issue_header.text().lower() == "declined issues":
                    status = IssueType.DECLINED
                else:
                    status = IssueType.UNPROCESSED

            # Get the issue count
            issue_header_count = issue_header(".header-count")

            # If the count does not exist, there are no issues on that domain
            if len(issue_header_count) == 0:
                logger.debug("No issues for template {}".format(self.url))
                continue

            header_count_text = issue_header_count.text()
            try:
                issue_amount = int(header_count_text)
            except ValueError:
                logger.warning("Cannot parse int from .header-count: {} - '{}'".format(self.url, header_count_text))
                return

            if issue_amount == 0:
                logger.debug("No open issues @ {} - header name: {}".format(self.url, pq("h3").eq(1).text()))
                continue

            # Only get all issues following that header
            site_issues = issue_header.next_all(".list-group-issues").eq(0)

            if len(site_issues) == 0:
                logger.debug("No issues found!")
                continue

            for issue in site_issues.items(".list-group-contest-item"):
                creator = issue(".contest-item-author > a").text()
                issue_url = issue(".contest-item-num > a").attr("href")

                if issue_url is None:
                    logger.error("issue_url is none for {}".format(self.url))
                    continue
                date = issue(".contest-item-date").text()
                self.add_issue(author=creator, url="https://instantview.telegram.org{}".format(issue_url), date=date, domain=self.domain, status=status)

    def to_dict(self):
        return dict(creator=self.creator, url=self.url, issues=self.issues, unprocessed_issues=self.unprocessed_issues, accepted_issues=self.accepted_issues, declined_issues=self.declined_issues)

    @staticmethod
    def from_dict(template_dict):
        creator = template_dict.get("creator")
        url = template_dict.get("url")
        issues = template_dict.get("issues")
        unprocessed_issues = template_dict.get("unprocessed_issues")
        accepted_issues = template_dict.get("accepted_issues")
        declined_issues = template_dict.get("declined_issues")
        domain = template_dict.get("domain")
        template = Template(creator=creator, url=url, parse_content=False, domain=domain)
        all_issues = issues + unprocessed_issues + accepted_issues + declined_issues

        for issue in all_issues:
            issue_author = issue.get("author")
            issue_url = issue.get("url")
            issue_comment = issue.get("comment")
            issue_date = issue.get("date")
            creator_comment = issue.get("creator_comment")
            template_creator = issue.get("template_creator")
            self_made = issue.get("self_made")
            domain = issue.get("domain")
            status = IssueType(int(issue.get("status")))

            template.add_issue(url=issue_url,
                               author=issue_author,
                               comment=issue_comment,
                               date=issue_date,
                               creator_comment=creator_comment,
                               template_creator=template_creator or creator,
                               self_made=self_made,
                               domain=domain,
                               status=status)

        return template

    def __dict__(self):
        return self.to_dict()

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return "{} | {} | {}".format(self.creator, self.url, self.all_issues)
