from glob import glob
import pandas as pd
from tqdm import tqdm
from ao3scraper import Work
import time


def read_year(file):
    return pd.read_csv(file, compression="gzip", header=None).rename(columns={0: "work_id"})


def process_work(work_id):
    return vars(Work.WorkScraper(work_id=work_id).work)


def main():
    files = glob("./data/HP/workids/HP_*.csv")
    for file in tqdm(files[:3]):
        works = read_year(file)
        results = []
        for work_id in works.work_id:
            results.append(process_work(work_id))
            time.sleep(2)
        pd.DataFrame(results).to_parquet(
            f"./data/HP/workinfo/HP_{file.split('_')[1].split('.')[0]}.parquet", compression="gzip"
        )


if __name__ == "__main__":
    main()
