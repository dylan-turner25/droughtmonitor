#%%
import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
import requests
from functools import lru_cache


def check_status_code(status_code):
    """
    Checks if the provided HTTP status code is 200 (OK).
    
    Args:
    status_code (int): The HTTP status code to check.
    
    Exception: If the status code is not 200, an exception 
    is raised with the status code.
    """
    if status_code != 200:
        raise Exception(f"HTTP status code: {status_code}")


def load_fips_codes():
    """
    Reads a CSV file containing FIPS codes that is in the 'data' folder, 
    cleans several columns,
    and returns it as a pandas DataFrame.
    Returns:
      pandas.DataFrame: A DataFrame containing the FIPS codes.
    """
    # load the fips codes
    file_path = os.path.join(os.path.dirname(__file__),
                             'data', 'fips_codes.csv')
    fips_codes = pd.read_csv(file_path)

    # convert state fips to character and add leading zero where necessary
    fips_codes['state_code'] = fips_codes['state_code'].astype(str)
    fips_codes['state_code'] = fips_codes['state_code'].str.zfill(2)

    # convert county fips to character and add leading zeros where necessary
    fips_codes['county_code'] = fips_codes['county_code'].astype(str)
    fips_codes['county_code'] = fips_codes['county_code'].str.zfill(3)

    # concat state_fips and county_fips to get a 5-digit "full_fips"
    fips_codes['full_fips'] = fips_codes['state_code']+fips_codes['county_code']

    return fips_codes


def valid_geography(geography, geography_type=None,
                    fips_codes=load_fips_codes()):
    """
    Clean the area of interest and ensure it is in a valid format.

    Parameters:
    geography (str or int): A numeric value or character string representing
                    either a state abbreviation, state FIPS code, or county FIPS code.
    fips_codes (DataFrame): A DataFrame containing 'state', 'state_code', and 'county_code' columns.

    Returns:
    str: A character string representing a 5-digit FIPS code.

    Raises:
    ValueError: If the area of interest is not valid.
    """

    # convert geography to a string
    geography = str(geography).strip().lower()

    # if us or continental us is chosen, then stop and return the geography
    if geography in ["us", "conus", "total"]:
        if geography.lower() == "us":
            return "TOTAL"
        else:
            return "CONUS"

    if geography_type in ["fips", None]:

        # get the number of characters in the geography
        n = len(geography)

        # if n is less than or equal to 2, process the geography as a state
        if n <= 2:
            # check to see if the geography is one of the state abbreviations
            if geography in [s.lower() for s in fips_codes['state']]:
                return fips_codes['state'][[s.lower() for s in fips_codes['state']].index(geography)]

            # check to see if the geography is in one of the state fips codes
            elif int(geography) in [int(f) for f in fips_codes['state_code']]:
                matching_fips = fips_codes['state_code'][[int(f) for f in fips_codes['state_code']].index(int(geography))]
                matching_abb = fips_codes.loc[fips_codes['state_code'] == matching_fips, 'state'].values[0]
                return matching_abb
            else:
                raise ValueError("Invalid area of interest specified. Either use the state's 2 letter abbreviation or the state's FIPS code. If you are attempting to specify a county as the area of interest, use the county's  5-digit FIPS code.")

        # if n is greater than 2, process the geography as a county
        if n > 2:
            # check to see if the geography matches a county fips code
            if int(geography) in [int(f) for f in fips_codes['full_fips']]:
                matching_fips = fips_codes['full_fips'][[int(f) for f in fips_codes['full_fips']].index(int(geography))]
                return matching_fips
            else:
              raise ValueError("Invalid area of interest specified.")


def geography_level(geography, geography_type=None, 
                    fips_codes=load_fips_codes()):
    """
    Determine the level of the area of interest (geography) based on the 
    provided geography parameter.
    
    Parameters:
    geography (str): The area of interest.
    fips_codes (DataFrame): A DataFrame containing FIPS codes, defaults to data loading via load_fips_codes().
    
    Returns:
    str: The level of the area of interest, which can be "national", "state", or "county".
    
    Raises:
    ValueError: If the supplied geography is not valid.
    """

    # make sure supplied geography is valid
    geography = valid_geography(geography, geography_type)

    # check if the area of interest is national
    if geography.lower() in ["us", "conus", "total"]:
        return "national"

    if geography_type in ["fips",None]:
        # get a list of state codes, state abbreviations, and county fips to
        # check geography agains
        state_abb = list(set(fips_codes['state'].str.strip()))
        state_code = list(set(fips_codes['state_code'].str.strip()))
        county_fips = list(set(fips_codes['full_fips'].str.strip()))

    # check to see if the area of interest is a state
    if geography in state_code or geography in state_abb:
        return "state"

    # check to see if the area of interest is a county
    if geography in county_fips:
        return "county"


def determine_date_type(date_list):
    """
    Determines the type of dates in the provided list.
    
    Args:
      date_list (list or int or str): A list of dates or a single date. Dates can be in the form of a year (int) or a string in the format "YYYY-MM-DD" or "MM-DD-YYYY".
    
    Returns:
      str: A string indicating the type of dates in the list:
        - "year" if all dates are years (integers).
        - "date" if all dates are in a valid date string format.
        - "mixed" if there is a mix of years and date strings.
        - "invalid" if the input is not a valid date or year.
    """

    if not isinstance(date_list, list):
        date_list = [date_list]

    year_count = 0
    date_count = 0

    for date in date_list:

      if len(str(date)) == 4 and isinstance(date, int):
        year_count += 1

      elif isinstance(date, str):
        date = date.replace("-", "/")
        try:  
          # try year-month-day format
          try:
              datetime.strptime(date, "%Y/%m/%d")
              date_count += 1
          except ValueError:
            # try month-day-year format
            try:
              datetime.strptime(date, "%m/%d/%Y")
              date_count += 1
            except ValueError:
              pass

        # if neither format works, return invalid  
        except ValueError:
          return "invalid"
      else:
        return "invalid"

    if year_count == len(date_list):
        return "year"
    elif date_count == len(date_list):
        return "date"
    elif year_count > 0 and date_count > 0:
        return "mixed"
    else:
        return "invalid"


def valid_dates(time_period):
    """
    Determine the start and end dates based on the provided time period.

    Parameters:
    time_period (int, list of int, or list of str): The time period for which to determine the valid dates.
      - If an integer or list of integers is provided, it is assumed to be a year or list of years.
      - If a list of two strings is provided, it is assumed to be a start date and an end date in 'YYYY-MM-DD' format.
    
    Returns:
    tuple: A tuple containing the start date and end date in 'MM/DD/YYYY' format.
    
    Raises:
    ValueError: If the time_period is not valid (i.e., not a list of years or a list of two dates).
    """
    # determine date type 
    date_type = determine_date_type(time_period)

    if date_type == "year":
        if (isinstance(time_period, int)):
            time_period = [time_period]
        start_date = f"01/01/{min(time_period)}"
        end_date = f"12/31/{max(time_period)}"
        return [start_date, end_date]
      
    if date_type == "date":
        if len(time_period) == 2:
          start_date = time_period[0].replace("-", "/")
          end_date = time_period[1].replace("-", "/")

          # check is start date is in day-month-year format
          try:
              datetime.strptime(start_date, "%d/%m/%Y")
              start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%m/%d/%Y")
          except ValueError:
              pass

          # check if end date is in year-month-day format
          try:
              datetime.strptime(end_date, "%Y/%m/%d")
              end_date = datetime.strptime(end_date, "%Y/%m/%d").strftime("%m/%d/%Y")
          except ValueError:
              pass

        else:
            return [time_period.replace("-", "/")]
        
        return [start_date, end_date]
    
    if date_type == "mixed" or date_type == "invalid":
        raise ValueError("The values entered for the time_period parameter are not valid. Please enter a list of years, a list of two dates (i.e. start and end dates)")


def rename_comp_stat_columns(query, names):
    """
    Renames columns in the given list of names based on the query string.

    This function looks for specific substrings in the query to determine the 
    label to append to the column names. It then replaces occurrences 
    of certain column names with their uppercase versions followed by the
    determined label.

    Args:
      query (str): The query string used to determine the label.
      names (list of str): The list of column names to be renamed.

    Returns:
      list of str: The list of renamed column names.
    """

    cols_to_change = ["none", "d0", "d1", "d2", "d3", "d4"]

    if "ByArea?" in query:
        label = "Area"
    if "AreaPercent?" in query:
        label = "AreaPercent"
    if "Population?" in query:
        label = "Population"
    if "PopulationPercent?" in query:
        label = "PopulationPercent"
    if "DSCI?" in query:
        label = "DSCI"

    for c in cols_to_change:
        names = [name.replace(c, f"{c.upper()}_{label}") for name in names]
    return names


def convert_state_code(state, fips_codes=load_fips_codes()):
    """
    Convert a state name to its corresponding FIPS state code or vice versa.
    This function takes a state name or FIPS state code and converts it to the
    corresponding FIPS state code or state name, respectively. The conversion
    is based on the provided FIPS codes DataFrame.
    
    Parameters:
    state (str): The state name or FIPS state code to be converted.
    fips_codes (pd.DataFrame, optional): A DataFrame containing FIPS codes with
                       columns 'state' and 'state_code'. If not
                       provided, the default is to call load_fips_codes().
    
    Returns:
    str: The corresponding FIPS state code if a state name is provided, or the
       corresponding state name if a FIPS state code is provided.
    
    Raises:
    ValueError: If the provided state name or FIPS state code cannot be converted.
    """
    
    if state in fips_codes['state'].unique():
        match = fips_codes.loc[fips_codes['state'] == state, 'state_code'].values[0]
        return match
    elif state in fips_codes['state_code'].unique():
        match = fips_codes.loc[fips_codes['state_code'] == state, 'state'].values[0]
        return match
    else:
        raise ValueError(f"Unable to convert {state}")

def clean_drought_threshold(drought_threshold):
        """
        Cleans and validates the drought threshold input.
        This function ensures that the input drought threshold is a list of integers.
        If the input is a single integer, it converts it to a list containing that integer.
        If the input is a string, it raises a ValueError.
        
        Parameters:
        drought_threshold (int or list of int): The drought threshold(s) to be cleaned and validated.
        
        Returns:
        list of int: A list of integers representing the drought thresholds.
        
        Raises:
        ValueError: If the input drought_threshold is a string.
        """
        
        # typ check drought_threshold
        if isinstance(drought_threshold, str):
           raise ValueError("drought_threshold must be a list of integers")
        if isinstance(drought_threshold, int):
            drought_threshold = [drought_threshold]
        return drought_threshold
  
def clean_stat(stat):
        """
        Cleans and standardizes the input statistic(s).
        This function takes a statistic or a list of statistics and converts them to a standardized format.
        If a single string is provided, it is converted to a list containing that string. The function then
        processes each statistic by converting it to lowercase and replacing certain keywords with their
        standardized counterparts.
        
        Args:
          stat (str or list of str): The statistic(s) to be cleaned. Can be a single string or a list of strings.
        
        Returns:
          list of str: A list of cleaned and standardized statistics.
        """
        
        # clean stat input (put it in a list of a single string was input)
        if isinstance(stat, str):
            stat = [stat]

        stat = [
            s.lower()
            .replace('area', "Area")
            .replace('percent', "Percent")
            .replace('population', "Population")
            .replace('dsci', "DSCI")
            .replace("nonconsecutive", "NonConsecutiveStatisticsCounty")
            .replace("consecutive", "ConsecutiveWeeksCounty")
            for s in stat
        ]

        return stat


@lru_cache(maxsize=None)
def load_map_dates():
    current_year = datetime.now().year

    q = (
      "https://usdmdataservices.unl.edu/api/USStatistics/"
      "GetDroughtSeverityStatisticsByArea?aoi=TOTAL&startdate=01/01/2000"
      f"&enddate=12/31/{current_year}&statisticsType=1"
    )

    headers = {'Accept': 'application/json'}

    # Get the data
    response = requests.get(q, headers=headers)

    # Check status code before continuing
    check_status_code(response.status_code)

    # Extract the data as a list
    map_dates = pd.DataFrame(response.json())['mapDate']

    # Convert map_dates to datetime
    map_dates = pd.to_datetime(map_dates)

    return map_dates


def get_closest_mapdate(date):
        """
        Given a date, this function retrieves the closest map date from the US Drought Monitor data.
        Args:
          date (str): The date for which to find the closest map date. The date should be in a format recognized by pandas.to_datetime().
        Returns:
          str: The closest map date in the format 'YYYYMMDD'.
        Raises:
          ValueError: If the provided date is not valid.
          requests.exceptions.RequestException: If there is an issue with the HTTP request.
        Notes:
          - This function fetches data from the US Drought Monitor API.
          - The function assumes the API returns data in JSON format with a 'mapDate' field.
        """
        
        date = valid_dates(date)
        
        # load map dates 
        map_dates = load_map_dates()

        # determine which date in map_dates is closest to the date provided
        closest_date = map_dates.iloc[(map_dates - pd.to_datetime(date[0])).abs().argsort()[:1]]

        # convert closest_date from series to string
        closest_date = closest_date.to_string(index=False)

        # convert closest_date from string to datetime
        closest_date = pd.to_datetime(closest_date)

        # convert to format used in USDM url
        closest_date = closest_date.strftime("%Y%m%d")
        
        return closest_date


# a class USDM that contains the primary arguments for the data
class USDM:
    """
    A class to interact with the United States Drought Monitor (USDM) API.
    Attributes:
    -----------
    geography : str
      The geographical area of interest.
    geography_type : str
      The type of geographical area (e.g., state, county).
    time_period : list
      The time period for which data is requested.
    url : str
      The base URL for the USDM API.
    Methods:
    --------
    get_comp_stats(stat=["Area", "AreaPercent", "Population", "PopulationPercent", "DSCI"], drought_threshold=[0, 1, 2, 3, 4], threshold_range=None):
      Retrieves composite statistics from the USDM API.
    get_weeks_in_drought(drought_threshold=[0, 1, 2, 3, 4], stat=["consecutive", "nonconsecutive"]):
      Retrieves the number of weeks in drought from the USDM API.
    get_spatial_data(format="df"):
      Retrieves spatial data from the USDM API.
    """

    def __init__(self, geography=None, geography_type=None,
                 time_period=None, url="https://usdmdataservices.unl.edu/api/"):
        self.geography_type = geography_type
        self.geography = valid_geography(geography, geography_type)

        # clean dates
        self.cleaned_dates = valid_dates(time_period)
        self.start_date = min(self.cleaned_dates)
        self.end_date = max(self.cleaned_dates)   
        self.url = url
       
    # methods to access each of three main APIs in the USDM
    def get_comp_stats(self, 
                       stat=["Area", "AreaPercent", "Population","PopulationPercent","DSCI"], 
                       drought_threshold=[0, 1, 2, 3, 4], 
                       threshold_range=None):
        
        """
        Retrieves composite statistics from the US Drought Monitor (USDM) API.

        This method fetches composite statistics for the specified geographical area and time period from the USDM API.
        The statistics can include area, area percent, population, population percent, and DSCI (Drought Severity and Coverage Index).
        The method constructs API queries based on the provided parameters, retrieves the data, and returns it as a pandas DataFrame.

        Parameters:
        -----------
        stat : list of str, optional
            A list of statistics to retrieve. Default is ["Area", "AreaPercent", "Population", "PopulationPercent", "DSCI"].
        drought_threshold : list of int, optional
            A list of drought thresholds to include in the query. Default is [0, 1, 2, 3, 4].
        threshold_range : list of int, optional
            A range of drought thresholds to include in the query. If specified, the query will include thresholds within this range.

        Returns:
        --------
        pandas.DataFrame
            A DataFrame containing the retrieved composite statistics.

        Raises:
        -------
        ValueError
            If the provided parameters are not valid.

        Example:
        --------
        usdm_instance = USDM(geography="NE", time_period=[2020, 2021])
        comp_stats_df = usdm_instance.get_comp_stats()
        print(comp_stats_df)
        """

        # might need to type check drought_threshold if it is specifed for
        # stats that aren't expressed as a percentage

        # clean drought threshold argument and type check it
        drought_threshold = clean_drought_threshold(drought_threshold)
        
        # clean stat input and type check it
        stat = clean_stat(stat)

        # Define area based on geography level
        area = {
            "national": "USStatistics/",
            "state": "StateStatistics/",
            "county": "CountyStatistics/"
        }.get(geography_level(self.geography))

        # initialize a vector to store queries
        query = []

        # Stat type can be 1 or 2, but both values appear to return the same data
        stat_type = 1

        # states, for whatever reason need to be entered as fips 
        # whereas other endpoints require two-letter abbreviation
        if area == "StateStatistics/":
            aoi = convert_state_code(self.geography)
        else:
            aoi = self.geography

        # construct portion of the query related to min/max thresholds
        if threshold_range is not None:
            stat_endpoint = "BasicStatisticsBy"
            threshold_query = f"&dx={drought_threshold[0]}&DxLevelThresholdFrom={min(threshold_range)}&DxLevelThresholdTo={max(threshold_range)}"
        else:
            threshold_query = ""
            stat_endpoint = "DroughtSeverityStatisticsBy"

        # paste the components specific to the variable together
        query.extend(
           [
              f'{self.url}{area}Get{stat_endpoint*(s != "DSCI")}{s}?aoi={aoi}{threshold_query}&startdate={self.start_date}&enddate={self.end_date}&statisticsType={stat_type}'
              for s in stat
           ]
        )

        # initialize data as a dict
        data_dict = {}

        # initialize a index variable
        index = 1

        # loop over each individual url in the query vector
        for q in query:

            # header specifying data should be returned in json format
            headers = {'Accept': 'application/json'}

            # get the data
            response = requests.get(q, headers=headers)
            
            # check status code before continuing
            check_status_code(response.status_code)

            # extract the data as a list
            data = response.json()

            # add data to data_list dictionary
            data_dict[index] = pd.DataFrame(data)

            data_dict[index].columns = rename_comp_stat_columns(query=q, names=data_dict[index].columns)

            # rename columns
            data_dict[index].rename(columns={
                "validStart": "mapStartDate",
                "validEnd": "mapEndDate",
            }, inplace=True)

            # advance index
            index += 1

        # merge each of the dataframes in the data_list dictionary using a full join
        result_df = data_dict[1]
        for i in range(2, len(data_dict) + 1):
            result_df = result_df.merge(data_dict[i], how='outer')

        # remove time of day from date columns
        date_columns = [c for c in result_df.columns if "Date" in c]
        for c in date_columns:
            result_df[c] = pd.to_datetime(result_df[c]).dt.date

        # remove any columns not defined by the drought threshold
        # if drought threshold was defined. 
        if drought_threshold is not None:
            for d in range(5):
              if d not in drought_threshold:
                result_df = result_df[[c for c in result_df.columns if f"D{d}" not in c]]
        
        return result_df


    def get_weeks_in_drought(self, drought_threshold=[0, 1, 2, 3, 4], stat=["consecutive", "nonconsecutive"]):
        """
        Retrieve the number of weeks in drought for specified drought levels and statistics.
        Parameters:
        -----------
        drought_threshold : list of int, optional
          List of drought levels to query. Default is [0, 1, 2, 3, 4].
        stat : list of str, optional
          List of statistics to query. Options are "consecutive" and "nonconsecutive". Default is ["consecutive", "nonconsecutive"].
        Returns:
        --------
        pd.DataFrame
          A DataFrame containing the number of weeks in drought for each specified drought level and statistic.
          The DataFrame includes columns for consecutive and nonconsecutive weeks, start and end dates for consecutive weeks,
          and the query date range.
        Raises:
        -------
        ValueError
          If the response status code is not 200.
        """

        # clean drought threshold argument and type check it
        drought_threshold = clean_drought_threshold(drought_threshold)

        # clean stat input and type check it    
        stat = clean_stat(stat)     

        # define area for weeds in drought 
        area = "ConsecutiveNonConsecutiveStatistics/"
        
        # initialize a list to store queries
        query = []

        # iterate over stat_type and drought_threshold to create a list of queries
        query.extend(
          [
            f"{self.url}{area}Get{s}?geography={self.geography}&dx={drought_level}&minimumweeks=0&startdate={self.start_date}&enddate={self.end_date}"
            for drought_level in drought_threshold
            for s in stat
          ]
        )

        # initialize data as a ldict
        data_dict = {}

        # initialize a index variable
        index = 1

        # loop over each individual url in the query vector
        for q in query:

          # header specifying data should be returned in json format
          headers = {'Accept': 'application/json'}

          # get the data
          response = requests.get(q, headers=headers)
          
          # check status code before continuing
          check_status_code(response.status_code)

          # extract the data as a list
          data = response.json()

          # add data to data_list dictionary
          data_dict[index] = pd.DataFrame(data)

          # get the drought level from the query
          drought_level = None
          for d in range(5):
            if f"dx={d}" in q:
              drought_level = f"D{d}"

          # relabel columns to include drought level
          data_dict[index].rename(columns={
              "nonConsecutiveWeeks": f"{drought_level}_NonConsecutiveWeeks",
              "consecutiveWeeks": f"{drought_level}_ConsecutiveWeeks",
              "startDate": f"{drought_level}_ConsecutiveWeeksStartDate",
              "endDate": f"{drought_level}_ConsecutiveWeeksEndDate",
          }, inplace=True)

          # advance index
          index += 1
        
        # merge each of the dataframes in the data_list dictionary using a full join
        result_df = data_dict[1]
        for i in range(2, len(data_dict) + 1):
          result_df = result_df.merge(data_dict[i], how='outer')

        #add date range to specify the query date range
        result_df['QueryStartDate'] = pd.to_datetime(self.start_date)
        result_df['QueryEndDate'] = pd.to_datetime(self.end_date)

        # remove time of day from date columns
        date_columns = [c for c in result_df.columns if "Date" in c]
        for c in date_columns:
          result_df[c] = pd.to_datetime(result_df[c]).dt.date
      
        return result_df


    def get_spatial_data(self, format="df"):

        """
        Retrieve spatial data for the United States Drought Monitor (USDM) for a specific date.
        Parameters:
        format (str): The format in which to return the data. Options are "df" for a GeoDataFrame (default) 
                or "json" for a JSON object.
        Returns:
        GeoDataFrame or dict: The spatial data for the specified date in the requested format.
        Raises:
        ValueError: If the time_period parameter is not a single date in the format '%m/%d/%Y'.
        Notes:
        - This method is only applicable to national data. If the geography is not "TOTAL" or "CONUS", 
          it defaults to returning data for the whole United States.
        - The method prints a message indicating the date for which data is being retrieved.
        """
        
        if self.geography not in ["TOTAL", "CONUS"]:
            print("The get_spatial_data method is only applicable to national data. Defaulting to returning data for the whole United States.")
        
        # make sure the cleaned dates are a list, and set them to `map_date`
        if isinstance(self.cleaned_dates, list) == False:
            map_dates = [self.cleaned_dates]
        else:
            map_dates = self.cleaned_dates

        # if there is more than one map_date, take steps to get a list of 
        # applicable maps in between the start and end date
        if len(map_dates) > 1:
            
            # get the full range of dates between the start and end date
            map_dates = pd.date_range(start=min(self.cleaned_dates), end=max(self.cleaned_dates)).strftime("%m/%d/%Y").tolist()
            
        # get the closest map date for each date in map_dates, then keep the 
        # unique set to end up with the full range of avaliable map dates that 
        # are avaliable on USDM
        map_dates = list(set(get_closest_mapdate(date) for date in map_dates))
    
        # initialize a dictionary to store the map data
        geo_data = {}

        # loop over each map date
        for m in map_dates:

            # print a user message
            m_label = f'{m[4:6]}/{m[6:8]}/{m[0:4]}'

            print(f"Retrieving data for map dated: {m_label}")

            url = f"https://droughtmonitor.unl.edu/data/json/usdm_{m}.json"
            
            if format == "json":
                response = requests.get(url)
                data = response.json()
            
            if format == "df":
                data = gpd.read_file(url)

            geo_data[m_label] = data

        return geo_data

