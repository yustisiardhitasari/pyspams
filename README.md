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

The current implementation can read meteorological data from The Royal Netherlands Meteorological Institute [KNMI](https://www.knmi.nl/nederland-nu/klimatologie/daggegevens) stations. This repo provides an example dataset under `data/`, including SPAMS parameters estimated using InSAR observations from 2016 to 2022 and meteorological data from the closest KNMI stations.

## Usage
### SPAMS time series surface motions
```
python spams_main.py
```

### Get information about required input parameters
```
python spams_main.py -h
```

