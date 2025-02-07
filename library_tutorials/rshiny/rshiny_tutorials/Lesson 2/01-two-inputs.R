# 01-two-inputs. Pretty straightforward. Use taglist() if you don't want fluidPage
# FluidRow - ensures apps appear on same line (as long as there is space in 12 unit grid)

library(shiny)

ui <- fluidPage(
  sliderInput(inputId = "num", 
    label = "Choose a number", 
    value = 25, min = 1, max = 100), # textOutput('numText'), 
    br(), br(), # Horizontal Space
  textInput(inputId = "title", 
    label = "Write a title",
    value = "Histogram of Random Normal Values"),
  plotOutput("hist")
)

server <- function(input, output) {
  # output$numText <- renderText(input$num)
  
  output$hist <- renderPlot({
    hist(rnorm(input$num), main = input$title)
  })
}

shinyApp(ui = ui, server = server)