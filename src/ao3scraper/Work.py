from typing import Optional
from bs4 import BeautifulSoup
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode


BASE_URL = "https://archiveofourown.com/works/{work_id}?view_adult=true"
KUDOS_URL = "https://archiveofourown.com/works/{work_id}/kudos?page={page}"
BOOKMARKS_URL = "https://archiveofourown.com/works/{work_id}/bookmarks?page={page}"
COMMENTS_URL = "https://archiveofourown.com/works/{work_id}/comments?page={page}"
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
# All the tags except language and stats are lists.
# The language tag is a scalar and stats tag is a dl
LIST_TAGS = [
    "rating",
    "warning",
    "category",
    "fandom",
    "relationship",
    "character",
    "freeform",
]
OTHER_TAGS = [
    "language",
    "stats",
    "published",
    "status",
    "words",
    "chapters",
    "comments",
    "kudos",
    "bookmarks",
    "hits",
]


class Work:
    def __init__(self, work_id: str, extras: bool = True):
        self.work_id = work_id
        self.extras = extras

        self.url = BASE_URL.format(work_id=self.work_id)

        self._scrape_page()
        self._parse_metadata()

    def _scrape_page(self):
        print("Scraping Main page...", end="")
        req = requests.get(self.url, headers=HEADERS)
        while req.status_code == 429:
            self.log.info("+")
            time.sleep(10)
            req = requests.get(self.url, headers=HEADERS)
        self.soup = BeautifulSoup(req.text, "lxml")
        print("Done")

    def _parse_metadata(self):
        self._parse_authors()
        self._parse_header()
        self._parse_stats()
        if self.extras:
            self._scrape_comments()
            self._scrape_bookmarks()
            self._scrape_kudos()

    def _parse_authors(self):
        print("Parsing author...", end="")
        self.authors = self.soup.find("h3", class_="byline heading").select(
            "a", rel="author"
        )
        self.authors = [author.contents[0] for author in self.authors]
        print("Done")

    def _parse_header(self):
        print("Parsing headers...", end="")
        self.metadata = self.soup.find("dl", class_="work meta group")
        self.tags = {
            tag: [
                subtags.contents[0].contents[0]
                for subtags in self.metadata.find("dd", class_=tag).find_all("li")
            ]
            for tag in LIST_TAGS
        }
        self.tags["language"] = (
            self.metadata.find("dd", class_="language").contents[0].strip()
        )
        print("Done")

    def _parse_stats(self):
        print("Parsing stats...", end="")
        self.stats = {
            stat["class"][0]: stat.contents[0]
            for stat in self.metadata.find("dd", class_="stats").find_all("dd")
        }
        self.stats["complete"] = (
            True
            if self.metadata.find("dd", class_="stats")
            .find_all("dt", class_="status")[0]
            .contents[0]
            .split(":")[0]
            == "Completed"
            else False
        )
        print("Done")

    def _scrape_comments(self):
        pass

    def _scrape_kudos(self, query_delay: int = 5):
        print("Scraping Kudos...|", end="")
        LastPage = False
        kudos_page = 1
        self.kudos = set()
        while not LastPage:
            time.sleep(query_delay)
            kudos, LastPage = self.__scrape_kudos_page(
                KUDOS_URL.format(work_id=self.work_id, page=kudos_page)
            )
            if kudos:
                self.kudos.update(kudos)
            else:
                print("Done")
                return
            kudos_page += 1

    def __scrape_kudos_page(
        self, kudos_url: str, error_delay_seconds: int = 10
    ) -> tuple[set[str] | None, bool]:
        req = requests.get(kudos_url, headers=HEADERS)

        while req.status_code == 429:
            self.log.info(
                f"\nRequest failed with status code 429. Retrying in {error_delay_seconds} seconds.\n"
            )
            time.sleep(error_delay_seconds)
            req = requests.get(kudos_url, headers=HEADERS)

        soup = BeautifulSoup(req.text, "lxml")
        kudos = soup.find("p", class_="kudos")
        if not kudos:
            return None, True
        print(".", end="")
        return set([kudo.contents[0] for kudo in kudos.find_all("a")]), False

    def _scrape_bookmarks(self, query_delay: int = 5):
        print("Scraping Bookmarks...|", end="")
        LastPage = False
        bookmarks_page = 1
        self.bookmarks = set()
        while not LastPage:
            time.sleep(query_delay)
            bookmarks, LastPage = self.__scrape_bookmarks_page(
                BOOKMARKS_URL.format(work_id=self.work_id, page=bookmarks_page)
            )
            if bookmarks:
                self.bookmarks.update(bookmarks)
            else:
                print("Done")
                return
            bookmarks_page += 1

    def __scrape_bookmarks_page(
        self, bookmarks_url, error_delay_seconds: int = 10
    ) -> tuple[set[tuple[str, str]] | None, bool]:
        req = requests.get(bookmarks_url, headers=HEADERS)

        while req.status_code == 429:
            self.log.info(
                f"\nRequest failed with status code 429. Retrying in {error_delay_seconds} seconds.\n"
            )
            time.sleep(error_delay_seconds)
            req = requests.get(bookmarks_url, headers=HEADERS)

        soup = BeautifulSoup(req.text, "lxml")
        bookmarks = soup.find("ol", class_="bookmark")

        if len(bookmarks) == 0:
            return None, True

        print(".", end="")
        return (
            set(
                [
                    (  # Bookmarker's ( user id, user name)
                        bookmark["class"][-1].split("-")[1],
                        bookmark.find("a", href=True)["href"].split("/")[2],
                    )
                    for bookmark in bookmarks.find_all("li", class_="user")
                ]
            ),
            False,
        )
