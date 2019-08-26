#' @import shiny
app_server <- function(input, output,session) {
  golem::warning_dev('This app is in developer mode!\n')
  # List the first level callModules here
  callModule(mod_tab1_server, "my_tab1_1")
  callModule(mod_dev_mode_server, "dev_mode_ui_1")
}
