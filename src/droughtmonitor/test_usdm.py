import pytest
from droughtmonitor import usdm


def test_determine_date_type():
    assert usdm.determine_date_type([2020, 2021, 2022]) == "year"
    assert usdm.determine_date_type(["2020-01-01", "2022/12/31"]) == "date"
    assert usdm.determine_date_type(["01/01/2020", "12-31-2022"]) == "date"
    assert usdm.determine_date_type(["01-01-2020", "2022-12-31"]) == "date"
    assert usdm.determine_date_type(["2020-01-01", 2022]) == "mixed"
    assert usdm.determine_date_type("2020-01-01") == "date"
    assert usdm.determine_date_type(2020) == "year"
    assert usdm.determine_date_type("invalid") == "invalid"


def test_valid_dates():
    assert usdm.valid_dates(2020) == ("01/01/2020", "12/31/2020")
    assert usdm.valid_dates([2020, 2021, 2022]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(["01-01-2020", "12-31-2022"]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(["01-01-2020", "2022-12-31"]) == ("01/01/2020", "12/31/2022")
    assert usdm.valid_dates(2020) == ("01/01/2020", "12/31/2020")
    with pytest.raises(ValueError):
        usdm.valid_dates(["99-99-9999", "1111-11-11"])
    with pytest.raises(ValueError):
        usdm.valid_dates("invalid")


def test_valid_geography():
    assert usdm.valid_geography(1) == "AL"
    assert usdm.valid_geography("01") == "AL"
    assert usdm.valid_geography("AL") == "AL"
    assert usdm.valid_geography("al") == "AL"
    assert usdm.valid_geography(1001) == "01001"
    assert usdm.valid_geography("1001") == "01001"
    assert usdm.valid_geography("01001") == "01001"
    with pytest.raises(ValueError):
        usdm.valid_geography("invalid_geography")


def test_geography_level():
    assert usdm.geography_level(1) == "state"
    assert usdm.geography_level("01") == "state"
    assert usdm.geography_level("AL") == "state"
    assert usdm.geography_level("al") == "state"
    assert usdm.geography_level(1001) == "county"
    assert usdm.geography_level("1001") == "county"
    assert usdm.geography_level("01001") == "county"
    assert usdm.geography_level("us") == "national"
    assert usdm.geography_level("US") == "national"
    assert usdm.geography_level("CONUS") == "national"
    assert usdm.geography_level("conus") == "national"
    assert usdm.geography_level("total") == "national"
    assert usdm.geography_level("TOTAL") == "national"
    with pytest.raises(ValueError):
        usdm.geography_level("invalid_geography")


def test_helper():
    result = usdm.USDM.a_helper_function()
    assert result == 'this is a helper function'


def test_get_weeks_in_drought(mocker):
    # Mock the requests.get call to return a custom response
    mock_response = mocker.Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = [
        {
            'fips': '01003',
            'startDate': '2023-09-12T00:00:00',
            'endDate': '2023-11-14T00:00:00',
            'consecutiveWeeks': 10,
            'state': 'AL',
            'county': 'Baldwin County'
        },
        {
            'fips': '01007',
            'startDate': '2023-11-14T00:00:00',
            'endDate': '2023-12-26T00:00:00',
            'consecutiveWeeks': 7,
            'state': 'AL',
            'county': 'Bibb County'
        },
        {
            'fips': '01009',
            'startDate': '2023-10-31T00:00:00',
            'endDate': '2023-12-26T00:00:00',
            'consecutiveWeeks': 9,
            'state': 'AL',
            'county': 'Blount County'
        },
        {
            'fips': '01013',
            'startDate': '2023-10-24T00:00:00',
            'endDate': '2023-11-14T00:00:00',
            'consecutiveWeeks': 4,
            'state': 'AL',
            'county': 'Butler County'
        }
    ]

    mocker.patch("requests.get", return_value=mock_response)

    # Create a USDM object
    drought_object = usdm.USDM(geography="AL", time_period=2023)

    # Call the get_weeks_in_drought method
    result_df = drought_object.get_weeks_in_drought(3)

    # Check the result
    assert not result_df.empty
    assert "D3_ConsecutiveWeeks" in result_df.columns
    assert "QueryStartDate" in result_df.columns
    assert "QueryEndDate" in result_df.columns
    assert "county" in result_df.columns
    assert "state" in result_df.columns
    assert result_df.state.unique() == ["AL"]
