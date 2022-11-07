from pydantic.dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
import time
import requests


BASE_URL = "https://archiveofourown.com/works/{work_id}?view_adult=true"
KUDOS_URL = "https://archiveofourown.com/works/{work_id}/kudos?page={page}"
BOOKMARKS_URL = "https://archiveofourown.com/works/{work_id}/bookmarks?page={page}"
COMMENTS_URL = (
    "https://archiveofourown.com/works/{work_id}?view_adult=true&show_comments=true&view_full_work=true#comments"
)
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
STATS = [
    "published",
    "status",
    "complete",
    "words",
    "chapters_published",
    "chapters_expected",
    "comments",
    "kudos",
    "bookmarks",
    "hits",
]
CLASS_PROPERTIES = (
    [
        "title",
        "summary",
        "author",
        "language",
        "kudos_by",
        "bookmarks_by",
        "comments_by",
    ]
    + LIST_TAGS
    + STATS
)


@dataclass
class Work:
    id: int
    url: str
    title: str
    summary: str
    authors: list[str]
    language: str
    rating: str
    warning: list[str]
    category: list[str]
    fandom: list[str]
    relationship: list[str]
    character: list[str]
    freeform: list[str]
    published: datetime
    status: datetime
    complete: bool
    words: int
    chapters_published: int
    chapters_expected: None | int
    comments: int
    kudos: int
    bookmarks: int
    hits: int


class WorkScraper:
    def __init__(self, work_id: int):
        self.work_id = work_id
        self.url = BASE_URL.format(work_id=self.work_id)

        self._scrape_page()
        self._parse_metadata()

    def __eq__(self, __o: object) -> bool:
        return __o.work_id == self.work_id

    def _scrape_page(self):
        req = requests.get(self.url, headers=HEADERS)
        while req.status_code == 429:
            time.sleep(10)
            req = requests.get(self.url, headers=HEADERS)
        self.soup = BeautifulSoup(req.text, "lxml")

    def _parse_metadata(self):
        self._parse_title()
        self._parse_summary()
        self._parse_authors()
        self._parse_header()
        self._parse_stats()

    def _parse_title(self):
        title = self.soup.find("h2", class_="title heading")
        if title:
            self.title = title.contents[0].strip()
        else:
            self.title = ""

    def _parse_summary(self):
        summary = self.soup.find(class_="summary")
        if summary:
            self.summary = " ".join(summary.find("p").get_text(separator="|", strip=True).split("|"))
        else:
            self.summary = ""

    def _parse_authors(self):
        authors = self.soup.find("h3", class_="byline heading").select("a", rel="author", href=True)
        if authors:
            self.authors = [author.text for author in authors]
        else:
            self.authors = []

    def _parse_header(self):
        self.metadata = self.soup.find("dl", class_="work meta group")
        self.tags = {}
        for tag in LIST_TAGS:
            subtags = self.metadata.find("dd", class_=tag)
            if subtags:
                self.tags[tag] = [subtag.contents[0].contents[0] for subtag in subtags.find_all("li")]
            else:
                self.tags[tag] = []
        self.rating = self.tags["rating"][0]
        self.warning = self.tags["warning"]
        self.category = self.tags["category"]
        self.fandom = self.tags["fandom"]
        self.relationship = self.tags["relationship"]
        self.character = self.tags["character"]
        self.freeform = self.tags["freeform"]

        language = self.metadata.find("dd", class_="language")
        if language:
            self.tags["language"] = language.contents[0].strip()
        else:
            self.tags["language"] = ""
        self.language = self.tags["language"]

    def _parse_stats(self):
        self.stats = {
            stat["class"][0]: stat.contents[0] for stat in self.metadata.find("dd", class_="stats").find_all("dd")
        }
        for stat in ["published", "status"]:
            if stat in self.stats:
                self.stats[stat] = datetime.strptime(self.stats[stat].text, "%Y-%m-%d")
        if "status" in self.stats:
            if (
                self.metadata.find("dd", class_="stats").find_all("dt", class_="status")[0].contents[0].split(":")[0]
                == "Completed"
            ):
                self.stats["complete"] = True
            else:
                self.stats["complete"] = False
        else:
            self.stats["status"] = self.stats["published"]
            self.stats["complete"] = True
        self.stats["chapters_published"], self.stats["chapters_expected"] = self.stats["chapters"].split("/")
        for stat in ["words", "comments", "kudos", "hits", "chapters_published"]:
            if stat in self.stats:
                self.stats[stat] = int(self.stats[stat])
            else:
                self.stats[stat] = 0
        if "bookmarks" in self.stats:
            self.stats["bookmarks"] = int(self.stats["bookmarks"].contents[0])
        else:
            self.stats["bookmarks"] = 0
        self.stats["chapters_expected"] = (
            None if self.stats["chapters_expected"] == "?" else int(self.stats["chapters_expected"])
        )
        self.published = self.stats["published"]
        self.status = self.stats["status"]
        self.complete = self.stats["complete"]
        self.words = self.stats["words"]
        self.chapters = self.stats["chapters"]
        self.chapters_published = self.stats["chapters_published"]
        self.chapters_expected = self.stats["chapters_expected"]
        self.comments = self.stats["comments"]
        self.kudos = self.stats["kudos"]
        self.bookmarks = self.stats["bookmarks"]
        self.hits = self.stats["hits"]

    @property
    def work(self) -> Work:
        return Work(
            **{
                "id": self.work_id,
                "url": self.url,
                "title": self.title,
                "summary": self.summary,
                "language": self.language,
                "rating": self.rating,
                "published": self.published,
                "status": self.status,
                "complete": self.complete,
                "words": self.words,
                "chapters_published": self.chapters_published,
                "chapters_expected": self.chapters_expected,
                "comments": self.comments,
                "kudos": self.kudos,
                "bookmarks": self.bookmarks,
                "hits": self.hits,
                "authors": self.authors,
                "warning": self.warning,
                "category": self.category,
                "fandom": self.fandom,
                "relationship": self.relationship,
                "character": self.character,
                "freeform": self.freeform,
            }
        )


