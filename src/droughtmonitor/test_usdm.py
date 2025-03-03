#%%
import pytest
from droughtmonitor import usdm
from droughtmonitor.usdm import load_fips_codes

def determine_date_type(date_list):
    assert usdm.determine_date_type([2020,2021,2022]) == "year"
    assert usdm.determine_date_type(["2020-01-01", "2022/12/31"]) == "date"
    assert usdm.determine_date_type(["01/01/2020", "12-31-2022"]) == "date"
    assert usdm.determine_date_type(["01-01-2020", "2022-12-31"]) == "date"
    assert usdm.determine_date_type(["2020-01-01", 2022]) == "mixed"
    assert usdm.determine_date_type("2020-01-01") == "date"
    assert usdm.determine_date_type(2020) == "year"
    assert usdm.determine_date_type("2020") == "year"
    assert usdm.determine_date_type("invalid") == "invalid"

def test_valid_dates():
    assert usdm.valid_dates(2020) == ("01/01/2020", "12/31/2020")    
    assert usdm.valid_dates([2020,2021,2022]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(["01-01-2020", "12-31-2022"]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(["01-01-2020", "2022-12-31"]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(2020) == ("01/01/2020", "12/31/2020")
    with pytest.raises(ValueError):
        usdm.valid_dates("invalid")


def test_valid_aoi():
    """
    test the 'valid_aoi' function
    """
    assert usdm.valid_aoi(1) == "01"
    assert usdm.valid_aoi("01") == "01"
    assert usdm.valid_aoi("AL") == "01"
    assert usdm.valid_aoi("al") == "01"
    assert usdm.valid_aoi(1001) == "01001"
    assert usdm.valid_aoi("1001") == "01001"
    assert usdm.valid_aoi("01001") == "01001"
    with pytest.raises(ValueError):
        usdm.valid_aoi("invalid_aoi")

def test_aoi_level():
    """
    test the 'aoi_level' function to make sure it returns the correct geographic scope
    """
    assert usdm.aoi_level(1) == "state"
    assert usdm.aoi_level("01") == "state"
    assert usdm.aoi_level("AL") == "state"
    assert usdm.aoi_level("al") == "state"
    assert usdm.aoi_level(1001) == "county"
    assert usdm.aoi_level("1001") == "county"
    assert usdm.aoi_level("01001") == "county"
    assert usdm.aoi_level("us") == "national"
    assert usdm.aoi_level("US") == "national"
    assert usdm.aoi_level("CONUS") == "national"
    assert usdm.aoi_level("conus") == "national"
    assert usdm.aoi_level("total") == "national"
    assert usdm.aoi_level("TOTAL") == "national"
    with pytest.raises(ValueError):
        usdm.aoi_level("invalid_aoi")

def test_helper():
    """
    Test the helper function.
    """
    result = usdm.USDM.a_helper_function()
    assert result == 'this is a helper function'


def test_get_comp_stats():
    """
    Test the get_comp_states function.
    """
    drought_object = usdm.USDM(aoi = "us", time_period = 2020)
    result = drought_object.get_comp_stats()
    assert result == 'comp stats for TOTAL'



# %%
