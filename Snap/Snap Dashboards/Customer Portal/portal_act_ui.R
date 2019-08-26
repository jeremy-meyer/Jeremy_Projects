
portal_act_ui <- function(id){
  ns <- NS(id)
  fluidPage(
    fluidRow(
      valueBox(
        uiOutput(ns('tot_reg')), "Accounts Registered"
        , color = "blue"
        ,icon = icon("registered")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('port_log')), "Logged In Accounts"
        , color = "teal"
        ,icon = icon("users")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('acc_pdo')), "Accounts Paid Off"
        , color = "green"
        ,icon = icon("user-check")
        , width = 3
      ),
    
      valueBox(
        uiOutput(ns('card_add')), "Card Added"
        , color = "yellow"
        ,icon = icon("plus")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('card_chg')), "Card Changed"
        , color = "navy"
        ,icon = icon("credit-card")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('card_pmt')), "Card Payment Created"
        , color = "purple"
        ,icon = icon("money-check-alt")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('man_pmt')), "Manual Payment Posted"
        , color = "maroon"
        ,icon = icon("file-invoice-dollar")
        , width = 3
      ),
      
      valueBox(
        uiOutput(ns('pmt_met')), "Payment Method Changed"
        , color = "fuchsia"
        ,icon = icon("handshake")
        , width = 3
      )
      

      
      ),
    
    fluidRow(box(width=2,
                 
                 materialSwitch(
                   inputId = ns("perc"),
                   label = HTML(paste0('<font size="3">', tags$b("View as Percentages"), '</font>')), 
                   status = "primary"
                 ),
                 
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
             
             ), 
      
      column(10,
        tabBox(width=12 
             ,tabPanel('Graph', 
                       fluidPage(
                         fluidRow(
                          uiOutput(ns('graph_opt'))
                          ),
                         fluidRow(highchartOutput(ns('pa_graph')))
                       )
              )
             ,tabPanel('Table',
                       fluidRow(column(12,dataTableOutput(ns('pa_table')))))
      )
     
    )
  )
  )
  
}