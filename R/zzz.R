.onLoad <- function(libname, pkgname) {

  # memoise functions
  monitor_drought <<- memoise::memoise(monitor_drought)

  # load fips codes
  utils::data("fips_codes")

}
