# Module UI

#' @title   mod_tab1_ui
#' @description  A shiny Module.

#' @param id shiny id
#' @param input internal
#' @param output internal
#' @param session internal
#'
#' @rdname tab1
#'
#' @keywords internal
#' @export 
#' @importFrom shiny NS tagList
#' @importFrom golem get_golem_options
mod_tab1_ui <- function(id){
  ns <- NS(id)
  fluidPage(
    fluidRow(h2(get_golem_options('msg')),
      sliderInput(ns('nbin'), 'Select the number of bins', min=1, max=100, value=10)),
    fluidRow(column(9,  
                    plotOutput(ns('hist'))),
             column(3,
                    valueBox(
                      textOutput(ns('mean_box')), 'Mean', width=12, color='blue', icon('list'))
                    
                    ,valueBox(
                      textOutput(ns('var_box')), 'Variance', width=12, icon('list-ol'))
                    ,
                    actionButton(ns("browser"), "Debug First Tab"),
                    tags$script("$('#browser').hide();")
             )
    )
  )
}