# remotes::install_github("ardata-fr/Shiny-Modules-Tutorials")
datasets <- function() {
  tmp <-  unlist(
    sapply(ls("package:datasets"), function(x){
      "data.frame" %in% class(get(x))
    })
  )
  names(tmp[tmp])
}


load_dataUI <- function(id) {
  ns <- NS(id)
  
  shinyjs::useShinyjs()
  fluidRow(
    column(12,
           selectInput(ns("SI_dataset"), label = "Dataset", choices = datasets(), selected = "iris"),
           selectInput(ns("SI_var"), label = "Choose variable", choices = NULL),
           shinyjs::disabled(actionButton(ns("AB_load"), label = "(Re) load !"))
    )
  )
}


load_data <- function(input, output, session) {
  
  ns <- session$ns
  
  # Define the ReactiveValue to return : "toReturn"
  # with slots "variable", "variable_name" & "trigger"
  toReturn    <-  reactiveValues(
    variables = NULL,
    variable_name = NULL,
    trigger = 0
  )
  
  # Update selectInput according to dataset
  observe({
    if (!is.null(input$SI_dataset)) {
      df <- get(input$SI_dataset)
      choices <- colnames(df)[sapply(df, is.numeric)]
      updateSelectInput(session, "SI_var", choices = choices)
    }
  })
  
  # Enable / Disable (Re)load button
  observe({
    req(input$SI_var)
    if (input$SI_var != "") {
      shinyjs::enable("AB_load")
    } else {
      shinyjs::disable("AB_load")
    }
  })
  
  # (Re)load button
  observeEvent(input$AB_load, {
    toReturn$variable       <- get(input$SI_dataset)[,input$SI_var]
    toReturn$variable_name  <- input$SI_var
    toReturn$trigger        <- toReturn$trigger + 1
  })
  
  return(toReturn)
}


# App ---------------------------------------------------------------------
library(shiny)
library(shinyModulesTuto)

ui <- fluidPage(
  #loadModulesCSS("modules_styling.css"),
  
  fluidRow(
    column(12,
           h1("Data from Module to Application"),
           
           # module UI
           load_dataUI(id = "id1"),
           tags$hr(),
           
           # Print the numeric vector
           uiOutput("ui_PR_results_print")
    )
  )
)

server <- function(input, output, session) {
  
  # Create reactiveValues from module outputs
  # 3 slots returned :
  #   - variable (the numeric vector)
  #   - variable_name (name of the variable)
  #   - trigger (not used here)
  results <- callModule(module = load_data, id = "id1")
  
  # Print results$variable
  output$PR_results_print <- renderPrint({
    print(results$variable)
  })
  
  # Set the verbatimTextOutput inside renderUI with a title "h3"
  output$ui_PR_results_print <- renderUI({
    if (is.null(results$variable)) {
      tags$span(class = "warn", "No dataset loaded")
    } else {
      tags$div(
        h3(results$variable_name),
        verbatimTextOutput("PR_results_print")
      )
    }
  })
}

# Run the application
shinyApp(ui = ui, server = server)


