datasets <- function() {
  tmp <-  unlist(
    sapply(ls("package:datasets"), function(x){
      "data.frame" %in% class(get(x))
    })
  )
  names(tmp[tmp])
}

# GLOBAL
TAB_1 <- reactive('iris')
TAB_2 <- reactive('rock')

# Module for color box. 
# Note: Title is important as it provides the variable reference
color.boxUI <- function(id, ttl='Color Selection', key = strsplit(ttl, ' ')[[1]][1]){
  ns <- NS(id)
  box(title=ttl, width=NULL, sliderInput(ns(paste0('colR',key)), 'Red Component', 0,255,5,value=255),
      sliderInput(ns(paste0('colG',key)), 'Green Component', 0,255,5,value=0),
      sliderInput(ns(paste0('colB',key)), 'Blue Component', 0,255,5,value=0))
}


data.loaderUI <- function(id){
  ns <- NS(id)

  
  #print(paste('Choosing from', isolate(dat1()), 'Mod UI'))
  # print(sapply(data, is.numeric))
  # print(colnames(data)[sapply(data, is.numeric)])
  fluidRow(  
    column(3, 
           box(selectInput(ns("SI_colname"), label = paste("Choose", "numeric variable"),
                           choices = NULL), width=NULL),
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

  # Update selectInput according to dataset
  # Try seeing if you can put the options here instead
  
  d <- reactive(get(dat()))
  
  observe({
    #print(paste('updating inputs for', dat()))
    #print(colnames(d())[sapply(d(), is.numeric)])
    updateSelectInput(session, "SI_colname", choices = colnames(d())[sapply(d(), is.numeric)])
  })
  
  col.names <- reactive({
    cn <- colnames(d())
    #print('Checking NULL')
    if (input$SI_colname == ""){
      #print('NULL VALUE!, updating')
      updateSelectInput(session, "SI_colname", choices = cn[sapply(d(), is.numeric)])
    }
    cn
  })
  
  col.data <- reactive({
    #print(paste('Choosing from', dat(), 'Mod Server'))
    #print(input$SI_colname)

    d1 <- d()
    #print(col.names())
    #print(which(col.names() == input$SI_colname))
    unlist(d1[,which(col.names() == input$SI_colname)])
  })
  
  SI_inp <- reactive({input$SI_colname})
  
  output$plot1 <- renderPlot({
    require(ggplot2)
    validate(need(col.data(), message=''))
    col.bar <- rgb(input$colRBar, input$colGBar, input$colBBar, maxColorValue = 255)
    col.line <- rgb(input$colRLine, input$colGLine, input$colBLine, maxColorValue = 255)
    #print(paste(length(col.data()), 'Length'))
    #print(col.data())
    qplot(na.omit(col.data()), geom = "histogram", 
          bins = input$nBins, main = paste(dat(), 'Dataset'), xlab = input$SI_colname,
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
              data.loaderUI(id='id2')
              
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
    data.loaderUI(id='id3')
  })
  
  # callModule(data.loader, id= 'id3', reactive(input$dataset)) # Server side is NOT updating
  callModule(data.loader, id= 'id3', ds.react)
  
  
  
  
  
}

shinyApp(ui, server)