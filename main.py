# -*- coding: utf-8 -*-
import json
import logging
import os
from queue import Queue

from pyquery import PyQuery

from domain import Domain
from util import send_request, DataEncoder
from threadpool import Threadpool

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def download_issues():
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
            domain_name = row("div > a").text()

            if row(".status-winner") is None:
                logger.info("Domain {} already got a winner".format(domain_name))
                continue

            if not all(ord(c) < 128 for c in domain_name):
                logger.warning("{} - Non ascii domain found: {}".format(domain_counter, domain_name))
                domain_counter += 1
                continue

            logger.info("{} - New domain found: {}".format(domain_counter, domain_name))
            tp.start_thread(download_domain, name=str(domain_counter), domain_name=domain_name, domain_queue=domain_queue)
            # domains.append(Domain(domain_name, parse_content=True))

            domain_counter += 1
    except Exception:
        logger.error("An exception happened!")
        tp.kill()

    while not domain_queue.empty():
        domains.append(domain_queue.get())

    logger.info("Total number of {} domains found!".format(len(domains)))

    # Write the file to the disk
    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, "domains.json")
    with open(domains_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj=domains, cls=DataEncoder))


def download_domain(domain_name, domain_queue):
    domain = Domain(domain_name, parse_content=True)
    domain_queue.put(domain)


def search_saved_domains(search_word):
    current_path = os.path.dirname(os.path.abspath(__file__))
    domains_file = os.path.join(current_path, "domains.json")

    with open(domains_file, "r", encoding="utf-8") as f:
        content = f.read()
        content_json = json.loads(content)

    domains = []

    for domain in content_json:
        domain_o = Domain.from_dict(domain)
        domains.append(domain_o)

    print("-----------------------------------------------------------------------")

    for domain in domains:
        for template in domain.templates:
            for issue in template.issues:
                logger.info("{} | {} | {}".format(issue.url, domain.name, issue.comment))
                #if search_word in issue.comment:
                #    logger.info("{} | {} | {}".format(issue.url, domain.name, issue.comment))


if __name__ == "__main__":
    #download_issues()
    search_saved_domains("")
