#' Retrieve data from the U.S. Drought Monitor API
#'
#' @param aoi The are of interest to call drought data for. Can be one of: "us"
#' for the entire United States, "conus" for the continental United States.
#' Selecting a state can be done by either specifying the numeric FIPS code
#' corresponding to the state or by using the state's two letter
#' abbreviation (ex: California can be selected with either: 06 or "CA"). A
#' specific county can be selected by specifying a character string representing
#' the county FIPS code (ex: "06019" for Fresno County, California).
#' @param var a character string representing the variables to return. Can be
#' either "cs" for comprehensive statistics or "wid" for weeks in drought.
#' @param start_date "a character string representing the start date to retrieve data for"
#' @param end_date "a character string representing the end date to retrieve data for"
#' @param year "a character string or numeric value for the year to retrieve data for.
#' `year` can be specified instead of start_date and end_date to retrieve data
#' for an entire year or range of years"
#' @return returns a tibble
#' @export
#'
#' @examples
#' data <- monitor_drought(aoi = "us",var = "cs",
#'                         year = 2021)
#' data <- monitor_drought(aoi = "01001",var = "cs",
#'                        start_date = "1/1/2021",
#'                        end_date = "12/31/2021")
monitor_drought <- function(aoi, var, start_date = NULL, end_date = NULL,
                            year = NULL){

  # if start date and end date aren't specified, create dates using the
  # specified year
  if(is.null(start_date) & is.null(end_date)){

    # if no year is specified, issue an error
    if(is.null(year)){
      stop("You must specify the start_date and end_date parameters or specify the year parameter.")
    } else{

      # construct the start date
      start_date <- paste0("1/1/",min(year))

      # construct the end date
      end_date <- paste0("12/31/",max(year))
    }

  }


  # get the api query
  query <- gen_api_query(aoi = aoi, var = var,
                         start_date = start_date, end_date = end_date)

  # initialize data as a list
  data_list <- list()

  # initialize a index variable
  index <- 1

  # loop over each individual url in the query vector
  for(q in query){

    # request the data
    response <- httr::GET(url = q)

    # check status code before continuing
    check_status_code(response$status_code)

    # extract the data as a list
    data <- httr::content(response)

    # bind each element of the list together to form a data frame
    data_list[[index]] <- t(data.frame(do.call(rbind, data)))

    # rename the columns
    if(var == "cs"){
      colnames(data_list[[index]]) <- get_column_names(query = q,
                                                     names = colnames(data_list[[index]]))

    # remove any columns that are already in the first data frame
    if(index > 1 & !is.null(colnames(data_list[[1]])) ){
      to_remove <- which(colnames(data_list[[index]]) %in% colnames(data_list[[1]]))
      data_list[[index]] <- data_list[[index]][,-to_remove]
    }

    }

    if(var == "wid"){
      drought_level = NULL
      for(d in 0:4){
        if(grepl(paste0("dx=",d),q)){
          drought_level = paste0("D",d)
        }
      }

      # replace the gsubs with direct assignment
      colnames(data_list[[index]])[which(colnames(data_list[[index]]) == "NonConsecutiveWeeks" )] <- paste0(drought_level,"_NonConsecutiveWeeks")
      colnames(data_list[[index]])[which(colnames(data_list[[index]]) == "ConsecutiveWeeks" )] <- paste0(drought_level,"_ConsecutiveWeeks")

    }

    # advance index
    index <- index + 1
  }


  if(var == "wid"){
    data <- data.frame(data_list[[1]]) # applied to wid data
    data <- data %>% dplyr::select(-contains("Date"))
    for(k in 2:length(data_list)){
      data <- dplyr::full_join(data, data.frame(data_list[[k]]), by = c("FIPS","County","State"))
      data <- data %>% dplyr::select(-contains("Date"))
    }
  } else{
    data <- do.call(cbind, data_list) # applies to cs data
  }


  # remove the list formatting from each column
  # Note: I've had alot of trouble trying to vectorize
  # this for loop for some reason.
  for(i in seq_len(ncol(data))){
    data[,i] <-unlist(data[,i])
  }

  # make sure data is in data frame format
  data <- data.frame(data)

  # convert columns to numeric
  for(i in seq_len(ncol(data))){
    if(grepl("None|D0|D1|D2|D3|D4",colnames(data)[i])){
      # remove comma and convert to numeric
      data[,i] <- as.double(gsub(",","",data[,i]))
    }
  }

  # clean area of interest column
  if("AreaOfInterest" %in% colnames(data)){
    data$AreaOfInterest <- gsub("Total", "Total U.S.",data$AreaOfInterest)
  }

  # convert MapDate to a POSIX object
  if("MapDate" %in% colnames(data)){
    map_year <- substr(data$MapDate,1,4)
    map_month <- substr(data$MapDate,5,6)
    map_day <- substr(data$MapDate,7,8)
    data$MapDate <- as.Date(paste(map_year,map_month, map_day,sep="-"),
                                  "%Y-%m-%d")
  }

  # remove columns that aren't needed
  to_remove <- c("ValidStart","ValidEnd","StatisticFormatID")
  if(T %in% (colnames(data) %in% to_remove )){
    data <- data[,-which(colnames(data) %in% to_remove)]
  }

  if(var == "wid"){

    data <- data %>% dplyr:: group_by(FIPS, County, State) %>%
      dplyr::summarize_all(max)

    data$StartDate <- start_date
    data$EndDate <- end_date
  }

  # convert the data to a tibble
  data <- tibble::as_tibble(data)

  # return the data
  return(data)
}






