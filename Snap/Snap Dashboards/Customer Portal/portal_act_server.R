
portal_act_server <- function(input, output, session, date_range){
  ns <- session$ns
  NDIGIT <- 2
  COLS <- c('#39cccc', '#00a65a', '#f39c12', '#001f3f', '#605ca8', '#d81b60', '#f012be')
  
  call_account_data <- reactive({
    
    params_list <- list(from_date = date_range()[1], to_date = date_range()[2], time_view = input$time_view,
                        skill_group_name = NULL, 
                        disposition_service = NULL,
                        product_type = input$product
    )
    
    urls <- c('contactRate/accounts/in_time', 
              'contactRate/accounts/aggregate'
              )
    api_call(urls=urls, params_list = params_list)
  })
  
  accounts_in_time <- reactive({
    
    df <- call_account_data()[[fullPath('contactRate/accounts/in_time')]]
    
    shiny::validate(need(length(df)>0, 'No data available.'))
    
    df <- df %>% 
      select('date'
             ,'Registered Accounts' = registered_count
             ,'Logged In Accounts' = login_count
             ,'Accounts Paid Off' = rg_account_paid_off_ct
             ,'Card Added' = rg_card_added_ct
             ,'Cards Changed' = rg_card_change_ct
             ,'Card Payment Created' = rg_pmt_created_ct
             ,'Manual Payment Posted' = rg_pmt_posted_ct
             ,'Payment Method Changed' = rg_pmt_mth_change_ct

      ) %>% 
      mutate(date = as.Date(date))
      df
  })
  
  cn <- reactive(colnames(accounts_in_time()))
  
  time_data <- reactive({
    df <- accounts_in_time()
    if(input$perc){
      df[,-1] <- t(apply(df[,-1], 1, function(x) x/x[1]))
    }
    df
  })
  
  accounts_in_aggregate <- reactive({
    
    df <- call_account_data()[[fullPath('contactRate/accounts/aggregate')]]
    shiny::validate(need(length(df)>0, 'NA'))
    reg_count <- as.numeric(df$registered_count)
    round(df %>% select(-contains('rate')) / ifelse(input$perc, reg_count/100, 1),NDIGIT)
    
  })
  
  format_num <- function(num, perc=input$perc){
    paste0(format(num, big.mark = ',', nsmall=ifelse(perc, NDIGIT, 0)), ifelse(perc, '%', ''))
  }
  
  output$tot_reg <- renderText({
    format_num(accounts_in_aggregate()$registered_count)
  })
  
  output$port_log <- renderText({
    format_num(accounts_in_aggregate()$rg_portal_logins_ct)
  })
  
  output$card_chg <- renderText({
    format_num(accounts_in_aggregate()$rg_card_change_ct)
  })
  
  output$acc_pdo <- renderText({
    format_num(accounts_in_aggregate()$rg_account_paid_off_ct)
  })
  
  output$card_add <- renderText({
    format_num(accounts_in_aggregate()$rg_card_added_ct)
  })
  
  output$man_pmt <- renderText({
    format_num(accounts_in_aggregate()$rg_pmt_posted_ct)
  })
  
  output$pmt_met <- renderText({
    format_num(accounts_in_aggregate()$rg_pmt_mth_change_ct)
  })
  
  output$card_pmt <- renderText({
    format_num(accounts_in_aggregate()$rg_pmt_created_ct)
  })
  
  output$pa_table <- renderDataTable({
    time_data() %>% 
      styleTable() %>% formatPercentage(if(input$perc) 2:10 else 110, 3)
  })
  
  output$graph_opt <- renderUI({
    graph_choices <- sort(cn()[-c(1,2)])    
    pickerInput(
          inputId = ns("gph_line"),
          label = "Select Metric",
          choices = graph_choices, 
          selected = graph_choices[graph_choices != 'Logged In Accounts'],
          options = list(
            `actions-box` = TRUE,
            size = 10,
            `selected-text-format` = "count > 4"
          ),
          multiple = TRUE
        )         
  })
  
  output$pa_graph <- renderHighchart({
    gph_dat <- time_data()
    cols_to_gph <- match(input$gph_line, cn())
    
    h <- highchart(type='stock') %>% 
      hc_rangeSelector(inputEnabled=FALSE)
    
    for (i in cols_to_gph){
      h <- h %>% 
        hc_add_series(xts(gph_dat[[i]]*ifelse(input$perc, 100, 1), gph_dat[['date']]), name=cn()[i], color=COLS[i-2])
    }
    
    if(input$perc){
      h %>% 
        hc_yAxis(labels = list(format = "{value}%"), title=list(text='% of Registered Accounts'), opposite=TRUE) %>% 
        hc_tooltip(valueSuffix=' %', valueDecimals=3)
    }
    else{
      h %>% 
        hc_yAxis(title=list(text='Counts'), opposite=TRUE)
    }
  })
  
  #observeEvent(input$button, browser())
}