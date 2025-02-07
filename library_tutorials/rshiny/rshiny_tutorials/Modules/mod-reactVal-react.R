
# Module ------------------------------------------------------------------

show_dataUI <- function(id) {
  ns <- NS(id)
  # Space for graph, number of bins, and summary
  fluidRow(
    column(12,
           uiOutput(ns("ui_PL_histogram_var")), 
           uiOutput(ns("ui_SLI_nb_bins")),
           verbatimTextOutput(ns("PR_summary_var"))
    )
  )
}

show_data <- function(input, output, session, variable = NULL, variable_name = NULL, useggplot = TRUE) {
  
  ns <- session$ns
  
  # If useggplot, then SliderInput for number of bins
  output$ui_SLI_nb_bins <- renderUI({
    if (!is.null(variable()) && useggplot) {
      sliderInput(ns("SLI_nb_bins"), label = "Number of bins", min = 5, max = 100, value = 30)
    }
  })
  
  # Histogram
  output$PL_histogram_var <- renderPlot({
    if (useggplot) {
      require(ggplot2)
      qplot(variable(), geom = "histogram", 
            bins = input$SLI_nb_bins, main = "", xlab = variable_name(),
            fill = I("blue"), col = I("red"), alpha = I(0.2))
    } else {
      hist(variable(), main = variable_name(), xlab = NULL)
    }
  })
  
  # Use a renderUI of renderPlot to print "no dataset loaded" if no data
  output$ui_PL_histogram_var <- renderUI({
    if (is.null(variable())) {
      tags$span(class = "warn", "No dataset loaded")
    } else {
      plotOutput(ns("PL_histogram_var"))
    }
  })
  
  # Summary
  output$PR_summary_var <- renderPrint({
    req(variable())
    print(summary(variable()))
  })
}

# App ---------------------------------------------------------------------


library(shiny)
library(shinyModulesTuto)

ui <- fluidPage(
  #loadModulesCSS("modules_styling.css"),
  
  fluidRow(
    column(12,
           h1("Data from Application to Module"),
           selectInput("SI_colname", label = "Choose iris numeric variable",
                       choices = colnames(iris)[which(sapply(iris, is.numeric))]),
           
           h2("Solution 1 : Using a reactive"),
           show_dataUI(id = "id1"),
           tags$hr(), # Horizontal Line
           
           h2("Solution 2 : Using a reactiveValues"),
           show_dataUI(id = "id2")
    )
  )
)

server <- function(input, output, session) {
  
  ####################################+
  ## Solution 1 : Using a reactive ####
  ####################################+
  {
    # Reactive containing numeric vector
    variable <- reactive({
      iris[, input$SI_colname]
    })
    
    # Get histogram and summary with module show_data
    callModule(module = show_data, id = "id1",
               variable = variable,
               variable_name = reactive(input$SI_colname))
  }
  
  ##########################################+
  ## Solution 2 : Using a reactiveValues ####
  ##########################################+
  {
    # Create & update reactiveValues
    rv <- reactiveValues(variable = NULL)
    
    observe({
      rv$variable <- iris[, input$SI_colname]
    })
    
    callModule(module = show_data, id = "id2",
               variable = reactive(rv$variable),
               variable_name = reactive(input$SI_colname))
  }
  
}

# Run the application
# shinyApp(ui = ui, server = server, options = list(display.mode = "showcase"))
shinyApp(ui = ui, server = server)
