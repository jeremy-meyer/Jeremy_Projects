datasets <- function() {
  tmp <-  unlist(
    sapply(ls("package:datasets"), function(x){
      "data.frame" %in% class(get(x))
    })
  )
  names(tmp[tmp])
}

TAB_1 <- 'iris'
TAB_2 <- 'rock'

# Module for color box. 
# Note: Title is important as it provides the variable reference
color.boxUI <- function(id, ttl='Color Selection', key = strsplit(ttl, ' ')[[1]][1]){
  ns <- NS(id)
  box(title=ttl, width=NULL, sliderInput(ns(paste0('colR',key)), 'Red Component', 0,255,5,value=255),
      sliderInput(ns(paste0('colG',key)), 'Green Component', 0,255,5,value=0),
      sliderInput(ns(paste0('colB',key)), 'Blue Component', 0,255,5,value=0))
}


data.loaderUI <- function(id, dat=TAB_1){
  ns <- NS(id)
  data <- get(dat)
  dat1 <- reactive({ifelse(class(dat)[1] =='character', dat, dat())}) # Converts to reactive value
  print(paste('Choosing from', isolate(dat1()), 'Mod UI'))
  # print(sapply(data, is.numeric))
  # print(colnames(data)[sapply(data, is.numeric)])
  fluidRow(  
    column(3, 
           box(selectInput(ns("SI_colname"), label = paste("Choose", isolate(dat1()), "numeric variable"),
                           choices = colnames(data)[sapply(data, is.numeric)]), width=NULL),
           box(title = "Controls", sliderInput(ns("nBins"), "Number of Bins:", 2,50,1,value=20),
                                    sliderInput(ns('trans'), 'Opaqueness (%)',0,100, 5, value=40), width=NULL)
           
          
    ),
    
    column(2, color.boxUI(id, 'Bar Color'),
           color.boxUI(id, 'Line Color')
           ),
    column(7, box(plotOutput(ns("plot1"), height=400), valueBoxOutput(ns('NAs'), width=NULL))
  )
  )
}

data.loader <- function(input, output, session, dat=TAB_1){
  ns <- session$ns

  dat1 <- reactive({ifelse(class(dat)[1] =='character', dat, dat())}) # Converts to reactive value
  
  col.data <- reactive({
    print(paste('Choosing from', dat1(), 'Mod Server'))
    print(input$SI_colname)
    d <- get(dat1())
    print(colnames(d))
    print(which(colnames(d) == input$SI_colname))
    unlist(d[,which(colnames(d) == input$SI_colname)])
  })
  
  output$plot1 <- renderPlot({
    require(ggplot2)
    validate(need(col.data(), message=''))
    col.bar <- rgb(input$colRBar, input$colGBar, input$colBBar, maxColorValue = 255)
    col.line <- rgb(input$colRLine, input$colGLine, input$colBLine, maxColorValue = 255)
    qplot(na.omit(col.data()), geom = "histogram", 
          bins = input$nBins, main = paste(dat1(), 'Dataset'), xlab = input$SI_colname,
          fill = I(col.bar), col = I(col.line), alpha = I(input$trans/100))
  })
  
  output$NAs <- renderValueBox({
    num_miss <- sum(is.na(col.data()))
    valueBox(
     num_miss, "Missing Values", icon = icon("list"),
      color = ifelse(num_miss == 0, 'green', 'red'), width=NULL
    )
  })
  
  }



library(shiny)
library(shinydashboard)

# Dashboard Page Has three parts, a header, sidebar and body
ui <- dashboardPage(
  dashboardHeader(title = "Module / Dashboard"),
  
  dashboardSidebar({
    sidebarMenu(
    menuItem("Hist", tabName = "tab1", icon = icon("dashboard")),
    menuItem("Hist2", tabName = "tab2", icon = icon("dashboard")),
    menuItem("Data", tabName = "tab3", icon = icon("dashboard")),
    menuItem("Test", tabName = "tab4", icon = icon("dashboard"))
    )
  }),
  
  dashboardBody(
    tabItems(
    tabItem(tabName = "tab1",
      data.loaderUI(id='id1')
    ),
    
    tabItem(tabName= 'tab2', 
      data.loaderUI(id='id2', TAB_2)
      
    ),
    
    tabItem(tabName= 'tab3', selectInput("dataset", label = "Choose a Dataset", choices = datasets()),
            uiOutput('allData')
            ),
  
    tabItem(tabName= 'tab4', 
            box(title = "Box Title", width = NULL, background = "light-blue", "Just to test if we can switch tabs"))  
  )
  )
)

server <- function(input, output) {
 callModule(data.loader, id = 'id1')
 callModule(data.loader, id = 'id2', TAB_2)
 
 ds.react <- reactive({input$dataset})
 
 output$allData <- renderUI({
   data.loaderUI(id='id3', input$dataset)
 })

 # callModule(data.loader, id= 'id3', reactive(input$dataset)) # Server side is NOT updating
 callModule(data.loader, id= 'id3', ds.react)
 
 
 
 
 
}

shinyApp(ui, server)