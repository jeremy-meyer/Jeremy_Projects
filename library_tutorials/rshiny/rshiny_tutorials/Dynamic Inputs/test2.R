library(shiny)
library(shinydashboard)
library(ggplot2)

datasets <- function() {
  tmp <-  unlist(
    sapply(ls("package:datasets"), function(x){
      "data.frame" %in% class(get(x))
    })
  )
  names(tmp[tmp])
}

s
apply.funUI <- function(id){
  ns <- NS(id)
  box(title='Module: Transform data', solidHeader=TRUE, background='green',
      radioButtons(ns('fun'), label='Select a Function', choices=c('x','log(x)', 'abs(x)', 'sqrt(x)')))
  
}

show.dataUI <- function(id){
  ns <- NS(id)
  box(title='Module: Showing the data' , background='blue', plotOutput(ns('fun_dataH')), verbatimTextOutput(ns('fun_dataS')))
  
}

load.dataUI <-function(id){
  ns <- NS(id)
  box(title='Module: Load Data', solidHeader=TRUE, background='red',
      selectInput(ns('dataset'), label='Select a Dataset', choices=datasets()), 
      selectInput(ns("SI_colname"), label = paste("Choose", "numeric variable"), choices = NULL),
      actionButton(ns("AB_load"), label = "Load Data!"))
}

apply.fun <- function(input, output, session, data=reactive(iris[,1])){
  dat.new <- reactiveValues()
  dat.new$fun <- reactive(input$fun)
  dat.fun <- reactive({function(x) eval(parse(text=input$fun))})
  dat.new$newDat <- reactive({dat.fun()(data())})
  return(dat.new)
}

show.data <- function(input, output, session, dat.rvs){
  output$fun_dataH <- renderPlot({
    # ggplot(dat.rvs$newDat()) + geom_histogram(aes(y=..density..), bins=30, fill=I("blue"), col=I("red"), alpha=I(.3), bins=30)
    qplot(dat.rvs$newDat(), geom='histogram', main=paste0('Transformed (', dat.rvs$fun(), ') Data'),
          fill=I("blue"), 
          col=I("red"), 
          alpha=I(.3), bins=30)
  })
  output$fun_dataS <- renderPrint(summary(dat.rvs$newDat()))
}

load.data <- function(input, output, session){
  
  toReturn    <-  reactiveValues(
    variable = NULL,
    variable_name = NULL,
    trigger = 0
  )
  
  observe({
    if (!is.null(input$dataset)) {
      df <- get(input$dataset)
      choices <- colnames(df)[sapply(df, is.numeric)]
      updateSelectInput(session, "SI_colname", choices = choices)
    }
  })
  
  observeEvent(input$AB_load, {
    toReturn$variable       <- get(input$dataset)[,input$SI_colname]
    toReturn$variable_name  <- input$SI_colname
    toReturn$trigger        <- toReturn$trigger + 1
    print(class(toReturn$variable))
  })
  print(isolate(class(toReturn$variable)))
  return(toReturn)
}


# Dashboard Page Has three parts, a header, sidebar and body. Using Iris dataset
ui <- dashboardPage(skin='blue',
        dashboardHeader(title='Apply Function'),
        dashboardSidebar(sidebarMenu(
          menuItem("Tab1", tabName = "tab1", icon = icon("list")),
          menuItem("Tab2", tabName = "tab2", icon = icon("box"))
        )),
        dashboardBody(tabItems(
          tabItem(tabName = 'tab1',
                  fluidRow( load.dataUI('id3'),
                            apply.funUI('id1')
                  ), 
                  fluidRow(show.dataUI('id2')))
          
          
        ))
)

server <- function(input, output) {
  dat <- callModule(load.data, id='id3')
  print(str(dat))
  data.fun <- callModule(apply.fun, id='id1', data=reactive(iris[,2]))
  callModule(show.data, id='id2', data.fun)
  
}

shinyApp(ui, server)