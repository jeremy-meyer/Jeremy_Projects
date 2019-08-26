library(shinydashboard)

ui <- dashboardPage(skin='red',
  # Dashboard Header with dropdown menus
  # dashboardHeader(disable = TRUE) # To Disable
  dashboardHeader(title = "Title Goes Here", 
  dropdownMenu(type = "notifications",
    messageItem(
      from = "Code",
      message = "This is how you create a user defined message.",
      icon = icon('life-ring')
    ),
    notificationItem(
      text= paste('Current Date', paste(unlist(strsplit(date(), ' '))[c(1:3,5)], collapse=' '))
    )
  ),
  # Tasks
  dropdownMenu(type = "tasks",
    taskItem(value = 90, color = "green",
             "Documentation"
    ),
    taskItem(value = 17, color = "aqua",
             "Project X"
    )
  )),
  
  # Sidebar options
  # The tabnames must match the tabNames in the tab items function
  dashboardSidebar(
    sidebarMenu(
      sidebarSearchForm(textId = "searchText", buttonId = "searchButton",
                        label = "Search..."),
    menuItem("Tab Name goes here", tabName = "dashboard", icon = icon("dashboard")),
    menuItem("Dynamic Widgets", tabName = "Dynamic_Widgets", icon = icon("th"),
             badgeLabel = "NEW!", badgeColor = "orange"),
    menuItem("Boxes", tabName = "boxes", icon = icon("box")),
    textInput('sideText', 'Title', value = 'Graph Title'), # Also make inputs!
    
    # Can create Hyper Links in shiny dashboard
    menuItem("LINK: Help-Dashboards", icon = icon("file-pdf"), 
             href = "https://rstudio.github.io/shinydashboard/structure.html#header"),
    menuItem("URL: Cheat Sheet", icon = icon("link"), 
             href = "https://shiny.rstudio.com/images/shiny-cheatsheet.pdf")

    )
  ),
  dashboardBody(
    tabItems(
      # First tab content
      tabItem(tabName = "dashboard",
    # Boxes need to be put in a row (or column)
    fluidRow(
      box(plotOutput("plot1", height = 250)),
      
      box(
        title = "Controls",
        sliderInput("slider", "Number of observations:", 1, 100, 50)
      )
    )
      ), 
    # Second tab content
    tabItem(tabName = "Dynamic_Widgets",
            titlePanel("Dynamically generated user interface components"),
            fluidRow(
              # MUST SPECIFY WIDTH=NULL
              column(4, wellPanel( # Column layouts 
                                    selectInput("input_type", "Select Type",
                                    c("slider", "text", "numeric", "checkbox",
                                    "checkboxGroup", "radioButtons", "selectInput",
                                    "selectInput (multi)", "date", "daterange")
                                  )), 
                                      box(
                                        title = "Box Title", width = NULL, background = "light-blue",
                                        "This is how we stack boxes vertically")
                                  ),
              
              column(4, wellPanel(
                # This outputs the dynamic UI component
                uiOutput("ui_tab2")
              ))
            
    )
    ),
    # Third Tab
    tabItem(tabName = 'boxes',
      fluidRow(box(title = "Graph", status = "primary", plotOutput("plot3", height = 250), solidHeader = TRUE),
      
      box(
        title = "Inputs", collapsible = TRUE, background = "black",
        "Box content here", br(), "More box content", # If We want to add text into a line
        sliderInput("slider3", "Weibull Shape:", .5, 20, 5, step = .5),
        textInput("text3", "Box Color", value='yellow')
      )),
      
      fluidRow(valueBoxOutput('t3mean'), valueBoxOutput("t3box"))
    
                    
    )
  )
))


server <- function(input, output) {
  set.seed(122)
  histdata <- rnorm(500)
  
  output$plot1 <- renderPlot({
    data <- histdata[seq_len(input$slider)]
    hist(data, main= input$sideText)
  })
  
  output$ui_tab2 <- renderUI({
    switch(input$input_type,
           "slider" = sliderInput("dynamic", "Slider",
                                  min = 1, max = 20, value = 10),
           "text" = textInput("dynamic", "Text",
                              value = "starting value"),
           "numeric" =  numericInput("dynamic", "Numeric",
                                     value = 12),
           "checkbox" = checkboxInput("dynamic", "Checkbox",
                                      value = TRUE),
           "checkboxGroup" = checkboxGroupInput("dynamic", "Checkbox - Group",
                                                choices = c("Option 1" = "option1",
                                                            "Option 2" = "option2"),
                                                selected = "option2"
           ),
           "radioButtons" = radioButtons("dynamic", "Radio",
                                         choices = c("Option 1" = "option1",
                                                     "Option 2" = "option2"),
                                         selected = "option2"
           ),
           "selectInput" = selectInput("dynamic", "Select",
                                       choices = c("Option 1" = "option1",
                                                   "Option 2" = "option2"),
                                       selected = "option2"
           ),
           "selectInput (multi)" = selectInput("dynamic", "Select (multi)",
                                               choices = c("Option 1" = "option1",
                                                           "Option 2" = "option2"),
                                               selected = c("option1", "option2"),
                                               multiple = TRUE
           ),
           "date" = dateInput("dynamic", "Dynamic"),
           "daterange" = dateRangeInput("dynamic", "Dynamic")
    )
    
  })
  
  output$plot3 <- renderPlot({
    curve(dweibull(x, input$slider3, 1), xlim=qweibull(c(.005,.995), input$slider3, 1), main='Weibull Dist Curve', lwd=2)
  })
  
  output$t3mean <- renderValueBox({
    valueBox(
      round(gamma(1+1/input$slider3),3), "Mean", icon = icon("list"),
      color = "blue"
    )
  })
  
  output$t3box <- renderValueBox({
    m <- 1*gamma(1+1/input$slider3) 
    valueBox(
      paste0(round(pweibull(m, input$slider3, 1),3)*100, "%"), "Percent below the mean", icon = icon("list"),
      color = input$text3
    )
  })
}

shinyApp(ui, server)