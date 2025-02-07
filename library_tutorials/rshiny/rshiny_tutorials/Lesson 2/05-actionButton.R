# 05-actionButton

library(shiny)

ui <- fluidPage(
  actionButton(inputId = "clicks", 
    label = "Click me"), textOutput('numClicks')
)

server <- function(input, output) {
  observeEvent(input$clicks, {
    print(as.numeric(input$clicks))
  })
  output$numClicks <- renderText(paste('Number of Clicks:', input$clicks))
}

shinyApp(ui = ui, server = server)