#%%
import pytest
from droughtmonitor.usdm import USDM 

def test_helper():
    """
    Test the helper function.
    """
    result = USDM.a_helper_function()
    assert result == 'this is a helper function'


def test_get_comp_stats():
    """
    Test the get_comp_states function.
    """
    usdm = USDM(aoi = "us", start_date=2000, end_date=2024, year = 2020)
    result = usdm.get_comp_stats()
    assert result == 'comp stats for us'



# %%
