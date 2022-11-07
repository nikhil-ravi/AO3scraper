from glob import glob
import pandas as pd


def main():
    years = glob("./data/HP_*.csv")
    pd.concat(
        [
            pd.read_csv(year, header=None, compression="gzip")
            .rename(columns={0: "id"})
            .assign(year=int(year.split("_")[1].split(".")[0]))
            for year in years
        ],
        ignore_index=True,
        axis=0,
    ).to_csv("./data/HP.csv.gzip", index=False, compression="gzip")


if __name__ == "__main__":
    main()
