# droughtmonitor

[![PyPI - Version](https://img.shields.io/pypi/v/droughtmonitor.svg)](https://pypi.org/project/droughtmonitor)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/droughtmonitor.svg)](https://pypi.org/project/droughtmonitor)

[![Python package](https://github.com/dylan-turner25/droughtmonitor/actions/workflows/python-package.yml/badge.svg)](https://github.com/dylan-turner25/droughtmonitor/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/dylan-turner25/droughtmonitor/graph/badge.svg?token=NBLHixFDSD)](https://codecov.io/gh/dylan-turner25/droughtmonitor)
[![Project Status:
WIP](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#WIP)
-----

## Table of Contents
- [About](#about)
The `droughtmonitor` package serves as an API wrapper for U.S. Drought Monitor. 

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation
Currently, `droughtmonitor` can be installed directly from GitHub. The drought monitor API does not utilize API keys meaning no further setup is required. 
```console
# To install directly from GitHub
pip install git+https://github.com/dylan-turner25/droughtmonitor
```

## Usage

Usage of the `droughtmonitor` package starts by creating an object of the class `USDM` which is done by specifying a geographic location (`geography`) and time period (`time_period`).

```console
# import the usdm module from drought monitor
from droughtmonitor import usdm

# create a drought object of the USDM class specifying California from 2020 to 2024
drought = usdm.USDM(geography = "CA", time_period=list(range(2020,2024)))

# create a drought object of the USDM class specifying the continential US from in the first month of 2020.
drought = usdm.USDM(geography = "conus", time_period=["1/1/2020", "1/31/2020"])

```

### Weeks in Drought
Once an object of the `USDM` class is created, the `get_weeks_in_drought` method can be used to obtain the number of weeks that the specified geography was at a specified drought level. An option `drought_threshold` parameter can be specified as one of `[0,1,2,3,4]` corresponding to the drought levels used by U.S. Drought Monitor (default is to return measures for all drought levels in distinct columns). Another optional `stat` parameter can be specified as either `"consecutive"` or `"nonconsecutive"` to specify if the number of weeks at the specified drought level need to be consecutive or not. Note that U.S. Drought Monitor only produces weeks at drought measures at the county level, meaning if a higher level geography is specified, the returned data will be at the county level for all counties within the specified geography. 

```console

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



## License

`droughtmonitor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
