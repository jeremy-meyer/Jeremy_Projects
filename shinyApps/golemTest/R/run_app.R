#' This will run the hello world example app.
#' Type right here to document code
#' 
#' @param msg Title heading to put on first tab
#' 
#' @return No return value, it just runs the app!
#' 
#' @examples
#' golemTest::run_app()
#' run_app()
#' 
#' @export
#' @importFrom shiny shinyApp
#' @importFrom golem with_golem_options
# Import allows you to use the whole namespace without loading the functions. Alt to ::

run_app <- function(msg='INSERT TITLE HERE') {
  with_golem_options(
    app = shinyApp(ui = app_ui, server = app_server), 
    golem_opts = list(msg=msg)
  )
}

