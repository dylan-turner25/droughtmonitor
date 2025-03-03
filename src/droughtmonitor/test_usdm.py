#%%
import pytest
from droughtmonitor import usdm
from droughtmonitor.usdm import load_fips_codes

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
    drought_object = usdm.USDM(aoi = "us", start_date=2000, end_date=2024, year = 2020)
    result = drought_object.get_comp_stats()
    assert result == 'comp stats for us'



# %%
