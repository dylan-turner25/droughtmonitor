# droughtmonitor

[![PyPI - Version](https://img.shields.io/pypi/v/droughtmonitor.svg)](https://pypi.org/project/droughtmonitor)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/droughtmonitor.svg)](https://pypi.org/project/droughtmonitor)
[![Python package](https://github.com/dylan-turner25/droughtmonitor/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/dylan-turner25/droughtmonitor/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/dylan-turner25/droughtmonitor/graph/badge.svg?token=qJ37dsQJPV)](https://codecov.io/gh/dylan-turner25/droughtmonitor)
[![Project Status:
WIP](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#WIP)
-----


## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)


The `droughtmonitor` package serves as an unofficial API wrapper for [U.S. Drought Monitor](https://droughtmonitor.unl.edu/) and provides a set of tools for making programatic access to the underlying data more accessable. The U.S. Drought Monitor website contains a [landing page](https://droughtmonitor.unl.edu/Data.aspx) for accessing both tabular and spatial data. However, accessing the data through this channel can be tedious for charts, measures, or analysis that need to be frequently updated. Programatic access is possible through the [existing API](https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx), but can also be tediuos without prior working knowledge of REST APIs. The `droughtmonitor` package strikes a balance between the two methods as it allows programatic access to enhance reproducability while requireing no additional techincal overhead beyond basic understanding of python. 

**Disclaimer** This product uses data from the U.S. Drought Monitor API, but is not endorsed by or affiliated with U.S. Drought Monitor or the Federal Government. 


## Installation
Currently, `droughtmonitor` can be installed from PyPI using pip. The drought monitor API does not utilize API keys meaning no further setup is required. 

```console
# install using pip
pip install droughtmonitor
```

## Usage

Usage of the `droughtmonitor` package starts by creating an object of the class `USDM` which is done by specifying a geographic location (`geography`) and time period (`time_period`). The geography can take the form of `"us"` for all of the United State, `"conus"` for the continental United States, a fips code or two letter abbreviation for a single state (ex: `6`,`"06`,`"CA"`, `"ca"` all return data for California), or a fips code for a single county (ex: `1001`,`"01001"`).

```python
# import the usdm module from drought monitor
from droughtmonitor import usdm

# create a drought object of the USDM class specifying California from 2020 to 2024
drought = usdm.USDM(geography = "CA", time_period=list(range(2020,2024)))

# create a drought object of the USDM class specifying the continential US from in the first month of 2020.
drought = usdm.USDM(geography = "conus", time_period=["1/1/2020", "1/31/2020"])

```

### Weeks in Drought
Once an object of the `USDM` class is created, the `get_weeks_in_drought` method can be used to obtain the number of weeks that the specified geography was at a specified drought level. An optional `drought_threshold` parameter can be specified as one of `[0,1,2,3,4]` corresponding to the drought levels used by U.S. Drought Monitor (default is to return measures for all drought levels in distinct columns). Another optional `stat` parameter can be specified as either `"consecutive"` or `"nonconsecutive"` to specify if the number of weeks at the specified drought level needs to be consecutive or not. Note that U.S. Drought Monitor only produces weeks at drought measures at the county level, meaning if a higher level geography is specified, the returned data will be at the county level for all counties within the specified geography. 

```python

# create drought object for California during 2021 using the state fips code
drought = usdm.USDM(geography = 6 , time_period=2021)

# get number of consecutive weeks at D3 level drought
wid = drought.get_weeks_in_drought(drought_threshold = 3, stat = "consecutive")
wid.head()

# get number of nonconsecutive weeks at all drought levels
wid = drought.get_weeks_in_drought(stat = "nonconsecutive")
wid.head()

# get number of consecutive and nonconsecutive weeks at all drought levels
wid = drought.get_weeks_in_drought()
wid.head()

```

### Comprehensive Statistics
The `get_comp_stats` method can be used to return several different statistics for each drought level for a specified geography and time period. The argument `stat` controls which statistic is returned and can be one of `["Area", "AreaPercent", "Population", "PopulationPercent", "DSCI"]` (not case sensitive) which correspond to the total area, percentage of an area, the total population, percentage of the population, and the [drought severity coverage index](https://droughtmonitor.unl.edu/About/AbouttheData/DSCI.aspx). The default behavior is to return the specified statistic for all drought levels (in sperate columns). If statistics for only one or a few drought threshold are desired, this can be achieved by specifying the `drought_threshold` parameter with a single integer or list of integers out of `[0,1,2,3,4]`.Unlike the weeks in drought data, comprehensive statistics are returned for the geographic level specified as opposed to returning county-level data for the specified geography.

```python

# create drought object for a single county from 2000 to 2024 using county fips code
drought = usdm.USDM(geography = "01001" , time_period=list(range(2000,2024)))

# get the percentage of the county that was in each drought level 
# for each week in the specified time period
cs = drought.get_comp_stats(stat = "AreaPercent")
cs.head()

# create drought object for california in 2024
drought = usdm.USDM(geography = "CA" , time_period=2024)

# get the total population subject to each drought level for 
# every week in 2024
cs = drought.get_comp_stats(stat = "Population")
cs.head()

# return only the area under D2 level drought
cs = drought.get_comp_stats(stat = "Area", drought_threshold = 2)
cs.head()

```

### Spatial Data

Spatial data can also be retrieved using `droughtmonitor`. To do so, create a USDM object and then call the `get_spatial_data` method. Spatial data is only avaliable at the national level, meaning `"us"` is the only valid geography for `USDM` when `get_spatial_data` is used. For the `time_period` argument, either a single date or a range of dates can be entered. In the case of a single date, the USDM map that has the closest date to the entered date will be retrieved. In the case of a range of dates being entered, the closest maps to the start and end date will be found, then those maps along with all maps between these dates, will be returned. 

Example: retrieving data for a single date.
```python

# import drought monitor
from droughtmonitor import usdm

# create a USDM object for the us with a single date as the time period
drought = usdm.USDM(geography = "us", time_period="1/1/2020")

# return geo-spatial drought data in json format for the map released closest to 1/1/2020
geo = drought.get_spatial_data(format = "json")

# data is returned as a dictionary with the keys equal to the date of the map (in this case the returned spatial data is from "12/31/2019" as that was the map with the closest date to the entered date)
geo['12/31/2019']

```


Example: retrieving data for a range of dates.
```python

# import drought monitor
from droughtmonitor import usdm

# create a USDM object for the us with a single date as the time period
drought = usdm.USDM(geography = "us", time_period=['1/1/2020','1/31/2020'])

# return geo-spatial drought data in data frame format
geo_data = drought.get_spatial_data(format = "df")

# data is returned as a dictionary with the keys equal to the date
geo_data['12/31/2019']

```


## License

`droughtmonitor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
