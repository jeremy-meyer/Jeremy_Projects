ui <- fluidPage(
  selectInput("dataset", "Dataset", c("diamonds", "rock", "pressure", "cars")),
  conditionalPanel( condition = "output.nrows > 1000", # Condition used output values
                    checkboxInput("headonly", "Only use first 1000 rows")), 
  plotOutput('pl')
)


server <- function(input, output, session) {
  datasetInput <- reactive({
    get(input$dataset)
  })
  
  nrows <- reactive({
    nrow(datasetInput())
  })
  
  output$nrows <- nrows
  
  outputOptions(output, "nrows", suspendWhenHidden = FALSE)  # THis is needed if outputs are referenced in the condition
  # However, this is inefficient, so avoid referencing outputs if necessary
  
  output$pl <- renderPlot({
    require(ggplot2)
    dat.to.plot <- datasetInput()[1:ifelse(input$headonly, 1000, nrows()),1]
    qplot(unlist(dat.to.plot), geom='histogram', xlab=colnames(datasetInput())[1], bins=14)
  })
}

shinyApp(ui, server)