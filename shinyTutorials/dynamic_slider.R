library(shiny)
ui <- fluidPage(
  numericInput("num", "Maximum slider value", 5),
  uiOutput("slider"), textOutput('slider2')
)

server <- function(input, output) {
  output$slider <- renderUI({
    sliderInput("slider_val", "Slider", min = 0,
                max = input$num, value = 0)
  })
  output$slider2 <- renderText(input$slider_val) # To access the value  
}

shinyApp(ui = ui, server = server)
