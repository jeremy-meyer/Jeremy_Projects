library(shiny)
library(shinydashboard)

# Dashboard Page Has three parts, a header, sidebar and body
ui <- dashboardPage(skin='black',
  dashboardHeader(title='Dashboard Template'),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Tab Name goes here", tabName = "tab1", icon = icon("dashboard")),
      menuItem("Tab Name goes here 2", tabName = "tab2", icon = icon("dashboard"))
    )
  ),
  dashboardBody(
    tabItems(
      # First tab content
      tabItem(tabName = "tab1", box(title = "Box Title", width = NULL, background = "green", "Tab 1 Text")),
      tabItem(tabName = 'tab2')
    )
  )
)

server <- function(input, output) { }

shinyApp(ui, server)