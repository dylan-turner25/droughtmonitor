#%%
import os
import pandas as pd
from datetime import datetime


def check_status_code(status_code):
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

    Examples:
    >>> valid_aoi(1, fips_codes)
    >>> valid_aoi("01", fips_codes)
    >>> valid_aoi("AL", fips_codes)
    >>> valid_aoi("al", fips_codes)
    >>> valid_aoi(1001, fips_codes)
    >>> valid_aoi(01001, fips_codes)
    >>> valid_aoi("1001", fips_codes)
    >>> valid_aoi("01001", fips_codes)
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
            return fips_codes['state_code'][[s.lower() for s in fips_codes['state']].index(aoi)]

        # check to see if the aoi is in one of the state fips codes
        elif int(aoi) in [int(f) for f in fips_codes['state_code']]:
            matching_fips = fips_codes['state_code'][[int(f) for f in fips_codes['state_code']].index(int(aoi))]
            #matching_abb = fips_codes.loc[fips_codes['state_code'] == matching_fips, 'state'].values[0]
            return matching_fips
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

def valid_dates(start_date=None, end_date=None, year=None):
  if start_date is None and end_date is None:
      if year is None:
          raise ValueError("You must specify the start_date and end_date parameters or specify the year parameter.")
      else:
          if(isinstance(year, int)):
              year = [year]
          start_date = f"1/1/{min(year)}"
          end_date = f"12/31/{max(year)}"
  
      return start_date, end_date
  elif start_date is None or end_date is None:
      raise ValueError("You must specify both the start_date and end_date parameters.")
  else:
      return start_date, end_date


# a class USDM that contains the primary arguments for the data
class USDM:
  def __init__(self, aoi, start_date=None, end_date=None, year=None, url = "https://usdmdataservices.unl.edu/api/"):
    self.aoi = valid_aoi(aoi)
    


    self.start_date = start_date
    self.end_date = end_date
    self.year = year
    self.url = url

  

  @staticmethod
  def a_helper_function():
    result = "this is a helper function"
    return(result)
  
# methods to access each of three main APIs in the USDM
  def get_comp_stats(self):
     result = "comp stats for " + self.aoi
     return(result)

  def get_weeks_in_drought(self):
      result = "return weeks in drought for " + str(self.year)
      return(result)

  def get_stats_by_threshold(self):
      result = "return stats by threshold for " + str(self.start_date)
      return(result)


#usdm = USDM(aoi = "us", start_date=2000, end_date=2024, year = 2020)

#usdm.get_weeks_in_drought()
#usdm.get_stats_by_threshold()


  
# %%
