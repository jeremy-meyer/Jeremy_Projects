context("golem tests")

library(golem)
# Does the UI return a taglist?
test_that("UI returns a taglist?", {
  ui <- app_ui()
  expect_shinytaglist(ui)
})
# Does the server return a function?
test_that("Server is a function?", {
  server <- app_server
  expect_is(server, "function")
})

# Configure this test to fit your need
# Runs app, then 
test_that(
  "app launches",{
    skip_on_cran()
    skip_on_travis()
    skip_on_appveyor()
    x <- processx::process$new(
      "R", 
      c(
        "-e", 
        "setwd('../../'); pkgload::load_all();run_app()"
      )
    )
    Sys.sleep(5)
    expect_true(x$is_alive())
    x$kill()
  }
)








