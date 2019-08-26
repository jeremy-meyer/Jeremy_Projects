# 03-reactive

library(shiny)

ui <- fluidPage(
  sliderInput(inputId = "num", 
    label = "Choose a number", 
    value = 25, min = 1, max = 100),
  plotOutput("hist"),
  verbatimTextOutput("stats")
)

server <- function(input, output) {
  
  # Cache data! However, this can only be used inside render() functions
  # Reactive values (input$num) need to be stored inside this function
  # When these functions become invalid, they notify code downstream
  # Makes objects to use in downstream code
  data <- reactive({
    rnorm(input$num)
  })
  
  output$hist <- renderPlot({
    title <- 'Histogram'        # You can put intermediate code in here
    hist(data(), main=title)    # We call data as if it's a function
  })
  output$stats <- renderPrint({
    summary(data())
  })
}

shinyApp(ui = ui, server = server)