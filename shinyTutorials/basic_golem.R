library(shiny)
library(testthat)
# Testthat for HTML UIs
ui <- tagList(h1("Hello world!"))
htmltools::save_html(ui, "ui1.html") # Note that this saved a file
golem::expect_html_equal(ui, "ui1.html")
# Changes, so this shouldn't match
ui <- tagList(h2("Hello world!"))
golem::expect_html_equal(ui, "ui1.html")

# Other valid testing functions:
# expect_shinytag()
# expect_shinytaglist()


# Testing modules: returns html taglist
my_mod_ui <- function(id){
  ns <- NS("id")
  tagList(
    selectInput(ns("this"), "that", choices = LETTERS[1:4])
  )
}
my_mod_ui_test <- tempfile(fileext = "html")
htmltools::save_html(my_mod_ui("test"), my_mod_ui_test)
# Some time later, and of course saved in the test folder, 
# not as a temp file
golem::expect_html_equal(my_mod_ui("test"), my_mod_ui_test)


# Standard testthat things
context("launch")

library(processx)

testthat::test_that(
  "app launches",{
    # We're creating a new process that runs the app
    x <- process$new(
      "R", 
      c(
        "-e", 
        # As we are in the tests/testthat dir, we're moving 
        # two steps back before launching the whole package
        # and we try to launch the app
        "setwd('../../'); pkgload::load_all();run_app()"
      )
    )
    # We leave some time for the app to launch
    # Configure this according to your need
    Sys.sleep(5)
    # We check that the app is alive
    expect_true(x$is_alive())
    # We kill it
    x$kill()
  }
)

# Notes:
# All exported functions must be documented
# Can be built to a tar.gz file -> library(golemapp); run_app()
