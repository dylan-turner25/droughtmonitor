#' Clean the area of interest and ensure it is in a valid format
#'
#' @param aoi A numeric value or character string representing
#' either a state abbreviation, state fips code, or county fips code.
#'
#' @return
#' @noRd
#' @keywords internal
#'
#' @import tigris
#'
#' @examples
#' valid_aoi(1)
#' valid_aoi("01")
#' valid_aoi("AL")
#' valid_aoi("al")
#' valid_aoi(1001)
#' valid_aoi(01001)
#' valid_aoi("1001")
#' valid_aoi("01001")
valid_aoi <- function(aoi){

  # if us or continential us is choosen, then
  # stop and return the aoi
  if(tolower(aoi) %in% c("us","conus","total")){
    if(aoi == "us"){
      return("TOTAL")
    } else {
      return("CONUS")
    }
  }

  # load fips codes from tigris
  fips <- tigris::fips_codes

  # get a vector of state codes
  state_abb <- trimws(unique(fips$state))

  # get a vector state fips
  state_fips <- trimws(unique(fips$state_code))

  # get a vector of county fips
  county_fips <- trimws(paste0(fips$state_code,fips$county_code))

  # convert aoi to a character
  aoi <- trimws(tolower(as.character(aoi)))

  # get the number of characters in the aoi
  n <- nchar(aoi)

  # if n is less than or equal to 2, process the aoi as a state
  if(n <= 2){

    # check to see if the aoi is one of the state abbreviations
    if(aoi %in% tolower(state_abb)){

      return(state_abb[which(aoi == tolower(state_abb))])

      # check to see if the aoi is in one of the state fips codes
    } else if (as.numeric(aoi) %in% as.numeric(state_fips)){

      # get fips code as it is formatted in the tigris data set
      matching_fips <- state_fips[which(as.numeric(aoi) == as.numeric(state_fips))]

      # get the state abbreviation of the matching fips code
      matching_abb <- unique(fips$state[which(fips$state_code == matching_fips)])

      return(matching_abb)
    } else{
      stop(paste0("Invalid area of interest specified. Either use the state's",
                  " 2 letter abbreviation or the state's FIPS code.",
                  " If you are attempting to specify a county as the area of",
                  " interest, use the county's FIPS code."))
    }

  }

  # if n is greater than 2, process the aoi as a county
  if(n > 2){

    # check to see if the aoi matches a county fips code
    if(as.numeric(aoi) %in% as.numeric(county_fips)){

      # get the fips code that matches and return it in the same
      # format as the tigris data set (i.e. convert 4 digit fips to 5 digits)
      matching_fips <- county_fips[which(as.numeric(aoi) == as.numeric(county_fips))]

      return(matching_fips)
    }
  }

}

aoi_level <- function(aoi){

  # make sure supplied aoi is valid
  aoi <- valid_aoi(aoi)

  # check if the area of interest is national
  if(tolower(aoi) %in% c("us","conus","total")){
    return("national")
  }

  # load fips codes from tigris
  fips <- tigris::fips_codes

  # get a vector of state codes
  state_abb <- trimws(unique(fips$state))

  # check to see if the area of interest is a state
  if(aoi %in% state_abb){
    return("state")
  }

  # get a vector state fips
  #state_fips <- trimws(unique(fips$state_code))

  # get a vector of county fips
  county_fips <- trimws(paste0(fips$state_code,fips$county_code))

  # check to see if the area of interest is a county
  if(aoi %in% county_fips){
    return("county")
  }

}

valid_var <- function(var){

  # list of all variables that can be queried from the API
  avaliable_vars <- list("wid" = "weeks_in_drought",
                         "cs" = "comp_stats",
                         "sbt" ="stats_by_threshold")


  # check to make sure the supplied var is a valid choice
  if(tolower(var) %in% tolower(avaliable_vars)){

    # return the name (i.e. the abbreviation) of the matching variable
    matching_var <- which(tolower(var) == tolower(avaliable_vars))

    return(names(avaliable_vars)[matching_var])

  } else if(tolower(var) %in% tolower(names(avaliable_vars))){

    return(tolower(var))

  }  else{
    stop(paste0(var, " is not a valid variable choice. Choose one of: ",
                paste(avaliable_vars, collapse = ", ")))
  }

}

