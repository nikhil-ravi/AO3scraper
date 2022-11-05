from typing import Optional
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import logging
import sys
from urllib.parse import urlparse, parse_qs, urlencode

HEADERS = {
    "User-Agent": "Mozilla/6.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
    "refere": "https://example.com",
    "cookie": """your cookie value ( you can get that from your web page) """,
}


class FandomWorks:
    def __init__(
        self,
        base_url: str,
        existing_list: Optional[str | set] = None,
        is_verbose: bool = False,
    ):
        self.base_url = base_url
        self.existing_list = existing_list
        self.process_existing_list()
        self.is_verbose = is_verbose
        self.configure_logger()
        self.page = 1

    def configure_logger(self):
        # configuring log
        if self.is_verbose:
            self.log_level = logging.DEBUG
        else:
            self.log_level = logging.INFO
        log_format = logging.Formatter("%(message)s")
        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.log_level)

        # writing to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.terminator = ""
        handler.setLevel(self.log_level)
        handler.setFormatter(log_format)
        self.log.addHandler(handler)

        # here
        self.log.debug("test")

    def process_existing_list(self):
        if self.existing_list and isinstance(self.existing_list, str):
            self.existing_list = set(
                pd.read_csv(self.existing_list, header=None, dtype=str, compression="gzip")[0].to_list()
            )
        elif self.existing_list and isinstance(self.existing_list, list):
            self.existing_list = set(self.existing_list)
        elif self.existing_list == None:
            self.existing_list = set()

    def set_next_page(self):
        parts = urlparse(self.base_url)
        query_dict = parse_qs(parts.query, keep_blank_values=True)
        query_dict["page"] = [f"{self.page}"]
        self.current_url = parts._replace(query=urlencode(query_dict, True)).geturl()
        self.page += 1

    def get_list_of_works(self):
        return self.existing_list

    def save_list_of_works(self, filename: str):
        pd.DataFrame(self.existing_list).to_csv(filename, index=False, header=False, compression="gzip")

    def set_list_of_works(self, query_delay: int = 5, filename: str = None):
        LastPage = False
        while not LastPage:
            time.sleep(query_delay)
            self.set_next_page()
            work_ids, info = self.scrape_page(self.current_url)
            LastPage = info["LastPage"]
            if work_ids:
                self.existing_list.update(work_ids)
            if filename:
                self.save_list_of_works(filename)
            self.log.info(".")

    def scrape_page(self, url, error_delay_seconds: int = 10):
        text = requests.get(url, headers=HEADERS)

        while text.status_code == 429:
            self.log.info("+")
            time.sleep(error_delay_seconds)
            text = requests.get(url, headers=HEADERS)

        soup = BeautifulSoup(text.text, "lxml")
        works = soup.select("li.work.blurb.group")
        if len(works) == 0:
            return None, {"LastPage": True}

        # Work id are of the form "work_123456789"
        return [work.get("id").split("_")[1] for work in works], {"LastPage": False}
