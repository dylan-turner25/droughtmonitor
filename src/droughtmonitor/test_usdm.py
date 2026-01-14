
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
    assert usdm.valid_dates(["01-01-2020", "12-31-2022"]) == ['01/01/2020',
                                                              '12/31/2022']
    assert usdm.valid_dates(["01-01-2020", "2022-12-31"]) == ["01/01/2020",
                                                              "12/31/2022"]
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
    assert usdm.clean_stat("nonconsecutive") == [
        "NonConsecutiveStatisticsCounty"
    ]
    assert usdm.clean_stat("consecutive") == ["ConsecutiveWeeksCounty"]

    # Test with a list of strings
    assert usdm.clean_stat(["area", "percent", "population",
                            "dsci", "nonconsecutive", "consecutive"]) == [
        "Area", "Percent", "Population", "DSCI",
        "NonConsecutiveStatisticsCounty", "ConsecutiveWeeksCounty"
    ]

    # Test with mixed case input
    assert usdm.clean_stat("ArEa") == ["Area"]


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


def test_get_closest_mapdate(mocker):

    import pandas as pd

    # Mock the load_map_dates function to return a predefined set of dates
    mock_dates = pd.Series(pd.to_datetime(["2023-01-01",
                                           "2023-06-15",
                                           "2023-12-31"]))
    mocker.patch("droughtmonitor.usdm.load_map_dates", return_value=mock_dates)

    # Test with a date that matches exactly
    assert usdm.get_closest_mapdate("2023-06-15") == "20230615"

    # Test with a date closer to the first date
    assert usdm.get_closest_mapdate("2023-01-02") == "20230101"

    # Test with a date closer to the last date
    assert usdm.get_closest_mapdate("2023-12-30") == "20231231"

    # Ensure the function handles DatetimeIndex correctly
    assert usdm.get_closest_mapdate("2023-06-16") == "20230615"

    # Test with an invalid date
    with pytest.raises(ValueError):
        usdm.get_closest_mapdate("invalid-date")


def test_get_spatial_data(mocker):
    mock_geojson = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'id': 1,
                'geometry': {
                    'type': 'MultiPolygon',
                    'coordinates': [
                        [
                            [
                                [-67.17698061099998, 18.009180920000063],
                                [-67.17708228299995, 18.00909258200005],
                                [-67.17718873699994, 18.008994146000077],
                                [-67.17719749899999, 18.008985891000066],
                                [-67.17723647999998, 18.008950515000038],
                                [-67.17728598299993, 18.00890140100006],
                                [-67.17744226599996, 18.00874777000007],
                                [-67.17749090299998, 18.008666438000034],
                                [-67.17749251199996, 18.00866348900007],
                                [-67.17753308899995, 18.008595666000076],
                                [-67.17698061099998, 18.009180920000063]
                            ]
                        ]
                    ]
                },
                'properties': {
                    'OBJECTID': 5,
                    'DM': 4,
                    'Shape_Length': 0.2663825701307218,
                    'Shape_Area': 0.003142887288363598
                }
            }
        ]
    }

    import geopandas as gpd

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_geojson
    mocker.patch("requests.get", return_value=mock_response)

    # Mock geopandas.read_file to return a GeoDataFrame
    mock_gdf = gpd.GeoDataFrame.from_features(mock_geojson['features'])
    mocker.patch("geopandas.read_file", return_value=mock_gdf)

    mock_map_date = "20231231"
    mocker.patch("droughtmonitor.usdm.get_closest_mapdate",
                 return_value=mock_map_date)

    # Create a USDM object
    drought_object = usdm.USDM(geography="TOTAL", time_period="2023-12-31")

    # Test with format="df"
    result = drought_object.get_spatial_data(format="df")
    assert isinstance(result, dict)
    assert "12/31/2023" in result
    assert isinstance(result["12/31/2023"], gpd.GeoDataFrame)
    assert not result["12/31/2023"].empty

    # test with format = "json"
    result = drought_object.get_spatial_data(format="json")
    assert isinstance(result, dict)
    assert "12/31/2023" in result
    assert isinstance(result["12/31/2023"], dict)
    assert "features" in result["12/31/2023"]
    assert len(result["12/31/2023"]["features"]) > 0
    assert result["12/31/2023"]["features"][0]["properties"]["DM"] == 4


