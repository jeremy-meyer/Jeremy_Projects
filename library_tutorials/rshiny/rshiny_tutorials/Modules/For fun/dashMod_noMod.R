
# Create an R shiny app that will allow us to manipulate iris dataset
# Use shiny dashboards

library(shiny)
library(shinydashboard)

# Dashboard Page Has three parts, a header, sidebar and body
ui <- dashboardPage(
  dashboardHeader(title = "Iris Dataset"),
  
  dashboardSidebar({
    sidebarMenu(
    menuItem("Hist", tabName = "tab1", icon = icon("dashboard")),
    menuItem("Test", tabName = "tab2", icon = icon("dashboard"))
    )
  }),
  
  dashboardBody(
    tabItems(
    tabItem(tabName = "tab1",
      
        fluidRow(  
        column(4, 
            box(title = "Controls", sliderInput("nBins", "Number of Bins:", 20,50,1), width=NULL),
            box(selectInput("SI_colname", label = "Choose iris numeric variable",
                        choices = colnames(iris)[which(sapply(iris, is.numeric))]), width=NULL)
            ),
        
        column(8, box(plotOutput("plot1")))
      )
    ),
    
    tabItem(tabName= 'tab2', 
            box(title = "Box Title", width = NULL, background = "light-blue", "Just to test if we can switch tabs"))
      
    )
  )
)

server <- function(input, output) {
  output$plot1 <- renderPlot({
    require(ggplot2)
    qplot(iris[,input$SI_colname], geom = "histogram", 
          bins = input$nBins, main = "", xlab = input$SI_colname,
          fill = I("blue"), col = I("red"), alpha = I(0.2))
    
  })
  
}

shinyApp(ui, server)