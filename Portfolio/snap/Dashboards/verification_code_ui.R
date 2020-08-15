library(shiny)
library(shinydashboard)
library(shinyBS)
library(shinydashboardPlus)

# UI only module
dashboard_verification_codeUi <- function(id, color='#000000'){
  ns <- NS(id)
  text <- getSupportCode()
  dropdownBlock(
    id = ns("supp_id")
    ,title = "Merchant Support Verification Code"
    ,icon='headset'
    ,badgeStatus=NULL
    ,bsPopover(ns('supp_id'), title='Verification Code', content=HTML(paste0(
      '<p1><font color="', color,'", size="6">', tags$b(text), '</font></p1>')))
  )
}

getSupportCode <- function(){
  return(12345)
}


ui <- dashboardPage(dashboardHeaderPlus(
                      title = "Credit+ Sales"
                      ,titleWidth = 250
                      ,left_menu = tagList(
                         tags$head(
                           tags$style(HTML('
                                          p1 {
                                           letter-spacing: 0.1em;   
                                          }
                                        ')
                                      )
                           )
                        ,dashboard_verification_codeUi('dashboard_vc', color='#0078c8')
                      )),
                    dashboardSidebar(
                      sidebarMenu(
                        menuItem("Tab Name goes here", tabName = "tab1", icon = icon("dashboard")),
                        menuItem("Tab Name goes here 2", tabName = "tab2", icon = icon("dashboard"))
                      )
                    ),
                    dashboardBody(
                      tabItems(
                        tabItem(tabName = "tab1", box(title = "Box Title", width = NULL, background = "blue", "Tab 1 Text")),
                        tabItem(tabName = 'tab2')
                      )
                    )
)


server <- function(input, output) {}

shinyApp(ui, server)
