# -*- coding: utf-8 -*-
import json
import logging
import os
from queue import Queue

from pyquery import PyQuery

from domain import Domain
from threadpool import Threadpool
from util import send_request, DataEncoder

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def download_issues(filename="domains.json", skip=0, only_active=False):
    """Downloads all the issues of the available domains"""
    domains = []
    main_html = send_request("https://instantview.telegram.org/contest")
    pq = PyQuery(main_html)

    tp = Threadpool(4)

    # Fetch all the domain rows
    rows = pq(".list-group-contest-rows")
    domain_counter = 1

    domain_queue = Queue()

    try:
        # Iterate over the rows to get the domains
        for row in rows.items(".list-group-contest-item"):
            # If the user wants to skip certain domains,
            if domain_counter < skip:
                domain_counter += 1
                continue

            domain_name = row("div > a").text()

            if row(".status-winner") is None:
                logger.info("Domain {} already got a winner".format(domain_name))
                continue

            if not all(ord(c) < 128 for c in domain_name):
                logger.warning("{} - Non ascii domain found: {}".format(domain_counter, domain_name))
                domain_counter += 1
                continue

            logger.info("{} - New domain found: {}".format(domain_counter, domain_name))
            tp.start_thread(download_domain, name=str(domain_counter), domain_name=domain_name, domain_queue=domain_queue, only_active=only_active)

            domain_counter += 1
    except Exception:
        logger.error("An exception happened!")
        tp.kill()

    while not domain_queue.empty():
        domains.append(domain_queue.get())

    logger.info("Total number of {} domains found!".format(len(domains)))

    # Write the file to the disk
    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, filename)

    with open(domains_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj=domains, cls=DataEncoder))


def download_domain(domain_name, domain_queue, only_active):
    """Downloads all the templates and issues related to one domain"""
    domain = Domain(domain_name, parse_content=True, only_active=only_active)
    domain_queue.put(domain)


def load_from_json(filename="domains.json"):
    """Load data from a json file"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, filename)

    with open(domains_file, "r", encoding="utf-8") as f:
        content = f.read()
        content_json = json.loads(content)

    domains = []

    for domain in content_json:
        domain_o = Domain.from_dict(domain)
        domains.append(domain_o)

    return domains


def search_saved_domains(search_word, filename="domains.json"):
    """Search domains/issues for certain words and print them"""
    domains = load_from_json(filename)

    for domain in domains:
        for template in domain.templates:
            for issue in template.issues:
                if search_word in issue.comment:
                    logger.info("{} | {} | {}".format(issue.url, domain.name, issue.comment))


def save_csv_file(file, csv_domains, headers=True):
    logger.info("Trying to save file as '{}'".format(file))
    with open(file, "w", encoding="utf-8") as f:
        if headers:
            header = "Domain;Template Creator;Issue Author;URL;Issue Author Comment;Template Creator Comment;\n"
        else:
            header = ""

        f.write(header + "\n".join(str(line) for line in csv_domains))


def to_csv(filename="domains.csv", domain_file="domains.json", headers=True):
    """Save domains to csv file"""
    domains = load_from_json(filename=domain_file)
    csv_domains = []

    for domain in domains:
        for template in domain.templates:
            for issue in template.issues:
                # tmp_str = "{};{};{};=HYPERLINK(\"{}\");\"{}\";".format(domain.name, issue.author.replace(";", ""), issue.url, issue.url, issue.comment.replace("\n", " ").replace("\"", "'"))
                tmp_str = "{};{};{};{};\"{}\";\"{}\";".format(domain.name,
                                                              template.creator.replace(";", ""),
                                                              issue.author.replace(";", ""),
                                                              issue.url,
                                                              issue.comment.replace("\n", " ").replace("\"", "'"),
                                                              issue.creator_comment.replace("\n", " ").replace("\"", "'"))
                csv_domains.append(tmp_str)

    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, filename)

    counter = 0
    while True:
        try:
            if counter == 0:
                file = domains_file
            else:
                file = os.path.join(str(counter) + current_path, filename)

            save_csv_file(file, csv_domains, headers)
            logger.info("Storing successful")
            break
        except PermissionError as e:
            counter += 1
            logger.error(e)


if __name__ == "__main__":
    download_issues(filename="all_domains.json", only_active=False)
    # search_saved_domains("missing")
    to_csv(filename="all_domains.csv", domain_file="all_domains.json")
