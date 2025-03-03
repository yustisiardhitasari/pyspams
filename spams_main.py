import argparse
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spamsx_fp",
        "-s",
        default="data/spams/nl_krimpenerwaard_spamsx.parquet",
        help="SPAMS parameters file path",
    )
    parser.add_argument(
        "--meteo_dir", "-m", default="data/knmi/", help="KNMI files directory",
    )
    parser.add_argument(
        "--start_date",
        "-sd",
        default=20230101,
        help="Start date when computing the SPAMS model",
    )
    parser.add_argument(
        "--end_date",
        "-ed",
        default=20231231,
        help="End date when computing the SPAMS model",
    )

    args = parser.parse_args()

    ## Load SPAMS parameters
    df_spams = pd.read_parquet(args.spamsx_fp)
    pnt_ids = df_spams["pnt_id"].unique()

    ## Load KNMI data
    filelist = sorted(Path(args.meteo_dir).glob("**/etmgeg_*.txt"))
    f1 = [None] * len(filelist)
    for i, file in enumerate(filelist):
        f1[i] = utils.read_knmi(file)
    df_knmi = pd.concat(f1)

    ## Compute time series
    start = pd.to_datetime(datetime.strptime(str(args.start_date), "%Y%m%d"))
    end = pd.to_datetime(datetime.strptime(str(args.end_date), "%Y%m%d"))
    epoch = pd.date_range(start=start, end=end)

    f1 = [None] * pnt_ids.size
    for i, spams in df_spams.iterrows():
        ## Point ID and KNMI ID
        pid = spams["pnt_id"]
        knmi_id = spams["knmi_id"]

        ## Model parameters
        xP = spams["xP"]
        xE = spams["xE"]
        xI = spams["xI"]
        t = int(spams["tau"])

        ## Create a subset from knmi dataframe based on station id and duration
        knmi_subset = df_knmi.loc[
            (df_knmi["knmi_id"] == knmi_id)
            & (df_knmi["datum"] > (start - timedelta(days=t)))
            & (df_knmi["datum"] <= end)
        ].reset_index(drop=True)

        ## Compute SPAMS model
        reversible, irreversible, height = utils.spams_model(xP, xE, xI, t, knmi_subset)

        ## Store it as pd.DataFrame
        f1[i] = pd.DataFrame(
            data={
                "pnt_id": pid,
                "epoch": epoch,
                "reversible": reversible,
                "irreversible": irreversible,
                "height": height,
            }
        )

    df_ts_spams = pd.concat(f1)

    ## Create an example plot for a random parcel
    pid = np.random.choice(pnt_ids)
    ts = df_ts_spams[df_ts_spams["pnt_id"]==pid]
    plt.figure(figsize=(12, 6))
    plt.title("Parcel #{}".format(pid))
    plt.plot(ts["epoch"], ts["height"], "-m", markersize=2, label="Total")
    plt.plot(ts["epoch"], ts["reversible"], "--C7", markersize=2, label="Reversible")
    plt.plot(ts["epoch"], ts["irreversible"], "--C7", linewidth=2, label="Irreversible")
    plt.legend(loc="upper right")
    plt.ylabel("Relative height (mm)")
    plt.grid(linestyle="--", alpha=0.5)
    plt.show()


if __name__ == "__main__":
    main()
