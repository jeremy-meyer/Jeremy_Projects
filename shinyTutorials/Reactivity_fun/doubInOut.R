# Two Inputs / Two outputs

library(shiny)

# Define UI for application that draws a histogram
ui <- fluidPage(
    headerPanel("Summary Statistics and histogram"),
    sliderInput(inputId='num',
    label='Sample Size:',
    value = 25, min=1, step=50,max=1000), 
    textInput('title', 'Histogram Title:', value='Histogram'),
    plotOutput('hist'),                  # Reserves space for output stuff! 
    verbatimTextOutput('stats')          # Puts histogram above summary statistics

)

# Define server logic required to draw a histogram
server <- function(input, output) {
    # Reactive function. Needed because data is needed for both hist and stats. 
    # Reactive (input value) also needs to be inside reactive function
    data <- reactive({          
        rnorm(input$num)
    })
    
    # In the appropriate output spaces called in the UI page:
    output$hist <- renderPlot({ # Call reactive value using a function
      hist(data(), breaks=ceiling(input$num/6), main=isolate({input$title}))  
      # Title only changes if something else is updated
    })
    output$stats <- renderPrint({
        summary(data())
    })
    
}

# Run the application 
shinyApp(ui = ui, server = server)
