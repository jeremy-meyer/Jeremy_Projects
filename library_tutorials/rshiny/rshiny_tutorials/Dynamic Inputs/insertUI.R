library(shiny)
library(datasets)
# Inserting UI

shinyApp(
  ui = fluidPage(
    titlePanel('Using insertUI'),
    sidebarLayout(
      sidebarPanel(
        selectInput('data', 'Choose a dataset', c('rock', 'pressure', 'cars')),
        radioButtons('tool', 'Choose a tool', c('summary', 'plot', 'head')),
        actionButton('add', 'Add result') # Counter for ID button
      ),
      mainPanel(
        div(id = 'placeholder')
      )
    )
  ),
  server = function(input, output, session) {
    dataset <- reactive({ switch(input$data,
                                 'rock' = rock, 'pressure' = pressure, 'cars' = cars)
    })
    
    observeEvent(input$add, {
      id <- paste0(input$tool, input$add)
      insertUI('#placeholder', 
               ui = switch(input$tool,
                           'summary' = verbatimTextOutput(id),
                           'plot' = plotOutput(id),
                           'head' = tableOutput(id))
      )
      output[[id]] <-
        if (input$tool == 'summary') renderPrint({ summary(isolate(dataset())) })
      else if (input$tool == 'plot') renderPlot({ plot(isolate(dataset())) })
      else if (input$tool == 'head') renderTable({ head(isolate(dataset())) })
    })
  }
)