@dataclass
class Comments:
    work_id: int
    comments: list


class CommentsScraper:
    def __init__(self, work_id: int):
        self.work_id = work_id
        self._scrape_comments()

    def _scrape_comments(self):
        # //TODO: Get list of comments left
        self.comments_list = []

    @property
    def comments(self) -> Comments:
        return Comments(**{"work_id": self.work_id, "comments": self.comments_list})


@dataclass
class Bookmarks:
    work_id: int
    bookmarks: set[tuple[int, str]]


class BookmarksScraper:
    def __init__(self, work_id: int):
        self.work_id = work_id
        self._scrape_bookmarks()

    def _scrape_bookmarks(self, query_delay: int = 5):
        LastPage = False
        bookmarks_page = 1
        self.bookmarks_list = set()
        while not LastPage:
            time.sleep(query_delay)
            bookmarks, LastPage = self.__scrape_bookmarks_page(
                BOOKMARKS_URL.format(work_id=self.work_id, page=bookmarks_page)
            )
            if bookmarks:
                self.bookmarks_list.update(bookmarks)
            else:
                return
            bookmarks_page += 1

    def __scrape_bookmarks_page(
        self, bookmarks_url, error_delay_seconds: int = 10
    ) -> tuple[set[tuple[str, str]] | None, bool]:
        req = requests.get(bookmarks_url, headers=HEADERS)

        while req.status_code == 429:
            time.sleep(error_delay_seconds)
            req = requests.get(bookmarks_url, headers=HEADERS)

        soup = BeautifulSoup(req.text, "lxml")
        bookmarks = soup.find("ol", class_="bookmark")

        if len(bookmarks) == 0:
            return None, True

        return (
            set(
                [
                    (  # Bookmarker's ( user id, user name)
                        int(bookmark["class"][-1].split("-")[1]),
                        bookmark.find("a", href=True)["href"].split("/")[2],
                    )
                    for bookmark in bookmarks.find_all("li", class_="user")
                ]
            ),
            False,
        )

    @property
    def bookmarks(self) -> Comments:
        return Bookmarks(**{"work_id": self.work_id, "bookmarks": self.bookmarks_list})


@dataclass
class Kudos:
    work_id: int
    kudos: set[str]


class KudosScraper:
    def __init__(self, work_id: int):
        self.work_id = work_id
        self._scrape_kudos()

    def _scrape_kudos(self, query_delay: int = 5):
        LastPage = False
        kudos_page = 1
        self.kudos_list = set()
        while not LastPage:
            time.sleep(query_delay)
            kudos, LastPage = self.__scrape_kudos_page(KUDOS_URL.format(work_id=self.work_id, page=kudos_page))
            if kudos:
                self.kudos_list.update(kudos)
            else:
                return
            kudos_page += 1

    def __scrape_kudos_page(self, kudos_url: str, error_delay_seconds: int = 10) -> tuple[set[str] | None, bool]:
        req = requests.get(kudos_url, headers=HEADERS)

        while req.status_code == 429:
            time.sleep(error_delay_seconds)
            req = requests.get(kudos_url, headers=HEADERS)

        soup = BeautifulSoup(req.text, "lxml")
        kudos = soup.find("p", class_="kudos")
        if not kudos:
            return None, True
        return set([kudo.contents[0] for kudo in kudos.find_all("a")]), False

    @property
    def kudos(self) -> Comments:
        return Kudos(**{"work_id": self.work_id, "kudos": self.kudos_list})
