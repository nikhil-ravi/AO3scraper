from ao3scraper.Fandom import FandomWorks
from urllib.parse import urlparse, parse_qs, urlencode
from tqdm import tqdm


def main():
    url = "https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works"
    years = list(range(2013, 2023))
    for year in tqdm(years):
        parts = urlparse(url)
        query_dict = parse_qs(parts.query, keep_blank_values=True)
        query_dict["page"] = ["1"]
        query_dict["work_search[date_from]"] = [f"{year}-01-01"]
        query_dict["work_search[date_to]"] = [f"{year}-12-31"]
        current_url = parts._replace(query=urlencode(query_dict, True)).geturl()
        works = FandomWorks(base_url=current_url)
        works.set_list_of_works()
        works.save_list_of_works(filename=f"./data/HP_{year}.csv")


if __name__ == "__main__":
    main()
