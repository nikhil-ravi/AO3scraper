from glob import glob
import pandas as pd
from tqdm import tqdm
from ao3scraper import Work
import time

BASE_PATH = "./data/HP"


def main():
    files = glob(f"{BASE_PATH}/workids/HP_*.csv")
    for file in files[2:]:
        works = pd.read_csv(file, compression="gzip", header=None).rename(columns={0: "work_id"})
        year = file.split("_")[1].split(".")[0]
        results = []
        for work_id in tqdm(works.work_id, desc=f"{year=}"):
            try:
                result = vars(Work.WorkScraper(work_id=work_id).work)
            except Exception as e:
                with open(f"{BASE_PATH}/workinfo/log.txt", "a") as f:
                    f.write(f"{work_id} -- {e}")
                result = None
            if result:
                results.append(result)
            time.sleep(2)
        pd.DataFrame(results).to_parquet(f"{BASE_PATH}/workinfo/HP_{year}.parquet", compression="gzip")


if __name__ == "__main__":
    main()
