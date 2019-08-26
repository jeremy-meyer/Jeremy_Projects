


contact_rate_ui <- function(id, label = "contact_rate"){

  ns <- shiny::NS(id)

  tabItem(
    tabName = "contact_rate",

    fluidRow(
      
      valueBox(
        uiOutput(ns('total_calls')), "Total Calls"
        , color = "green"
        ,icon = icon("phone")
        , width = 4
      ), 
      valueBox(
        uiOutput(ns('active_accounts')), "Active Accounts"
        , color = "blue"
        ,icon = icon("users")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('call_rate')), "Calls per Active Account"
        , color = "purple"
        ,icon = icon("phone-volume")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('registered_accounts')), "Registered Accounts"
        , color = "light-blue"
        ,icon = icon("registered")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('login_accounts')), "Logged in Accounts"
        , color = "teal"
        ,icon = icon("sign-in")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('activity_count')), "Active Users"
        , color = "aqua"
        ,icon = icon("sign-in")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('registered_rate')), "Registration % of Active Accounts"
        , color = "light-blue"
        ,icon = icon("registered")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('login_rate')), "Login % of Active Accounts"
        , color = "teal"
        ,icon = icon("sign-in")
        , width = 4
      ),
      valueBox(
        uiOutput(ns('activity_rate')), "Active Users % of Accounts"
        , color = "aqua"
        ,icon = icon("percent")
        , width = 4
      )
    ),
      
    fluidRow(
      box(width=3,

             awesomeRadio(
               inputId = ns("time_view"),
               label = "Select Timeview", 
               choices = c('Month' = 'month', "Week" = 'week', "Day" = 'day'),
               selected = 'week'
             ),
             
             awesomeCheckboxGroup(
               inputId = ns("product"),
               label = "Select Product", 
               choices = c("RTO" = 'RTO', "Snap Loan" = 'SLN', "Credit Plus" = 'SSL'),
               selected = "RTO"
             )
             
             ,pickerInput(
               inputId = ns("disposition_service"),
               label = "Select Disposition",
               choices = sort(c("AGENT","PARKING_SERVICE","IVR","VOICE_MAIL","FIRST_HOP",'NA')),
               selected = c("AGENT","PARKING_SERVICE"),
               options = list(
                 `actions-box` = TRUE,
                 size = 10,
                 `selected-text-format` = "count > 4"
               ),
               multiple = TRUE
             )
             , pickerInput(
               inputId = ns("skill_group"),
               label = "Select Skill Group",
               choices = sort(c('Spanish','Customer Service English','Customer Service Spanish','English',
                                'After Hours','Snap Loan English','Merchant Line Main',
                                'Snap Loan Spanish',
                                'After Hours English','After Hours Spanish',
                                'Emergency Closure','Closure','English Skill',
                                'Late Stage English','Emergency Closure Spanish',
                                'NA')),
               selected = c('Spanish','Customer Service English','Customer Service Spanish', 'English',
                            'Spanish Line',
                            'Merchant Line Main',
                            'English Skill',
                            'Late Stage English'
               ),
               options = list(
                 `actions-box` = TRUE,
                 size = 10,
                 `selected-text-format` = "count > 3"
               ),
               multiple = TRUE
             
          )),
          column(9, 
                 tabBox(width=12, 
                    tabPanel('Graph',
                    fluidRow(
                      column(1),
                    column(3,
                       awesomeRadio(
                         inputId = ns("view_type"),
                         label = "", 
                         choices = c("Individual Metric" = 'Individual', "Funnel")
                       )),         
                      uiOutput(ns("cr_view")),
                      column(12,highchartOutput(ns('cr_graph')))
                    )), 
                    tabPanel('Table', 
                    
                      fluidRow(column(12,dataTableOutput(ns('cr_table'))))
          )
        )
      
     )

    
      
    )
  )
}

