library(shiny)
library(datasets)

shinyApp(
  ui = fluidPage(
    titlePanel('Using renderUI'),
    sidebarLayout(
      sidebarPanel(
        selectInput('data', 'Choose a dataset', c('rock', 'pressure', 'cars')),
        radioButtons('tool', 'Choose a tool', c('summary', 'plot', 'head')),
        uiOutput('nObs')
      ),
      mainPanel(
        uiOutput('result')
      )
    )
  ),
  server = function(input, output, session) {
    dataset <- reactive({ get(input$data)})
    
    output$nObs <- renderUI({
      if (input$tool == 'head'){
        numericInput('nObs', 'Number of Observations', 5,1,nrow(dataset()))
      }
    })
    
    output$result <- renderUI({
      switch(input$tool,
             'summary' = verbatimTextOutput('summary'),
             'plot' = plotOutput('plot'),
             'head' = tableOutput('head'))
    })
    
    output$summary <- renderPrint({ summary(dataset()) })
    output$plot <- renderPlot({ plot(dataset()) })
    output$head <- renderTable({ 
      head(dataset(), ifelse(is.null(input$nObs), 5, input$nObs)) 
    })
  }
)