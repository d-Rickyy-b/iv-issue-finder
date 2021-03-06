# -*- coding: utf-8 -*-
import json
import logging

from pyquery import PyQuery

from backend.template import Template
from backend.util import send_request

logger = logging.getLogger(__name__)


class Domain(object):

    def __init__(self, name, parse_content=False, only_active=True, only_unprocessed=True):
        self.name = name
        self.url = "https://instantview.telegram.org/contest/{}/".format(name)
        self.templates = []
        self.parse_content = parse_content
        self.only_active = only_active
        self.only_unprocessed = only_unprocessed

        if parse_content:
            self.parse_templates()

    def add_template(self, creator=None, url=None, template=None):
        if template is None:
            logger.info("New template: {} - {}".format(creator, url))
            self.templates.append(Template(creator=creator, url=url, parse_content=self.parse_content, domain=self.name, only_unprocessed=self.only_unprocessed))
        else:
            logger.info("New template: {} - {}".format(template.creator, template.url))
            self.templates.append(template)

    def parse_templates(self):
        if len(self.templates) > 0:
            logger.error("There are already templates in here!")
            return

        domain_site = send_request(self.url)
        pq = PyQuery(domain_site)

        # Only get active templates
        if self.only_active:
            site_templates = pq(".list-group-contest").eq(0)
        else:
            # Otherwise parse rejected templates as well
            site_templates = pq(".list-group-contest")

        for template in site_templates.items(".list-group-contest-item"):
            creator = template(".contest-item-author > a").text()
            template_url = template(".contest-item-num > a").attr("href")
            self.add_template(creator, "https://instantview.telegram.org{}".format(template_url))

    def to_dict(self):
        return dict(name=self.name, url=self.url, templates=self.templates)

    @staticmethod
    def from_dict(domain_dict):
        name = domain_dict.get("name")
        url = domain_dict.get("url")
        domain = Domain(name, parse_content=False)
        templates = domain_dict.get("templates")

        for template in templates:
            template_o = Template.from_dict(template)
            domain.add_template(template=template_o)

        return domain

    def to_json(self):
        return json.dumps(self.to_dict())

    def __dict__(self):
        return self.to_dict()
