import argparse
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spamsx_filepath",
        "-spamsx_fp",
        default="data/nl_krimpenerwaard_spamsx.parquet",
        help="str, path to the SPAMS parameters file",
    )
    parser.add_argument(
        "--meteo_filepath",
        "-meteo_fp",
        default="data/etmgeg_344.txt",
        help="str, path to the meteo file",
    )
    parser.add_argument(
        "--start_date",
        "-sdate",
        default=20230101,
        help="int, start date when computing the SPAMS model",
    )
    parser.add_argument(
        "--end_date",
        "-edate",
        default=20231231,
        help="int, end date when computing the SPAMS model",
    )

    args = parser.parse_args()

    ## Load SPAMS parameters
    df_spams = pd.read_parquet(args.spamsx_filepath)
    pnt_ids = df_spams["pnt_id"].unique()

    ## Load meteo data
    df_meteo = utils.read_knmi(args.meteo_filepath)

    ## Time series dates
    start = pd.to_datetime(datetime.strptime(str(args.start_date), "%Y%m%d"))
    end = pd.to_datetime(datetime.strptime(str(args.end_date), "%Y%m%d"))
    epoch = pd.date_range(start=start, end=end)

    ## Select random point
    pid = np.random.choice(pnt_ids)

    ## SPAMS model parameters
    xP = df_spams[df_spams["pnt_id"] == pid]["xP"].values[0]
    xE = df_spams[df_spams["pnt_id"] == pid]["xE"].values[0]
    xI = df_spams[df_spams["pnt_id"] == pid]["xI"].values[0]
    t = int(df_spams[df_spams["pnt_id"] == pid]["tau"].values[0])

    ## Create a subset from the meteo dataset
    meteo_subset = df_meteo.loc[
        (df_meteo["datum"] > (start - timedelta(days=t))) & (df_meteo["datum"] <= end)
    ].reset_index(drop=True)

    ## Compute SPAMS model
    reversible, irreversible, height = utils.spams_model(xP, xE, xI, t, meteo_subset)

    ## An example plot for a random parcel
    plt.figure(figsize=(12, 6))
    plt.title("ID #{}".format(pid))
    plt.plot(epoch, height, "-m", markersize=2, label="Total")
    plt.plot(epoch, reversible, "--C7", markersize=2, label="Reversible")
    plt.plot(epoch, irreversible, "--C7", linewidth=2, label="Irreversible")
    plt.legend(loc="upper right")
    plt.ylabel("Relative height (mm)")
    plt.grid(linestyle="--", alpha=0.5)
    plt.show()


if __name__ == "__main__":
    main()
