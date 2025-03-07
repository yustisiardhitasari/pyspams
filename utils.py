import numpy as np
import pandas as pd


def spams_model(xP, xE, xI, tau, meteo_df):
    """Compute SPAMS model using SPAMS parameters and meteo data
    from The Royal Netherlands Meteorological Institute (KNMI).

    Reference: Conroy et. al.. 2023. SPAMS: A new empirical model for
    soft soil surface displacement based on meteorological input data
    (https://doi.org/10.1016/j.geoderma.2023.116699).


    Parameters
    ----------
    xP : float
        Scaling factor for precipitation (mm/mm).
    xE : float
        Scaling factor for evapotranspiration (mm/mm).
    xI : float
        Irreversible constant, active during dry period (mm/day).
    tau : int
        Time constant (days).
    meteo_df : pd.DataFrame
        Daily precipitation and evapotranspiration (mm).

    Returns
    -------
    float
        Relative height, reversible, and irreversible in mm.
    """
    ## Get daily precipitation and evapotranspiration
    p = np.lib.stride_tricks.sliding_window_view(meteo_df["precip"], tau)
    e = np.lib.stride_tricks.sliding_window_view(meteo_df["evapo"], tau)

    ## Reversible
    reversible = np.sum(xP * p - xE * e, axis=1)

    ## Irreversible
    dry_flag = np.zeros(reversible.size)
    dry_flag[reversible < 0] = 1
    irreversible = np.cumsum(xI * dry_flag)

    ## Relative height in m
    height = reversible + irreversible

    return reversible, irreversible, height


def read_knmi(file):
    """Precipitation and evapotranspiration data from
    The Royal Netherlands Meteorological Institute (KNMI).

    This function reads a KNMI file, extract daily precipitation (mm)
    and potential evapotranspiration (mm), and return it as a pd.DataFrame.

    The KNMI file can be downloaded through
    https://www.knmi.nl/nederland-nu/klimatologie/daggegevens.

    Parameters
    ----------
    file : str
        Path to the KNMI file with .txt format/

    Returns
    -------
    pd.DataFrame
        Daily precipitation and evapotranspiration.
    """
    df_knmi = pd.DataFrame(
        data=np.genfromtxt(
            file,
            delimiter=",",
            skip_header=53,
            missing_values="",
            filling_values=np.nan,
            usecols=(0, 1, 22, 40),
        ),
        columns=["knmi_id", "datum", "precip", "evapo"],
    )

    df_knmi["knmi_id"] = df_knmi["knmi_id"].astype(int)
    df_knmi["datum"] = pd.to_datetime(df_knmi["datum"].astype(str), format="%Y%m%d.0")
    df_knmi["precip"] = df_knmi["precip"] / 10  # mm
    df_knmi["evapo"] = df_knmi["evapo"] / 10  # mm

    return df_knmi
