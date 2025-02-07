# 04-isolate

library(shiny)

ui <- fluidPage(
  sliderInput(inputId = "num", 
    label = "Choose a number", 
    value = 25, min = 1, max = 100),
  textInput(inputId = "title", 
    label = "Write a title",
    value = "Histogram of Random Normal Values"),
  plotOutput("hist")
)

server <- function(input, output) {
  output$hist <- renderPlot({
    hist(rnorm(input$num), main = isolate(input$title))
  })
}

shinyApp(ui = ui, server = server)

# Isolate - creates a result that is NOT reactive. Cuts off "downstream" code to update
# This means, the title won't react to changes in the text box, only when code that depends on it is invalidated
# Use isolate() to treat reactive values as normal R values