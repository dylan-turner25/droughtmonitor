test_that("http status code errors are returned", {
   expect_equal(check_status_code(200),NULL)
   expect_error(check_status_code(404),"HTTP status code: 404")
})