# Tests for new group_by functionality

def test_usdm_group_by_parameter_validation():
    """Test that the USDM constructor validates group_by parameter correctly."""
    
    # Test valid group_by values
    usdm_obj = usdm.USDM(geography="CA", group_by=None, time_period=[2020])
    assert usdm_obj.group_by is None
    
    usdm_obj = usdm.USDM(geography="CA", group_by="county", time_period=[2020])
    assert usdm_obj.group_by == "county"
    
    usdm_obj = usdm.USDM(geography="US", group_by="state", time_period=[2020])
    assert usdm_obj.group_by == "state"
    
    # Test invalid group_by values
    with pytest.raises(ValueError, match="group_by must be None, 'county', or 'state'"):
        usdm.USDM(geography="CA", group_by="invalid", time_period=[2020])
    
    # Test invalid combinations
    # NOTE: US with group_by="county" is now VALID (enhanced functionality)
    # Just test that it works
    usdm_obj = usdm.USDM(geography="US", group_by="county", time_period=[2020], confirm=False)
    assert usdm_obj.group_by == "county"

    with pytest.raises(ValueError, match="group_by='state' is only valid with national geography"):
        usdm.USDM(geography="CA", group_by="state", time_period=[2020])

    with pytest.raises(ValueError, match="group_by='county' requires state-level or national geography"):
        usdm.USDM(geography="01001", group_by="county", time_period=[2020])  # county geography


def test_get_counties_in_state():
    """Test the get_counties_in_state helper function."""
    
    # Test with state abbreviation
    counties_ca = usdm.get_counties_in_state("CA")
    assert isinstance(counties_ca, list)
    assert len(counties_ca) > 0
    assert "06001" in counties_ca  # Alameda County should be in CA
    assert all(county.startswith("06") for county in counties_ca)  # All should start with CA state code
    
    # Test with state FIPS code
    counties_ca_fips = usdm.get_counties_in_state("06")
    assert counties_ca == counties_ca_fips  # Should return same result
    
    # Test with different state
    counties_tx = usdm.get_counties_in_state("TX")
    assert isinstance(counties_tx, list)
    assert len(counties_tx) > 0
    assert all(county.startswith("48") for county in counties_tx)  # TX state code is 48
    
    # Verify different states return different counties
    assert counties_ca != counties_tx


def test_get_all_states():
    """Test the get_all_states helper function."""
    
    states = usdm.get_all_states()
    assert isinstance(states, list)
    assert len(states) > 50  # Should have all US states and territories
    assert "CA" in states
    assert "TX" in states
    assert "NY" in states
    assert states == sorted(states)  # Should be sorted


def test_get_comp_stats_with_group_by_county(mocker):
    """Test get_comp_stats with group_by='county'."""
    
    # Mock API response for individual counties
    mock_county_response = {
        "validStart": "2020-01-07T00:00:00Z",
        "validEnd": "2020-01-13T00:00:00Z",
        "mapDate": "2020-01-07T00:00:00Z",
        "d0": 100.5,
        "d1": 75.2,
        "d2": 50.1,
        "d3": 25.0,
        "d4": 10.0,
        "none": 200.0
    }
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [mock_county_response]
    mocker.patch("requests.get", return_value=mock_response)
    
    # Mock get_counties_in_state to return just a few counties for testing
    mock_counties = ["06001", "06003", "06005"]  # Alameda, Alpine, Amador
    mocker.patch("droughtmonitor.usdm.get_counties_in_state", return_value=mock_counties)
    
    # Create USDM object with county grouping
    drought_obj = usdm.USDM(geography="CA", group_by="county", time_period=[2020])
    result = drought_obj.get_comp_stats(stat=["Area"])
    
    # Verify result structure
    assert isinstance(result, usdm.pd.DataFrame)
    assert len(result) == len(mock_counties)  # One row per county
    
    # Check that geographic identifiers are added
    required_columns = ["county_fips", "county_name", "state_code", "state_name"]
    for col in required_columns:
        assert col in result.columns
    
    # Check that all counties are represented
    assert set(result["county_fips"]) == set(mock_counties)
    
    # Verify all state codes are CA (06)
    assert all(result["state_code"] == "06")
    assert all(result["state_name"] == "CA")


def test_get_comp_stats_with_group_by_state(mocker):
    """Test get_comp_stats with group_by='state'."""
    
    # Mock API response for individual states
    mock_state_response = {
        "validStart": "2020-01-07T00:00:00Z",
        "validEnd": "2020-01-13T00:00:00Z",
        "mapDate": "2020-01-07T00:00:00Z",
        "d0": 1000.5,
        "d1": 750.2,
        "d2": 500.1,
        "d3": 250.0,
        "d4": 100.0,
        "none": 2000.0
    }
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [mock_state_response]
    mocker.patch("requests.get", return_value=mock_response)
    
    # Mock get_all_states to return just a few states for testing
    mock_states = ["CA", "TX", "NY"]
    mocker.patch("droughtmonitor.usdm.get_all_states", return_value=mock_states)
    
    # Mock convert_state_code for state FIPS conversion
    state_fips_map = {"CA": "06", "TX": "48", "NY": "36"}
    mocker.patch("droughtmonitor.usdm.convert_state_code", side_effect=lambda x: state_fips_map[x])
    
    # Create USDM object with state grouping
    drought_obj = usdm.USDM(geography="US", group_by="state", time_period=[2020])
    result = drought_obj.get_comp_stats(stat=["Area"])
    
    # Verify result structure
    assert isinstance(result, usdm.pd.DataFrame)
    assert len(result) == len(mock_states)  # One row per state
    
    # Check that geographic identifiers are added
    required_columns = ["state_code", "state_name"]
    for col in required_columns:
        assert col in result.columns
    
    # Check that all states are represented
    assert set(result["state_name"]) == set(mock_states)


def test_get_weeks_in_drought_ignores_group_by(mocker):
    """Test that get_weeks_in_drought ignores the group_by parameter."""
    
    # Mock API response
    mock_weeks_response = {
        "nonConsecutiveWeeks": 15,
        "consecutiveWeeks": 8,
        "startDate": "2020-06-01T00:00:00Z",
        "endDate": "2020-08-01T00:00:00Z"
    }
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [mock_weeks_response]
    mocker.patch("requests.get", return_value=mock_response)
    
    # Create USDM objects with and without group_by - should behave identically
    drought_obj_no_group = usdm.USDM(geography="CA", time_period=[2020])
    drought_obj_with_group = usdm.USDM(geography="CA", group_by="county", time_period=[2020])
    
    result_no_group = drought_obj_no_group.get_weeks_in_drought(drought_threshold=[0], stat=["consecutive"])
    result_with_group = drought_obj_with_group.get_weeks_in_drought(drought_threshold=[0], stat=["consecutive"])
    
    # Both results should be identical DataFrames
    assert isinstance(result_no_group, usdm.pd.DataFrame)
    assert isinstance(result_with_group, usdm.pd.DataFrame)
    
    # Should have same structure (group_by ignored)
    assert list(result_no_group.columns) == list(result_with_group.columns)
    assert len(result_no_group) == len(result_with_group)
    
    # Check for expected drought threshold columns
    assert "D0_ConsecutiveWeeks" in result_no_group.columns
    assert "D0_ConsecutiveWeeks" in result_with_group.columns
    
    # Should NOT have geographic identifier columns (since group_by is ignored)
    geographic_columns = ["county_fips", "county_name", "state_code", "state_name"]
    for col in geographic_columns:
        assert col not in result_no_group.columns
        assert col not in result_with_group.columns


def test_backward_compatibility():
    """Test that existing functionality without group_by still works."""

    # Test that USDM objects without group_by work as before
    drought_obj = usdm.USDM(geography="CA", time_period=[2020])
    assert drought_obj.group_by is None
    assert drought_obj.geography == "CA"

    # Test with explicit group_by=None
    drought_obj2 = usdm.USDM(geography="CA", group_by=None, time_period=[2020])
    assert drought_obj2.group_by is None
    assert drought_obj2.geography == "CA"


def test_list_geography_validation():
    """Test validation of list geography inputs."""

    # Valid: list of states
    usdm_obj = usdm.USDM(geography=["CA", "OR", "WA"], time_period=[2020])
    assert usdm_obj.geography == ["CA", "OR", "WA"]
    assert usdm_obj.geography_list_input == True

    # Invalid: list with non-state (county FIPS code)
    # This will fail with "All geographies in list must be the same type" because CA is state and 06001 is county
    with pytest.raises(ValueError, match="All geographies in list must be the same type"):
        usdm.USDM(geography=["CA", "06001"], time_period=[2020])

    # Invalid: mixed national and state
    with pytest.raises(ValueError, match="All geographies in list must be the same type"):
        usdm.USDM(geography=["CA", "US"], time_period=[2020])

    # Invalid: group_by=state with list of states
    with pytest.raises(ValueError, match="When providing a list of states, group_by must be None or 'county'"):
        usdm.USDM(geography=["CA", "OR"], group_by="state", time_period=[2020])


def test_national_county_query_validation():
    """Test that national geography with group_by=county is allowed."""

    # Should accept US with group_by=county
    usdm_obj = usdm.USDM(geography="US", group_by="county", time_period=[2020], confirm=False)
    assert usdm_obj.group_by == "county"
    assert usdm_obj.geography == "TOTAL"

    # Should accept CONUS with group_by=county
    usdm_obj2 = usdm.USDM(geography="CONUS", group_by="county", time_period=[2020], confirm=False)
    assert usdm_obj2.group_by == "county"
    assert usdm_obj2.geography == "CONUS"


def test_estimate_api_calls():
    """Test API call estimation function."""

    # Single state, no grouping
    assert usdm.estimate_api_calls("CA", None, 5) == 5

    # State with county grouping - CA has 58 counties
    ca_estimate = usdm.estimate_api_calls("CA", "county", 5)
    assert ca_estimate == 58 * 5  # 290

    # List of states with county grouping
    list_estimate = usdm.estimate_api_calls(["CA", "OR"], "county", 5)
    ca_counties = len(usdm.get_counties_in_state("CA"))
    or_counties = len(usdm.get_counties_in_state("OR"))
    assert list_estimate == (ca_counties + or_counties) * 5

    # List of states without grouping
    assert usdm.estimate_api_calls(["CA", "OR", "WA"], None, 5) == 3 * 5


def test_confirmation_bypass(mocker):
    """Test that confirm=False bypasses the confirmation prompt."""

    # Mock API response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"mapDate": "2020-01-07", "d0": 100}]
    mocker.patch("requests.get", return_value=mock_response)

    # Mock estimate_api_calls to return high count
    mocker.patch("droughtmonitor.usdm.estimate_api_calls", return_value=1000)

    # With confirm=False, should not prompt and should return results
    drought_obj = usdm.USDM(geography="CA", group_by="county",
                            time_period=[2020], confirm=False)
    result = drought_obj.get_comp_stats(stat=["Area"])

    # Should return a DataFrame without prompting
    assert isinstance(result, usdm.pd.DataFrame)


def test_list_geography_get_comp_stats(mocker):
    """Test get_comp_stats with list of states and county grouping."""

    # Mock responses
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"mapDate": "2020-01-07", "d0": 100}]
    mocker.patch("requests.get", return_value=mock_response)

    # Mock get_counties_in_state to return fixed counties
    mocker.patch("droughtmonitor.usdm.get_counties_in_state",
                 return_value=["06001", "06003"])

    # Test list of states with county grouping
    drought_obj = usdm.USDM(geography=["CA", "OR"], group_by="county",
                            time_period=[2020], confirm=False)
    result = drought_obj.get_comp_stats(stat=["Area"])

    # Should return DataFrame with county geographic columns
    assert isinstance(result, usdm.pd.DataFrame)
    assert "county_fips" in result.columns
    assert "county_name" in result.columns
    assert "state_code" in result.columns
    assert "state_name" in result.columns


def test_confirm_parameters():
    """Test that confirm and confirm_threshold parameters are stored."""

    # Test default values
    drought_obj = usdm.USDM(geography="CA", time_period=[2020])
    assert drought_obj.confirm == True
    assert drought_obj.confirm_threshold == 50

    # Test custom values
    drought_obj2 = usdm.USDM(geography="CA", time_period=[2020],
                             confirm=False, confirm_threshold=100)
    assert drought_obj2.confirm == False
    assert drought_obj2.confirm_threshold == 100


# 
