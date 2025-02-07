library(shiny)
library(shinydashboard)
library(shinyWidgets)
library(highcharter)
library(dplyr)

babynames <- read.csv('babynames.csv')
babynames <- babynames %>% mutate(prop = prop*100)
# plot.ts(babynames %>% filter(sex == 'M') %>% group_by(year,sex) %>% summarize('s'=sum(prop)) %>% select(s) %>% .[,2])
cap.1let <- function(name){
  paste0(toupper(substr(name,1,1)), tolower(substr(name, 2, nchar(name))))
}

# Dashboard Page Has three parts, a header, sidebar and body
ui <- dashboardPage(skin='black',
                    dashboardHeader(title='Babynames Dataset'),
                    dashboardSidebar(
                      sidebarMenu(
                        menuItem("Name Analysis", tabName = "tab1", icon = icon("dashboard")),
                        menuItem("Both Male/Female name analysis", tabName = "tab2", icon = icon("dashboard")),
                        menuItem("Name Comparison / Regular expression search", tabName = "tab3", icon = icon("dashboard")),
                        menuItem("Year Rank charts / Rank Analysis", tabName = "tab4", icon = icon("dashboard"))
                      )
                    ),
                    dashboardBody(
                      tabItems(
                        # First tab content
                        tabItem(tabName = "tab1",
                                fluidRow(box(
                                textInput('name', 'Enter Name', 'John'),
                                radioButtons('sex', 'Which Sex?', c('Female', 'Male', 'Both'), selected = 'Male'),
                                radioButtons('gph_typ', 'Graph Type', c('Frequency', 'Proportion'), selected = 'Proportion'),
                                sliderInput("year_range", "Date Range:", min = min(babynames$year), max = max(babynames$year), value = c(1880,2017)),
                                background='red'), 
                                
                                valueBox(
                                  uiOutput("tot_babies"), "Total Babies"
                                  , width = 3, color = 'aqua', icon = icon('baby')
                                ),
                                
                                valueBox(
                                  uiOutput("peak_yr"), "Year with the most Births"
                                  , width = 3, color = 'red', icon('baby-carriage')
                                ),
                                
                                valueBox(
                                  uiOutput("peak_rank"), "Peak Rank"
                                  , width = 3, color = 'orange', icon('sort-numeric-up')
                                ),
                                
                                valueBox(
                                  uiOutput("peak_rank_yr"), "Peak Rank Year (Latest)"
                                  , width = 3, color = 'orange', icon('calendar-alt')
                                ),
                                
                                valueBox(
                                  uiOutput("peak_prop"), "Peak Proportion"
                                  , width = 3, color = 'green', icon('percentage')
                                ),
                                
                                valueBox(
                                  uiOutput("peak_prop_yr"), "Peak Proportion Year"
                                  , width = 3, color = 'red'
                                ),
                                
                                valueBox(
                                  uiOutput("first_yr"), "First Appearance"
                                  , width = 3, color = 'purple'
                                ),
                                
                                valueBox(
                                  uiOutput("yrs_top10"), "Years in top 10"
                                  , width = 3, color = 'purple'
                                )
                                ),
                                fluidRow(highchartOutput('freq_graph'), width=9)
                                ),
                        tabItem(tabName = 'tab2', box(title = "Box Title", width = NULL, background = "green", "Tab 1 Text"))
                      )
                    )
)

server <- function(input, output) {
  # input$sex
  sel.sex <- reactive({
    if(input$sex == 'Both') return(c('F', 'M'))
    return(substr(input$sex, 1,1))
  })
  
  graph.dat <- reactive({
    validate(need(input$sex, message='Please select a sex'))
    babynames %>% 
      filter(name == cap.1let(input$name), year >= input$year_range[1], year <= input$year_range[2], sex %in% sel.sex())
    
  })
  
  # If both sexes, pool
  stat.dat <- reactive({
    
    
  })
  # Figure out what to do with both sexes
  output$tot_babies <- renderText({
    format(sum(graph.dat() %>% select(n)), big.mark=',')
  })
  
  output$peak_yr <- renderText({
    graph.dat() %>% 
      filter(n == max(n)) %>% select(year) %>%  .[[1]]
  })
  
  topRanks <- reactive({
    # rankList <-graph.dat() %>% 
    #   group_by(sex) %>% 
    #   mutate(ranks = rank(n, ties.method='first'), min.rank = min(ranks))
    # print(rankList$ranks)
    
    graph.dat() %>% 
      mutate(ranks = rank(n, ties.method='first'), min.rank = min(ranks)) %>% 
      filter(ranks == min.rank) %>% 
      arrange(desc(year))
  })

    output$peak_rank <- renderText({
    topRanks() %>%
      select(min.rank) %>% .[[1]]

  })

  output$peak_rank_yr <- renderText({
    topRanks() %>%
      select(year) %>% .[[1]]
  })
  
  output$freq_graph <- renderHighchart({
    title <- paste('Name Graph for', input$name)
    y.tt.lab <- substr(input$gph_typ,1,4)
    if(input$gph_typ == 'Frequency'){
      h <- hchart(graph.dat(), type='line', hcaes(x=year, y=n, group=sex)) %>%
        hc_title(text = title, align = "center") %>%
        hc_tooltip(shared=TRUE, useHTML=TRUE,
                   headerFormat='<small>{point.x}: {point.key}</small><table>',
                   pointFormat=paste0('<tr><td style="color: {series.color}"><span style="color:{point.color}">\u25CF</span>{series.name}: </td>',
                                      '<td style="text-align: right"><b>{point.y}</b></td></tr>'),
                   footerFormat= '</table>',
                   valueDecimals=0) %>% 
        hc_yAxis(title=list(text='Frequency'))
        
    }else{
      h <- hchart(graph.dat(), type='line', hcaes(x=year, y=prop, group=sex), title=title)
      h %>% hc_title(text = title, align = "center") %>% 
        hc_tooltip(shared=TRUE, useHTML=TRUE,
                   headerFormat='<small>{point.x}: {point.key}</small><table>',
                   pointFormat=paste0('<tr><td style="color: {series.color}"><span style="color:{point.color}">\u25CF</span>{series.name}: </td>',
                                      '<td style="text-align: right"><b>{point.y}</b> %</td></tr>'),
                   footerFormat= '</table>',
                   valueDecimals=3) %>%
      hc_credits(enabled = TRUE, # add credits
                   text = "SOURCE: US Social Security Administration",
                   href = "https://github.com/hadley/babynames") %>% 
      hc_yAxis(title=list(text='Percentage'))
      
        
    }
    
  })
  
}

shinyApp(ui, server)