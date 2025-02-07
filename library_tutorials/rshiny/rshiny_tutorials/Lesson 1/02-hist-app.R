library(shiny)

## How do I lay out the interface?
## Contains both input and output functions. User interface function
ui <- fluidPage(
  sliderInput(inputId = "num", ## Behind the scenes name
    label = "Choose a number", ## Interface label
    value = 25, min = 1, max = 100),
  plotOutput("hist") ## Tells Shiny to reserve space for a plot
)

## Braces: AS many lines of code as you want
## How do I assemble the inputs into the outputs?
server <- function(input, output) {
  #output$name <- objects to display
  # Save into output = render function
  output$hist <- renderPlot({ ## "hist" has same name as character in output function. Output object is saved
    hist(rnorm(input$num)) ## We can access the num value from ui
  })
}

shinyApp(ui = ui, server = server)