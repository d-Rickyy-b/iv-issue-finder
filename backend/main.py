# -*- coding: utf-8 -*-
import json
import logging
import os
import time
from queue import Queue

from pyquery import PyQuery

from backend.domain import Domain
from backend.threadpool import Threadpool
from backend.util import send_request, DataEncoder

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def download_issues(filename="domains.json", skip=0, only_active=False, only_without_winner=True, only_unprocessed=True):
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

            # Switch to decide if all domains or only those without a winner should get scraped
            if only_without_winner:
                # Only scrape domains which do not yet have a winner
                if row(".status-winner") is not None and row(".status-winner").text() == "Winner '19":
                    logger.debug("Domain {} already got a winner".format(domain_name))
                    continue

            # Ignore non-ascii domains for now
            if not all(ord(c) < 128 for c in domain_name):
                logger.warning("{} - Non ascii domain found: {}".format(domain_counter, domain_name))
                domain_counter += 1
                continue

            logger.info("{} - New domain found: {}".format(domain_counter, domain_name))
            tp.start_thread(download_domain, name=str(domain_counter), domain_name=domain_name, domain_queue=domain_queue, only_active=only_active, only_unprocessed=only_unprocessed)

            domain_counter += 1
    except Exception:
        logger.error("An exception happened!")
        tp.kill()

    # Wait until all the threads are finished
    tp._join_threads()

    while not domain_queue.empty():
        domains.append(domain_queue.get())

    logger.info("Total number of {} domains found!".format(len(domains)))

    # Write the file to the disk
    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, filename)

    with open(domains_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj=domains, cls=DataEncoder))


def download_domain(domain_name, domain_queue, only_active, only_unprocessed):
    """Downloads all the templates and issues related to one domain"""
    domain = Domain(domain_name, parse_content=True, only_active=only_active, only_unprocessed=only_unprocessed)
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
            for issue in template.all_issues:
                if search_word in issue.comment:
                    logger.info("{} | {} | {}".format(issue.url, domain.name, issue.comment))


def save_csv_file(file, csv_domains, headers=True):
    """Store all the issues in a csv file"""
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
            for issue in template.all_issues:
                tmp_str = "{};{};{};{};\"{}\";\"{}\";{};".format(domain.name,
                                                                 template.creator.replace(";", ""),
                                                                 issue.author.replace(";", ""),
                                                                 issue.url,
                                                                 issue.comment.replace("\n", " ").replace("\"", "'"),
                                                                 issue.creator_comment.replace("\n", " ").replace("\"", "'"),
                                                                 issue.status.value)
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


def to_issue_json(filename="issues.json", domain_file="domains.json", separate_issues=False):
    """Store all issues as a json file"""
    domains = load_from_json(filename=domain_file)
    all_issues = []
    accepted_issues = []
    declined_issues = []
    unprocessed_issues = []

    if separate_issues:
        for domain in domains:
            for template in domain.templates:
                all_issues += template.all_issues
                accepted_issues += template.accepted_issues
                declined_issues += template.declined_issues
                unprocessed_issues += template.unprocessed_issues

        date = int(time.time())
        path, ending = filename.split(".")
        issue_objs = list()
        issue_objs.append(dict(filename=path + "_all." + ending, obj=dict(date=date, issues=all_issues)))
        issue_objs.append(dict(filename=path + "_accepted." + ending, obj=dict(date=date, issues=accepted_issues)))
        issue_objs.append(dict(filename=path + "_declined." + ending, obj=dict(date=date, issues=declined_issues)))
        issue_objs.append(dict(filename=path + "_unhandled." + ending, obj=dict(date=date, issues=unprocessed_issues)))

        for issue_obj in issue_objs:
            with open(issue_obj.get("filename"), "w", encoding="utf-8") as f:
                f.write(json.dumps(obj=issue_obj.get("obj"), cls=DataEncoder))
    else:
        for domain in domains:
            for template in domain.templates:
                all_issues += template.all_issues

        date = int(time.time())
        issue_obj = dict(date=date, issues=all_issues)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(obj=issue_obj, cls=DataEncoder))


def count_domain_issues(domain_file="domains.json"):
    """Counts the amount of issues per domain"""
    domains = load_from_json(filename=domain_file)
    issues = []
    domain_issues = []

    for domain in domains:
        domain_issue_counter = 0
        for template in domain.templates:
            template_issue_counter = 0
            for issue in template.all_issues:
                template_issue_counter += 1
                issues.append(issue)
            domain_issue_counter += template_issue_counter

        if domain_issue_counter > 0:
            domain_issues.append([domain.name, domain_issue_counter])

    domain_issues = sorted(domain_issues, key=lambda x: x[1], reverse=True)
    from pprint import pprint
    pprint(domain_issues)


if __name__ == "__main__":
    # Download all issues
    #download_issues(filename="domains.json", only_active=False, only_unprocessed=False)
    # Download only currently open issues
    download_issues(filename="domains.json", only_active=True, only_unprocessed=True)
    # search_saved_domains("missing")
    to_csv(filename="domains.csv", domain_file="domains.json")
    to_issue_json(filename="issues.json", domain_file="domains.json", separate_issues=False)
    count_domain_issues()
