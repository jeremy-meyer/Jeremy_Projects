
mod_name_analysis_server <- function(input, output, session){
  ns <- session$ns
  
  sel.sex <- reactive({
    if(input$sex == 'Both') return(c('F', 'M'))
    return(substr(input$sex, 1,1))
  })
  
  dat.beforeRank <- reactive({
    babynames %>% 
      filter(year >= input$year_range[1], year <= input$year_range[2], sex %in% sel.sex())
    
  })
  
  graph.dat <- reactive({
    dat.beforeRank() %>% 
      filter(name == cap.1let(input$name))
    
  })
  
  pop_totals_MF <- reactive({
    babynames %>%
      group_by(year, sex) %>%
      summarise(data.prop=sum(prop), data.tot = sum(n)) %>% 
      ungroup() %>% 
      merge(applicants, by=c('year', 'sex'), all=TRUE) %>% 
      rename('ss.tot'='n_all')
  })
  
  pop_totals_both <- reactive({
    merge(pop_totals_MF() %>% group_by(year) %>% summarise(ss.nBabies = sum(ss.tot)),
          births, by='year', all=TRUE)
  })
  
  # If both sexes, pool
  stat.dat <- reactive({
    validate(need(nrow(graph.dat()) != 0, message='No Names Found'))
    if (input$sex == 'Both'){
      # pooled totals
      return(
        merge(graph.dat() %>% group_by(year) %>% summarise(n=sum(n)), 
              pop_totals_both(),
              by=c('year')) %>% 
          transmute(year=year, sex=input$sex, n = n, prop=n/ss.nBabies)
      )
    }
    graph.dat()
  })

  
  output$tot_babies <- renderText({
    format(sum(stat.dat() %>% select(n)), big.mark=',')
  })
  
  output$peak_yr <- renderText({
    stat.dat() %>% 
      filter(n == max(n)) %>% select(year) %>%  .[[1]]
  })
  
  allRanks <- reactive({
    dat.beforeRank() %>% 
      group_by(name, year) %>% 
      summarise(n = sum(n)) %>% 
      group_by(year) %>% 
      mutate(ranks = rank(-n, ties.method='first')) %>% 
      ungroup()
  })
  
  bothRanks <- reactive({
    dat.beforeRank() %>% 
      group_by(name, year, sex) %>% 
      summarise(n = sum(n)) %>% 
      group_by(year) %>% 
      mutate(ranks = rank(-n, ties.method='first')) %>% 
      ungroup() %>%
      filter(name == cap.1let(input$name))
  })
  # babynames %>% filter(year==1887) %>% group_by(name) %>% summarise(r=sum(n)) %>% arrange(desc(r))
  
  nameRanks <- reactive({
    allRanks() %>% 
      filter(name == cap.1let(input$name))
  })
  
  output$peak_rank <- renderText({
    validate(need(nrow(nameRanks()) != 0, message='No Names Found'))
    nameRanks() %>%
      summarise(min(ranks)) %>% .[[1]]
  })
  
  output$peak_rank_yr <- renderText({
    validate(need(nrow(nameRanks()) != 0, message='No Names Found'))
    nameRanks() %>% 
      filter(ranks == min(ranks)) %>% 
      select(year) %>% 
      arrange(desc(year)) %>% 
      head(1) %>% .[[1]]
  })
  
  output$peak_prop <- renderText({
    format.perc(stat.dat() %>% 
                  filter(prop == max(prop)) %>% 
                  select(prop) %>% 
                  .[[1]])
  })
  
  output$peak_prop_yr <- renderText({
    stat.dat() %>% 
      filter(prop == max(prop)) %>% 
      select(year) %>% .[[1]]
  })
  
  output$first_yr <- renderText({
    stat.dat() %>% 
      select(year) %>% 
      arrange(year) %>% 
      head(1) %>% .[[1]]
  })
  
  output$yrs_top10 <- renderText({
    validate(need(nrow(nameRanks()) != 0, message='No Names Found'))
    sum((nameRanks() %>% select(ranks)) <= 10)
  })
  
  observeEvent(input$browser,{
    browser()
  })
  
  hc_tt_cred <- function(hc, percent=FALSE, ndecimal=3){
    hc_tooltip(hc, shared=TRUE, useHTML=TRUE,
               headerFormat='<small>{point.x}: {point.key}</small><table>',
               pointFormat=paste0('<tr><td style="color: {series.color}"><span style="color:{point.color}">\u25CF</span>{series.name}: </td>',
                                  '<td style="text-align: right"><b>{point.y}</b>', ifelse(percent, ' %', ''), '</td></tr>'),
               footerFormat= '</table>',
               valueDecimals=ifelse(percent, ndecimal, 0)) %>% 
      hc_credits(enabled = TRUE, # add credits
                 text = "SOURCE: US Social Security Administration",
                 href = "https://github.com/hadley/babynames") %>% 
      hc_yAxis(title=list(text=ifelse(percent, 'Percentage', 'Frequency')))
  }
  
  output$freq_graph <- renderHighchart({
    title <- paste('Name Graph for', input$name)
    y.tt.lab <- substr(input$gph_typ,1,4)
    if(input$gph_typ == 'Frequency'){
      h <- hchart(graph.dat(), type='line', hcaes(x=year, y=n, group=sex)) %>%
        hc_title(text = title, align = "center") %>%
        hc_tt_cred(percent=FALSE)
      
    }
    else if(input$gph_typ == 'Proportion'){
      h <- hchart(graph.dat(), type='line', hcaes(x=year, y=prop, group=sex), title=title) %>% 
        hc_title(text = title, align = "center") %>% 
        hc_tt_cred(percent=TRUE) 
    }
    else if (input$gph_typ=='Rank'){
      h <- hchart(raw_data(), type='line', hcaes(x=year, y=ranks, group=sex), title=title) %>% 
        hc_title(text = title, align = "center") %>% 
        hc_tt_cred(percent=FALSE) %>% 
        hc_yAxis(reversed=TRUE, title=list(text=y.tt.lab))
    }
    h %>% 
      hc_xAxis(plotLines = list(list(
        value = 1935.62,
        color = '#000000',
        width = 1,
        zIndex = 4,
        label = list(text = "SSA Created",
                     style = list( color = '#000000')
        ))))
    
  })
  
  output$pooled_switch <- renderUI({
    if(input$sex == 'Both'){
      materialSwitch(
        inputId = ns("pooled"),
        label = tags$b("Show Pooled Totals"), 
        status = "info",
        value=TRUE
      )
    }

  })
  
  # Add SS pool, Total Population. ALso check for pooling both genders
  raw_data <- reactive({
    df <- merge(graph.dat(), nameRanks() %>% select(year, name, ranks), by=c('year', 'name')) %>% 
      rename(babies='n', percent='prop') %>% 
      arrange(desc(year)) 
      
    if(input$sex == 'Both'){
      df <- df %>% 
        select(-matches('ranks')) %>% 
        merge(bothRanks(), by=c('year', 'sex', 'name'))
    }
    return(df)
  })
  
  output$raw_data_tab <- renderDataTable({
    raw_data() %>% styleTable() %>% 
      formatPercentage('percent',2)
  })
  
  output$raw_data_tab_pooled <- renderDataTable({
    stat.dat() %>% 
      merge(nameRanks() %>% select(year, ranks), by='year') %>% 
      merge(pop_totals_both(), by='year') %>% 
      mutate(perc_SS = ss.nBabies/births) %>% 
      arrange(desc(year)) %>% 
      styleTable() %>% 
      formatPercentage(c('prop', 'perc_SS'),2)
  })
  
  output$data_table <- renderUI({
    
    if(input$sex == 'Both'){
      shiny::validate(need(!is.null(input$pooled), 'Loading'))
      if(input$pooled) return(dataTableOutput(ns('raw_data_tab_pooled')))
    }
    dataTableOutput(ns('raw_data_tab'))
  })
  
  observeEvent(input$browser,{
    browser()
  })
}