
contact_rate_server <- function(input, output, session, date_range){

  ns <- session$ns
  CHOICES <- c("Active Accounts", "Registered Accounts", "Logged in Accounts", "Active User Count")
  CHOICES_COLS <- c('#003C50', '#0064FF', '#39CCCC', '#96bdff')
  
  call_account_data <- reactive({

    params_list <- list(from_date = date_range()[1], to_date = date_range()[2], time_view = input$time_view,
                        skill_group_name = input$skill_group, disposition_service = input$disposition_service,
                        product_type = input$product
                        )
    
    urls <- c('contactRate/accounts/in_time', 
              'contactRate/accounts/aggregate',
              'contactRate/calls/aggregate'
              )
    api_call(urls=urls, params_list = params_list)
  })
  
  
  accounts_in_time <- reactive({
    
    df <- call_account_data()[[fullPath('contactRate/accounts/in_time')]]
    
    shiny::validate(need(length(df)>0, 'No data available.'))
    
    df %>% mutate(date = as.Date(date),
                  calls = as.numeric(calls),
                  active_accounts = as.numeric(active_accounts),
                  login_registration = round(login_count/registered_count,4),
                  activity_count = as.numeric(activity_count)
    ) 
    
  })
  
  cr_data <- reactive({
    df <-  accounts_in_time() %>% 
      select('Date' = 'date', 
             'Active Accounts' = 'active_accounts',
             'Registered Accounts'= 'registered_count',
             'Logged in Accounts' = 'login_count',
             'Active User Count' = 'activity_count',
             'Calls Count' = 'calls',
             'Calls per Active Account' = 'call_rate',
             'Registration % of Active Accounts' = 'registered_rate',
             'Login % of Active Accounts' = 'login_rate',
             'Active Users % of Accounts' = 'activity_rate') %>% 
      
      mutate('Login % of Registration' = round(`Logged in Accounts`/`Registered Accounts`,4),
             'Active User % of Registration'=round(`Active User Count`/`Registered Accounts`,4),
             'Active User % of Logins' = round(`Active User Count`/`Logged in Accounts`,4))
    
  })
  
  
  output$cr_view <- renderUI({
    shiny::validate(need(!is.null(input$view_type), 'Loading'))
    
    if(input$view_type == 'Individual'){
      column(3, selectInput(ns("metric"), "Select Metric", choices=colnames(cr_data())[-1]))

    }else{

      list(column(3, 
                awesomeRadio(
                  inputId = ns("graph_type"),
                  label = "", 
                  choices = c('Raw Numbers', 'Percentages')
                )
             ), 
            column(3, uiOutput(ns('perc_option')))
          )
      }
  })
  
  output$perc_option <- renderUI({
    shiny::validate(need(!is.null(input$graph_type), 'Loading'))
    if(input$graph_type == 'Percentages'){
      awesomeRadio(
        inputId = ns("allmets_baseline"),
        label = "Select Baseline", 
        choices=CHOICES[-length(CHOICES)]
      )
    }
  })
  

  calls_in_aggregate <- reactive({
    df <- call_account_data()[[fullPath('contactRate/calls/aggregate')]]
    shiny::validate(need(length(df)>0, 'NA'))
    as.numeric(df$calls)
  })
  
  accounts_in_aggregate <- reactive({
    
    df <- call_account_data()[[fullPath('contactRate/accounts/aggregate')]]
    shiny::validate(need(length(df)>0, 'NA'))
    df$active_accounts <- as.numeric(df$active_accounts)
    df$login_count <- as.numeric(df$login_count)
    df$registered_count <- as.numeric(df$registered_count)
    df$registered_rate <- 100*as.numeric(df$registered_rate)  
    df$login_rate <- 100* as.numeric(df$login_rate)
    df$activity_rate <- 100* as.numeric(df$activity_rate)
    df
    
  })
  
  
  
  output$call_rate <- renderText({
    val <- round(calls_in_aggregate()/accounts_in_aggregate()$active_accounts,2)
    format(val, big.mark=',')
  })
  
  output$total_calls <- renderText({
    format(calls_in_aggregate(), big.mark=',')
  })
  
  output$active_accounts <- renderText({
    format(accounts_in_aggregate()$active_accounts, big.mark=',')
  })
  
  
  output$registered_accounts <- renderText({
    format(accounts_in_aggregate()$registered_count, big.mark=',')
  })
  
  output$login_accounts <- renderText({
    format(accounts_in_aggregate()$login_count, big.mark=',')
  })
  
  output$registered_rate <- renderText({
    paste0(format(accounts_in_aggregate()$registered_rate, big.mark=','),'%')
  })
  
  output$login_rate <- renderText({
    paste0(format(accounts_in_aggregate()$login_rate, big.mark=','),'%')
  })
  
  
  output$activity_rate <- renderText({
    paste0(format(round(accounts_in_aggregate()$activity_rate,2), big.mark=','),'%')
  })
  
  output$activity_count <- renderText({
    format(accounts_in_aggregate()$activity_count, big.mark=',')
  })
  
  
  
  
  output$cr_graph <- renderHighchart({
    
    shiny::validate(need(!is.null(input$view_type), 'Loading'))

    if(input$view_type=='Individual'){
      
      gb <- cr_data()
      perc.cols <- which(grepl('%', colnames(gb)))
      gb[,perc.cols] <- gb[,perc.cols]*100
      shiny::validate(need(!is.null(input$metric), 'Loading'))
      
      g <- highchart(type="stock") %>%
        hc_rangeSelector(inputEnabled=FALSE) %>% 
        hc_add_series(xts(gb[,input$metric], gb$Date)
                      , marker = list(enabled = TRUE, radius = 3)
                      , zoneAxis = 'x'
                      , zones = list(list(dashStyle = 'solid'))
                      , name =input$metric
                      , color = "#143965"
        ) 
      g
    }
    else{
      shiny::validate(need(!is.null(input$graph_type), 'Loading'))
      if(input$graph_type == 'Raw Numbers'){
        
        df <- cr_data()
        h <- highchart() %>%
          hc_xAxis(categories= df[['Date']])
        
        for (i in 1:length(CHOICES)){
          h <- h %>% 
            hc_add_series(name = CHOICES[i], data = df[[CHOICES[i]]], type='area', color = CHOICES_COLS[i])
        }
        h %>%
          hc_tooltip(shared=TRUE, useHTML=TRUE,
                     headerFormat='<small>{point.key}</small><table>',
                     pointFormat=paste0('<tr><td> <span style="color:{point.color}">\u25CF</span> {series.name}: </td>',
                                        '<td style="text-align: right"><b>{point.y}</b></td></tr>'),
                     footerFormat= '</table>')
        
        
        
      }else{
        shiny::validate(need(!is.null(input$allmets_baseline), 'Loading'))
        df <- cr_data()
        baseline <- match(input$allmets_baseline, CHOICES)
        h <- highchart() %>%
          hc_xAxis(categories= df$Date)
        
        for (i in baseline:length(CHOICES)){
          h <- h %>% 
            hc_add_series(name = CHOICES[i], data = df[[CHOICES[i]]]/df[[CHOICES[baseline]]]*100, type='area', color = CHOICES_COLS[i])
        }
        h %>%
          hc_yAxis(labels = list(format = "{value}%"), max=100) %>% 
          hc_tooltip(shared=TRUE, useHTML=TRUE,
                     headerFormat='<small>{point.key}</small><table>',
                     pointFormat=paste0('<tr><td> <span style="color:{point.color}">\u25CF</span> {series.name}: </td>',
                                        '<td style="text-align: right"><b>{point.y}</b>%</td></tr>'),
                     footerFormat= '</table>', valueDecimals=2)    
      }
      
      
    }
    

  })
  
  output$cr_table <- renderDataTable({
    cols.with.percs <- which(grepl('%', colnames(cr_data())))
    cr_data() %>% 
    styleTable() %>%
    formatPercentage(cols.with.percs,2)
  })

}
