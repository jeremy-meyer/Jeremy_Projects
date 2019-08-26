library(shiny)
ui <- fluidPage(
  selectInput("dataset", "Dataset", c("diamonds", "rock", "pressure", "cars")),
  uiOutput('bins'),
  uiOutput('rows1000'),  
  plotOutput('pl')
)


server <- function(input, output, session) {
  datasetInput <- reactive({
    get(input$dataset)
  })
  
  nrows <- reactive({
    nrow(datasetInput())
  })
  
  output$rows1000 <- renderUI({
    if (nrows() > 1000){
      checkboxInput("headonly", "Only use first 1000 rows")
    }
  })
  
  output$bins <- renderUI({
    
  })
  
  output$pl <- renderPlot({
    require(ggplot2)
    first1000 <- ifelse(is.null(input$headonly), FALSE, input$headonly)
    dat.to.plot <- datasetInput()[1:ifelse(first1000, 1000, nrows()),1]
    qplot(unlist(dat.to.plot), geom='histogram', xlab=colnames(datasetInput())[1], bins=14)
  })
}

shinyApp(ui, server)