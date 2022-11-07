import pandas as pd
from tqdm import tqdm
from ao3scraper import Work
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--files", type=str, nargs="+")
parser.add_argument("--output", type=str)


def main():
    args = parser.parse_args()
    for file in args.files:
        works = pd.read_csv(file, compression="gzip", header=None).rename(
            columns={0: "work_id"}
        )
        year = file.split("_")[1].split(".")[0]
        results = []
        progress = tqdm(works.work_id, desc=f"{year=}")
        for work_id in progress:
            progress.set_postfix_str(work_id)
            try:
                result = vars(Work.WorkScraper(work_id=work_id).work)
            except Exception as e:
                with open(f"{args.output}/log.txt", "a") as f:
                    f.write(f"{work_id} -- {e}\n")
                result = None
            if result:
                results.append(result)
            time.sleep(2)
        pd.DataFrame(results).to_parquet(
            f"{args.output}/HP_{year}.parquet", compression="gzip"
        )


if __name__ == "__main__":
    main()
