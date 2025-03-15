#%%
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
    assert usdm.valid_dates(2020) == ["01/01/2020", "12/31/2020"]
    assert usdm.valid_dates([2020, 2021, 2022]) == ["01/01/2020", "12/31/2022"]
    assert usdm.valid_dates(["01-01-2020", "12-31-2022"]) == ['01/01/2020', '12/31/2022']
    assert usdm.valid_dates(["01-01-2020", "2022-12-31"]) == ["01/01/2020", "12/31/2022"]
    assert usdm.valid_dates(2020) == ["01/01/2020", "12/31/2020"]
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


def test_get_comp_stats(mocker):
        # Mock the requests.get call to return a custom response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'mapDate': '2023-12-26T00:00:00',
                'stateAbbreviation': 'VA',
                'none': 22.37,
                'd0': 77.63,
                'd1': 50.74,
                'd2': 7.9,
                'd3': 0.0,
                'd4': 0.0,
                'validStart': '2023-12-26T00:00:00',
                'validEnd': '2024-01-01T23:59:59',
                'statisticFormatID': 1
            },
            {
                'mapDate': '2023-12-19T00:00:00',
                'stateAbbreviation': 'VA',
                'none': 22.35,
                'd0': 77.65,
                'd1': 51.73,
                'd2': 7.9,
                'd3': 0.0,
                'd4': 0.0,
                'validStart': '2023-12-19T00:00:00',
                'validEnd': '2023-12-25T23:59:59',
                'statisticFormatID': 1
            },
            {
                'mapDate': '2023-12-12T00:00:00',
                'stateAbbreviation': 'VA',
                'none': 13.04,
                'd0': 86.96,
                'd1': 63.03,
                'd2': 12.83,
                'd3': 0.0,
                'd4': 0.0,
                'validStart': '2023-12-12T00:00:00',
                'validEnd': '2023-12-18T23:59:59',
                'statisticFormatID': 1
            }
        ]
        mocker.patch("requests.get", return_value=mock_response)

        # Create a USDM object
        drought_object = usdm.USDM(geography="VA", time_period=2023)

        # Call the get_comp_stats method
        result_df = drought_object.get_comp_stats()

        # Check the result
        assert not result_df.empty
        assert "NONE_Area" in result_df.columns
        assert "D0_Area" in result_df.columns
        assert "D1_Area" in result_df.columns
        assert "D2_Area" in result_df.columns
        assert "D3_Area" in result_df.columns
        assert "D4_Area" in result_df.columns
        assert "mapStartDate" in result_df.columns
        assert "mapEndDate" in result_df.columns


        def test_clean_stat():
          # Test with a single string input
          assert usdm.clean_stat("area") == ["Area"]
          assert usdm.clean_stat("percent") == ["Percent"]
          assert usdm.clean_stat("population") == ["Population"]
          assert usdm.clean_stat("dsci") == ["DSCI"]
          assert usdm.clean_stat("nonconsecutive") == ["NonConsecutiveStatisticsCounty"]
          assert usdm.clean_stat("consecutive") == ["ConsecutiveWeeksCounty"]

          # Test with a list of strings
          assert usdm.clean_stat(["area", "percent", "population", "dsci", "nonconsecutive", "consecutive"]) == [
            "Area", "Percent", "Population", "DSCI", "NonConsecutiveStatisticsCounty", "ConsecutiveWeeksCounty"
          ]

          # Test with mixed case input
          assert usdm.clean_stat("ArEa") == ["Area"]

          # Test with invalid input
          with pytest.raises(AttributeError):
            usdm.clean_stat(123)
          with pytest.raises(AttributeError):
            usdm.clean_stat(None)


        def test_clean_drought_threshold():
            # Test with a single integer input
            assert usdm.clean_drought_threshold(3) == [3]

            # Test with a list of integers
            assert usdm.clean_drought_threshold([0, 1, 2, 3, 4]) == [0, 1, 2, 3, 4]

            # Test with an empty list
            assert usdm.clean_drought_threshold([]) == []

            # Test with invalid input (string)
            with pytest.raises(ValueError):
                usdm.clean_drought_threshold("invalid")

            # Test with invalid input (None)
            with pytest.raises(ValueError):
                usdm.clean_drought_threshold(None)

# %%
