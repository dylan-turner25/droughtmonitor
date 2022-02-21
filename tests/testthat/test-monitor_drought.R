vcr::use_cassette("is_a_tibble", {
  test_that("returned objected is a tibble", {
    returned_obj <- monitor_drought(aoi = "01001",var = "cs",
                                    start_date = "1/1/2021",
                                    end_date = "12/31/2021")

    expect_equal(tibble::is_tibble(returned_obj), TRUE)
  })
})