get_column_names <- function(query,names){

  # drought severity by Area
  if(grepl("GetDroughtSeverityStatisticsByArea\\?",query)){
    cols_to_change <- c("None","D0","D1","D2","D3","D4")
    for(c in cols_to_change){
      names[names == c] <- paste0(c,"_Area")
    }
    return(names)
  }

  # drought severity by percent area
  if(grepl("GetDroughtSeverityStatisticsByAreaPercent\\?",query)){
    cols_to_change <- c("None","D0","D1","D2","D3","D4")
    for(c in cols_to_change){
      names[names == c] <- paste0(c,"_Area_Percent")
    }
    return(names)
  }

  # drought severity by population
  if(grepl("GetDroughtSeverityStatisticsByPopulation\\?",query)){
    cols_to_change <- c("None","D0","D1","D2","D3","D4")
    for(c in cols_to_change){
      names[names == c] <- paste0(c,"_Population")
    }
    return(names)
  }

  # drought severity by percent population
  if(grepl("GetDroughtSeverityStatisticsByPopulationPercent\\?",query)){
    cols_to_change <- c("None","D0","D1","D2","D3","D4")
    for(c in cols_to_change){
      names[names == c] <- paste0(c,"_Population_Percent")
    }
    return(names)
  }

}

gen_api_query <- function(aoi, var, start_date = NULL, end_date = NULL,
                          fips = NULL){


  # make sure the supplied area of interest is valid
  aoi <- valid_aoi(aoi)

  # make sure the supplied var is valid
  var <- valid_var(var)

  # pick the correct API based on the variable selected
  if(var %in% c("wid")){
    API <- "weeks_in_drought"
  }
  if(var %in% c("cs") ){
    API <- "comp_stats"
  }

  # assign area based on the relevant API and variable combination
  if(API == "weeks_in_drought"){
    area <- "ConsecutiveNonConsecutiveStatistics/"
  }
  if(API == "comp_stats"){
    # assign the area type based on the supplied area of interest
    if(aoi_level(aoi) == "national"){
      area <- "USStatistics/"
    }
    if(aoi_level(aoi) == "state" ){
     area <- "StateStatistics/"

     # need to also make sure state is specified as fips code
     aoi <- unique(fips[which(fips$state == aoi),"state_code"])
    }
    if(aoi_level(aoi) == "county"){
      area <- "CountyStatistics/"
    }
  }

  # base url of the drought monitor API
  base_url <- "https://usdmdataservices.unl.edu/api/"

  # construct the component of the URL relevant to the variable selected
  if(var == "wid"){

    # initialize a vector to store queries
    query <- c()

    # loop over the two stat types avaliable for weeks in drought
    for(stat in c("NonConsecutive","Consecutive")){

      # if the drought level isn't specified, default to 0
      if(!exists("drought_level")){
        drought_level <- 0
      }

      # paste the components specific to the variable together
      var_component <- paste0("Get",stat,"StatisticsCounty?aoi=",
                              aoi,"&dx=",drought_level, "&minimumweeks=0" ,
                              "&startdate=",start_date,
                              "&enddate=",end_date)


      # paste together the querty from constituent parts
      query <- c(query, paste0(base_url,area,var_component))
    }

    # return the query
      return(query)
  }
  if(var == "cs"){

    # initialize a vector to store queries
    query <- c()

    # loop over the two stat types avaliable for weeks in drought
    for(stat in c("Area","AreaPercent","Population","PopulationPercent")){

     # hard coding drought level threshold to 0. This API parameter limits
     # the data to drought at or above this threshold. Hard coding this to 0,
     # means all drought levels will be returned. This simplifies the user
     # experience and the user can always discard additional data if is is
     # not needed.
     drought_level <- 0

     # Stat type can be 1 or 2, but both values appear to return the same data
     stat_type <- 1

      # paste the components specific to the variable together
      var_component <- paste0("GetDroughtSeverityStatisticsBy",stat,
                              "?aoi=",aoi,
                              "&startdate=",start_date,
                              "&enddate=",end_date,
                              "&statisticsType=",stat_type)


      # paste together the query from constituent parts
      query <- c(query, paste0(base_url,area,var_component))
    }

    # return the query
    return(query)
  }
}

check_status_code <- function(status_code){
  if(status_code != 200){
    stop(paste0("HTTP status code: ", status_code))
  }
}






