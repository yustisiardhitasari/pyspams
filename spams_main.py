import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spamsx_filepath",
        "-spamsx_fp",
        default="/Users/ylumbangaol/Documents/S3/projects/krimpenerwaard/post/data_for_repo/nl_krimpenerwaard_spams10.parquet",
        help="str, path to the SPAMS parameters file",
    )
    parser.add_argument(
        "--meteo_dir",
        "-met_dir",
        default="/Users/ylumbangaol/Documents/S3/projects/krimpenerwaard/post/data_for_repo/",
        help="str, path to the meteo file",
    )
    parser.add_argument(
        "--meteo_filename",
        "-met_fn",
        help="str, the meteorological data file name",
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
    parser.add_argument(
        "--parcel_id",
        "-pid",
        help="int, it will take a random parcel if empty",
    )

    args = parser.parse_args()

    ## Load SPAMS parameters
    df_spams = pd.read_parquet(args.spamsx_filepath)
    pnt_ids = df_spams["pnt_id"].unique()

    ## Time series dates
    start = pd.to_datetime(datetime.strptime(str(args.start_date), "%Y%m%d"))
    end = pd.to_datetime(datetime.strptime(str(args.end_date), "%Y%m%d"))
    epoch = pd.date_range(start=start, end=end)

    ## Select a parcel
    if args.parcel_id is None:
        pid = np.random.choice(pnt_ids)
    else:
        pid = np.int32(args.parcel_id)
    df_spams_sel = df_spams[df_spams["pnt_id"] == pid]

    ## SPAMS model parameters of the selected parcel
    xP = df_spams_sel["xP"].values[0]
    xE = df_spams_sel["xE"].values[0]
    xI = df_spams_sel["xI"].values[0]
    t = int(df_spams_sel["tau"].values[0])

    ## SPAMS model parameters stdev of the selected parcel
    std_xP = np.sqrt(df_spams_sel["var_xP"].values[0])
    std_xE = np.sqrt(df_spams_sel["var_xE"].values[0])
    std_xI = np.sqrt(df_spams_sel["var_xI"].values[0])

    ## Load and subset meteo data
    if args.meteo_filename is None:
        filelist = sorted(Path(args.meteo_dir).glob("**/etmgeg_*.txt"))
        f1 = [None] * len(filelist)
        for i, file in enumerate(filelist):
            f1[i] = utils.read_knmi(file)
        df_meteo = pd.concat(f1)

        meteo_id = df_spams_sel["meteo_id"].values[0]

        meteo_subset = df_meteo.loc[
            (df_meteo["meteo_id"] == meteo_id)
            & (df_meteo["datum"] > (start - timedelta(days=t)))
            & (df_meteo["datum"] <= end)
        ].reset_index(drop=True)
    else:
        df_meteo = utils.read_knmi(os.path.join(args.meteo_dir, args.meteo_filename))

        meteo_subset = df_meteo.loc[
            (df_meteo["datum"] > (start - timedelta(days=t)))
            & (df_meteo["datum"] <= end)
        ].reset_index(drop=True)

    ## Compute SPAMS model
    reversible, irreversible, height = utils.spams_model(xP, xE, xI, t, meteo_subset)

    ## An example plot for a random parcel
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(epoch, height, "-m", markersize=2, label="Total")
    ax.plot(epoch, reversible, "--C7", markersize=2, label="Reversible")
    ax.plot(epoch, irreversible, "--C7", linewidth=2, label="Irreversible")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylabel("Relative surface elevation (mm)")
    ax.grid(linestyle="--", alpha=0.5)

    ## Add information using text boxes
    info_text = (
        f"Parcel ID: {pid}\n"
        f"Loc (lon, lat): {round(df_spams_sel['pnt_lon'].values[0], 4)}, {round(df_spams_sel['pnt_lat'].values[0], 4)}\n"
        f"SPAMS parameters:\n"
        f"\t$x_P$ = {round(xP, 4)}, $\sigma_{{x_P}}$ = {round(std_xP, 4)}\n"
        f"\t$x_E$ = {round(xE, 4)}, $\sigma_{{x_E}}$ = {round(std_xE, 4)}\n"
        f"\t$x_I$ = {round(xI, 4)} mm/day, $\sigma_{{x_I}}$ = {round(std_xI, 4)}\n"
        f"\t$\\tau$ = {t}"
    )
    ax.text(
        0.02,
        0.14,
        info_text,
        verticalalignment="center",
        transform=ax.transAxes,
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.7),
    )

    source_text = "Data source: 10.4121/dfbe9109-d058-4a64-a5b4-1cc9d9a5f836"
    ax.text(
        0.6,
        0.04,
        source_text,
        verticalalignment="center",
        transform=ax.transAxes,
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.7),
    )

    plt.show()


if __name__ == "__main__":
    main()
