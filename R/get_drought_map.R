# a function to download and save maps from the us drought monitor site.
#' Title
#'
#' @param date date of map to retrieve. Default is "current" which will return the most recent map.
#' @param aoi the area of interest to get the map for
#' @param path file path to save map to
#' @param display_options display options to customize map returned
#'
#' @return returns a plot in the R viewer when path is NULL. If a file path
#' is specified, the map will be saved to that location.
#' @export
#'
#' @examples
#'get_drought_map(date = "current", aoi = "CA", display_options = "none")

get_drought_map <- function(date = "current", aoi, path = NULL,
                            display_options = NULL){

  # check for a valid aoi
  aoi <- valid_aoi(aoi)

  # process date
  if(date == "current"){
    map_date <- "current"
  }

  # process area
  area <- tolower(aoi)

  # process map options
  if(is.null(display_options)){
    options = "trd"
  }
  if(display_options == "none"){
    options = "none"
  }

  # construct url
  url <- paste0("https://droughtmonitor.unl.edu/data/png/",map_date,"/",map_date,"_",area,"_",options,".png")

  # if only a single aoi is specified return the single image
  if(length(aoi) == 1){
    if(is.null(path)){
     return(plot(imager::load.image(url), axes = FALSE))
    } else{
      # save image in specified format
    }
  }


  # if more than one aoi is specified, loop through the set of aois and
  # either save them all to the specified path, or return a facet grid



  # "https://droughtmonitor.unl.edu/data/png/current/current_conus_none.png"
  # https://droughtmonitor.unl.edu/data/png/current/current_conus_trd.png
  # https://droughtmonitor.unl.edu/data/png/current/current_conus_cat.png
}

