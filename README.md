droughtmonitor: access data from U.S. Drought Monitor
================

-   [Introduction](#introduction)
-   [Examples](#examples)
    -   [Example: Return comprehensive statistics for Sacramento County,
        CA](#example-return-comprehensive-statistics-for-sacramento-county-ca)
    -   [Example:](#example)

[![Project Status:
WIP](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#WIP)
[![Lifecycle:
Experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)

## Introduction

`droughtmonitor` allows users to access [U.S. Drought
Monitor’s](https://droughtmonitor.unl.edu/) publicly available data. The
package provides a set of functions to easily navigate through and
obtain drought related data provided by the organization.

## Examples

### Example: Return comprehensive statistics for Sacramento County, CA

The following code returns comprehensive statistics by week from January
1st, 2020 to December 31st, 2020. Comprehensive statistics include …

``` r
data <- monitor_drought(aoi = "06067",
                        var = "cs",
                        start_date = "1/1/2020",
                        end_date = "12/31/2020")
data
```

    ## # A tibble: 53 × 28
    ##    MapDate    FIPS  County       State None_Area D0_Area D1_Area D2_Area D3_Area
    ##    <date>     <chr> <chr>        <chr>     <dbl>   <dbl>   <dbl>   <dbl>   <dbl>
    ##  1 2020-12-29 06067 Sacramento … CA            0    989.    989.    989.    167.
    ##  2 2020-12-22 06067 Sacramento … CA            0    989.    989.    989.    167.
    ##  3 2020-12-15 06067 Sacramento … CA            0    989.    989.    989.    167.
    ##  4 2020-12-08 06067 Sacramento … CA            0    989.    989.    989.    167.
    ##  5 2020-12-01 06067 Sacramento … CA            0    989.    989.    890.    167.
    ##  6 2020-11-24 06067 Sacramento … CA            0    989.    989.    890.    167.
    ##  7 2020-11-17 06067 Sacramento … CA            0    989.    989.    890.    167.
    ##  8 2020-11-10 06067 Sacramento … CA            0    989.    989.    890.    167.
    ##  9 2020-11-03 06067 Sacramento … CA            0    989.    989.    890.    167.
    ## 10 2020-10-27 06067 Sacramento … CA            0    989.    989.    890.    167.
    ## # … with 43 more rows, and 19 more variables: D4_Area <dbl>,
    ## #   None_Area_Percent <dbl>, D0_Area_Percent <dbl>, D1_Area_Percent <dbl>,
    ## #   D2_Area_Percent <dbl>, D3_Area_Percent <dbl>, D4_Area_Percent <dbl>,
    ## #   None_Population <dbl>, D0_Population <dbl>, D1_Population <dbl>,
    ## #   D2_Population <dbl>, D3_Population <dbl>, D4_Population <dbl>,
    ## #   None_Population_Percent <dbl>, D0_Population_Percent <dbl>,
    ## #   D1_Population_Percent <dbl>, D2_Population_Percent <dbl>, …

``` r
# The following are ways to obtain the same data 
data <- monitor_drought(aoi = "6067", # robust to omitting the leading 0
                        var = "cs",
                        start_date = "1/1/2020",
                        end_date = "12/31/2020")

# specifying the year argument is an easier way to get data for an entire year
data <- monitor_drought(aoi = "6067",
                        var = "cs",
                        year = 2020) 

# note that map releases do not always correspond to the first and last days
# of the year, meaning the returned data may be slightly outside the 
# specified year(s). For example, in this case the minimum map dates is 
# December 31st  of the previous year. 
summary(data$MapDate)
```

    ##         Min.      1st Qu.       Median         Mean      3rd Qu.         Max. 
    ## "2019-12-31" "2020-03-31" "2020-06-30" "2020-06-30" "2020-09-29" "2020-12-29"

``` r
# The year argument can also be specified as a range for multiple years of data
data <- monitor_drought(aoi = "06067",
                        var = "cs",
                        year = 2020:2021) 
```

### Example:
