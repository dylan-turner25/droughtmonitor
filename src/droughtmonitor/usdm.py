#%%
import os
import pandas as pd
from datetime import datetime
import requests

def check_status_code(status_code):
  """
  Checks if the provided HTTP status code is 200 (OK).
  Args:
    status_code (int): The HTTP status code to check.
  Raises:
    Exception: If the status code is not 200, an exception is raised with the status code.
  """
  if status_code != 200:
    raise Exception(f"HTTP status code: {status_code}")
  
def load_fips_codes():
  """
  Reads a CSV file containing FIPS codes that is in the 'data' folder, cleans several columns,
  and returns it as a pandas DataFrame.
  Returns:
    pandas.DataFrame: A DataFrame containing the FIPS codes.
  """
  # load the fips codes
  file_path = os.path.join(os.path.dirname(__file__), 'data', 'fips_codes.csv')
  fips_codes = pd.read_csv(file_path)

  # convert state fips to character and add leading zero where necessary
  fips_codes['state_code'] = fips_codes['state_code'].astype(str).str.zfill(2)

  # convert county fips to character and add leading zeros where necessary
  fips_codes['county_code'] = fips_codes['county_code'].astype(str).str.zfill(3)

  # concat state_fips and county_fips to get a 5-digit "full_fips"
  fips_codes['full_fips'] = fips_codes['state_code'] + fips_codes['county_code']

  return fips_codes

def valid_aoi(aoi, fips_codes = load_fips_codes()):
    """
    Clean the area of interest and ensure it is in a valid format.

    Parameters:
    aoi (str or int): A numeric value or character string representing
                    either a state abbreviation, state FIPS code, or county FIPS code.
    fips_codes (DataFrame): A DataFrame containing 'state', 'state_code', and 'county_code' columns.

    Returns:
    str: A character string representing a 5-digit FIPS code.

    Raises:
    ValueError: If the area of interest is not valid.
    """

    # convert aoi to a string
    aoi = str(aoi).strip().lower()

    # if us or continental us is chosen, then stop and return the aoi
    if aoi in ["us", "conus", "total"]:
        if aoi.lower() == "us":
            return "TOTAL"
        else:
            return "CONUS"


    # get the number of characters in the aoi
    n = len(aoi)

    # if n is less than or equal to 2, process the aoi as a state
    if n <= 2:
        # check to see if the aoi is one of the state abbreviations
        if aoi in [s.lower() for s in fips_codes['state']]:
            return fips_codes['state'][[s.lower() for s in fips_codes['state']].index(aoi)]

        # check to see if the aoi is in one of the state fips codes
        elif int(aoi) in [int(f) for f in fips_codes['state_code']]:
            matching_fips = fips_codes['state_code'][[int(f) for f in fips_codes['state_code']].index(int(aoi))]
            matching_abb = fips_codes.loc[fips_codes['state_code'] == matching_fips, 'state'].values[0]
            return matching_abb
        else:
            raise ValueError("Invalid area of interest specified. Either use the state's 2 letter abbreviation or the state's FIPS code. If you are attempting to specify a county as the area of interest, use the county's  5-digit FIPS code.")

    # if n is greater than 2, process the aoi as a county
    if n > 2:
        # check to see if the aoi matches a county fips code
        if int(aoi) in [int(f) for f in fips_codes['full_fips']]:
            matching_fips = fips_codes['full_fips'][[int(f) for f in fips_codes['full_fips']].index(int(aoi))]
            return matching_fips
        else:
          raise ValueError("Invalid area of interest specified.")

def aoi_level(aoi, fips_codes = load_fips_codes()):
  """
  Determine the level of the area of interest (AOI) based on the provided aoi parameter.
  
  Parameters:
  aoi (str): The area of interest.
  fips_codes (DataFrame): A DataFrame containing FIPS codes, defaults to data loading via load_fips_codes().
  
  Returns:
  str: The level of the area of interest, which can be "national", "state", or "county".
  
  Raises:
  ValueError: If the supplied AOI is not valid.
  """

  # make sure supplied aoi is valid
  aoi = valid_aoi(aoi)

  # check if the area of interest is national
  if aoi.lower() in ["us", "conus", "total"]:
      return "national"

  # get a list of state codes, state abbreviations, and county fips to
  # check aoi agains
  state_abb = list(set(fips_codes['state'].str.strip()))
  state_code = list(set(fips_codes['state_code'].str.strip()))
  county_fips = list(set(fips_codes['full_fips'].str.strip()))

  # check to see if the area of interest is a state
  if aoi in state_code or aoi in state_abb:
      return "state"

  # check to see if the area of interest is a county
  if aoi in county_fips:
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
 
  # determine date type 
  date_type = determine_date_type(time_period)

  if date_type == "year":
    if(isinstance(time_period, int)):
      time_period = [time_period]
    start_date = f"01/01/{min(time_period)}"
    end_date = f"12/31/{max(time_period)}"
    return start_date, end_date
  
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
      raise ValueError("A time_period entered as dates should be a list of exactly two dates specifying the start and end dates.")
    return start_date, end_date
 
  if date_type == "mixed" or date_type == "invalid":
    raise ValueError("The values entered for the time_period parameter are not valid. Please enter a list of years, a list of two dates (i.e. start and end dates)")

# a class USDM that contains the primary arguments for the data
class USDM:
  def __init__(self, aoi, time_period, url = "https://usdmdataservices.unl.edu/api/"):
    self.aoi = valid_aoi(aoi)

    # clean dates
    cleaned_dates = valid_dates(time_period)
    self.start_date = cleaned_dates[0]
    self.end_date = cleaned_dates[1]
 
    self.url = url


  
  @staticmethod
  def a_helper_function():
    result = "this is a helper function"
    return(result)
  
# methods to access each of three main APIs in the USDM
  def get_comp_stats(self):
     result = "comp stats for " + self.aoi
     return(result)

  def get_weeks_in_drought(self, drought_threshold = [0,1,2,3,4]):

    # if a single drought threshold is provided as an integer, convert to a list
    if isinstance(drought_threshold, int):
      drought_threshold = [drought_threshold]

    # define area for weeds in drought 
    area = "ConsecutiveNonConsecutiveStatistics/"
    
    # initialize a list to store queries
    query = []

    # loop over drought levels
    stat_types = ["NonConsecutiveStatisticsCounty", "ConsecutiveWeeksCounty"]
    query.extend(
      [f"{self.url}{area}Get{stat}?aoi={self.aoi}&dx={drought_level}&minimumweeks=0&startdate={self.start_date}&enddate={self.end_date}"
        for drought_level in drought_threshold
        for stat in stat_types]
    )

    # initialize data as a list
    data_list = {}

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
      data_list[index] = pd.DataFrame(data)


      # advance index
      index += 1
    
    return data_list


 

  def get_stats_by_threshold(self):
      result = "return stats by threshold for " + str(self.start_date)
      return(result)


  

# %%
