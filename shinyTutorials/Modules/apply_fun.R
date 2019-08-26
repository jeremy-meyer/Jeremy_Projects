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
      selectInput(ns("SI_colname"), label = paste("Choose", "numeric variable"), choices = NULL))
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
  d <- reactive({
    get(input$dataset)
    })
  
  cn <- reactive({
    coln  <- colnames(d())
    if(input$SI_colname == ''){
      print('Null Value, updating selection!')
      updateSelectInput(session, inputId = "SI_colname", choices = coln[sapply(d(), is.numeric)])
    }
    coln
  })
  
  observe({
    print(paste('Using dataset', input$dataset))
    # print(cn())
    print(paste('Updating Selection...'))
    updateSelectInput(session, inputId = "SI_colname", choices = cn()[sapply(d(), is.numeric)])
  })
  
  col.data <- reactive({
    #print(isolate(input$SI_colname))
    unlist(d()[,which(cn() == input$SI_colname)])
  })
  
  print(isolate(cn()[sapply(d(), is.numeric)]))
  print(isolate(input$SI_colname))
  return(col.data)
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
  data <- callModule(load.data, id='id3')
  print(isolate(data()))
  data.fun <- callModule(apply.fun, id='id1', data=reactive(iris[,2]))
  callModule(show.data, id='id2', data.fun)
  
}

shinyApp(ui, server)