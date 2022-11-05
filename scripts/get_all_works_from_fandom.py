from AO3 import FandomWorks
from urllib.parse import urlparse, parse_qs, urlencode
from tqdm import tqdm

def main():
    url = "https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works"
    headers = {
    'User-Agent': 'Mozilla/6.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'refere': 'https://example.com',
    'cookie': """your cookie value ( you can get that from your web page) """
    }
    years = list(range(1999, 2023))
    for year in tqdm(years):
        parts = urlparse(url)
        query_dict = parse_qs(parts.query, keep_blank_values=True)
        query_dict["page"] = ["1"]
        query_dict['work_search[date_from]'] = [f"{year}-01-01"]
        query_dict['work_search[date_to]'] = [f"{year}-12-31"]
        current_url = parts._replace(query=urlencode(query_dict, True)).geturl()
        works = FandomWorks(base_url=current_url, headers=headers)
        works.set_list_of_works()
        works.save_list_of_works(filename=f"./data/HP_{year}.csv")

if __name__ == '__main__':
    main()