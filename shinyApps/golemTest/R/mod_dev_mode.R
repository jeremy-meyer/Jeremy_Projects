# Module UI
  
#' @title   mod_dev_mode_ui and mod_dev_mode_server
#' @description  A shiny Module.
#'
#' @param id shiny id
#' @param input internal
#' @param output internal
#' @param session internal
#'
#' @rdname mod_dev_mode
#'
#' @keywords internal
#' @export 
#' @importFrom shiny NS tagList 
#' @importFrom golem app_dev
mod_dev_mode_ui <- function(id){
  ns <- NS(id)
  tagList( h2(paste('This app is currently in', ifelse(golem::app_dev(), 'Developer', 'Production'), 'mode')),
           uiOutput(ns('debug_button')),
  fluidRow(valueBox(uiOutput(ns('val_box')), subtitle = 'log_dev(10) Output', width=3))
           
  )
}
# ?golem::cat_dev()    



# Module Server
    
#' @rdname mod_dev_mode
#' @export
#' @keywords internal
    
mod_dev_mode_server <- function(input, output, session){
  ns <- session$ns
  
  output$debug_button <- renderUI({
    if(app_dev()) actionButton(ns('debug'), 'debug')
  })
  
  observeEvent(input$debug, browser())
  
  # Dev-dependent log function
  log_dev <- golem::make_dev(log)
  
  output$val_box <- renderText({
    log_dev(10)
  })
}
    
## To be copied in the UI
# mod_dev_mode_ui("dev_mode_ui_1")
    
## To be copied in the server
# callModule(mod_dev_mode_server, "dev_mode_ui_1")
 
