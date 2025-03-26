# pyspams
A Python implementation of Simple Parameterization for the Motion of Soils (SPAMS)

Reference: Conroy, P., van Diepen, S.A., Hanssen, R.F., 2023. SPAMS: A new empirical model for soft soil surface displacement based on meteorological input data. Geoderma 440, 116699. doi:10.1016/j.geoderma.2023.116699.

This model uses daily precipitation and evapotranspiration data from the closest meteorological station. The model parameters can be estimated using a certain period of observations, such as from extensometer and Interferometry Synthetic Aperture Radar (InSAR) data.

## Requirements
- [numpy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)

## Data
To generate time series surface motion using SPAMS, you need two datasets:
- A set of SPAMS parameters (see the reference for more details).
- Daily precipitation and evapotranspiration amount.

A set of SPAMS parameters (SPAMS10) for the Krimpenerwaard region in the Netherlands is available through [4TU.ResearchData](https://doi.org/10.4121/dfbe9109-d058-4a64-a5b4-1cc9d9a5f836). Users can download the data and the metadata from that repository to model relative surface elevation changes using this repository. The meteorological data from The Royal Netherlands Meteorological Institute [KNMI](https://www.knmi.nl/nederland-nu/klimatologie/daggegevens) stations can be downloaded following the station ID available in the metadata.

## Usage
### Get information about required input parameters
```
python spams_main.py -h
```
Four parameters need to be specified: the path to the SPAMS10 parameters and meteorological directory and the start and end date of the desired period. Optionally, users can specify the KNMI file name and parcel ID.

### SPAMS time series surface motions
```
python spams_main.py --spams10_filepath <SPAMS10_FILEPATH> --meteo_dir <METEO_DIR> --start_date <START_DATE> --end_date <END_DATE>
```
Replace variables with < > to your desired.
