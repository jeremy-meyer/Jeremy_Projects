# 06-observeEvent
# Triggers code to run on the server by waiting for a value to change. 

library(shiny)

ui <- fluidPage(
  sliderInput(inputId = "num", 
    label = "Choose a number",
    min = 1, max = 100, value = 25),
  actionButton(inputId = "go", 
    label = "Print Value")
)

server <- function(input, output) {
  
  # observe responds to the print button
  # but not the slider
  observeEvent(input$go, {
    print(as.numeric(input$num))
  })
}

shinyApp(ui = ui, server = server)

# Inside code of observe event acts as if under isolate(). Can use reactive values without functions
# observe({code}): will trigger whenever any code inside is invalidated. 