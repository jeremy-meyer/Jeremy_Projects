#' @import shiny
#' @import shinydashboard
app_ui <- function() {
  tagList(
    # Leave this function for adding external resources
    golem_add_external_resources(),
    # List the first level UI elements here
    dashboardPage(skin='black',
                  dashboardHeader(title='Golem Hello World!'),
                  dashboardSidebar(
                    sidebarMenu(
                      menuItem("First Tab", tabName = "tab1", icon = icon("dashboard")),
                      menuItem("Test Tab", tabName = "tab2", icon = icon("dashboard")),
                      menuItem('Dev Tab', tabName='tab3', icon = icon('dashboard'))
                    )
                  ),
                  dashboardBody(
                    tabItems(
                      tabItem(tabName = "tab1", mod_tab1_ui("my_tab1_1")),
                      tabItem(tabName = 'tab2', box(title = "Box Title", width = NULL, background = "green", "Golem is about helping us build the app to poduction")),
                      tabItem(tabName= 'tab3', mod_dev_mode_ui("dev_mode_ui_1"))
                    )
                  )
    )
    
  )
}

#' @import shiny
golem_add_external_resources <- function(){
  
  addResourcePath(
    'www', system.file('app/www', package = 'golemTest')
  )
 
  tags$head(
    golem::activate_js(),
    golem::favicon()
    # Add here all the external resources
    # If you have a custom.css in the inst/app/www
    # Or for example, you can add shinyalert::useShinyalert() here
    #tags$link(rel="stylesheet", type="text/css", href="www/custom.css")
  )
}
