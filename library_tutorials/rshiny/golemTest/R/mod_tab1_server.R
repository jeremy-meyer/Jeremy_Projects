#' @title mod_tab1_server
#' @description  Tab1 server module
#' @rdname tab1
#' @export
#' @keywords internal
#' @importFrom ggplot2 qplot
mod_tab1_server <- function(input, output, session){
  ns <- session$ns
  
  dat <- reactive(rand_data())
  output$hist <- renderPlot({
    qplot(dat(), bins=input$nbin, color=I('red'), fill=I('blue'), alpha=I(.5))
    # hchist(dat()) %>% 
    #   hc_plotOptions(column=list(binsNumber=input$nbin, borderWidth=5, borderColor='#666'))
  })
  
  observeEvent(input$browser,{
    browser()
  }) # $('#browser').show()
  
  output$mean_box <- renderText(mean(dat()))
  output$var_box <- renderText(var(dat()))
  
}