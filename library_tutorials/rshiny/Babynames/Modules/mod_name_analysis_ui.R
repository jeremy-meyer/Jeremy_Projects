
mod_name_analysis <- function(id){
  ns <- NS(id)
  
  fluidPage(
    fluidRow(box(
      fluidPage(
        fluidRow(column(6,
          textInput(ns('name'), 'Enter Name', 'John', width='67%')),
        column(6,
          awesomeRadio(ns('sex'), 'Which Sex?', c('Female', 'Male', 'Both'), selected = 'Male', inline=TRUE))
        ),
        fluidRow(column(12, sliderInput(ns("year_range"), "Date Range:", min = min(babynames$year), max = max(babynames$year), value = c(1900,2017)))))
      , width=12, background = 'black'))
    ,
    fluidRow(  
      valueBox(
        uiOutput(ns("tot_babies")), "Total Babies"
        , width = 3, color = 'navy', icon = icon('baby')
      ),
      
      valueBox(
        uiOutput(ns("first_yr")), "First Appearance"
        , width = 3, color = 'purple', icon('calendar-plus')
      ),
      
      valueBox(
        uiOutput(ns("peak_rank")), "Peak Rank"
        , width = 3, color = 'olive', icon('sort-numeric-up')
      ),
      
      valueBox(
        uiOutput(ns("peak_prop")), "Peak Proportion"
        , width = 3, color = 'light-blue', icon('percentage')
      ),
      
      valueBox(
        uiOutput(ns("peak_yr")), "Year with the most Births"
        , width = 3, color = 'blue', icon('baby-carriage')
      ),
      
      valueBox(
        uiOutput(ns("yrs_top10")), "Years in top 10"
        , width = 3, color = 'maroon', icon('calendar-times')
      ),
      
      valueBox(
        uiOutput(ns("peak_rank_yr")), "Peak Rank Year (Latest)"
        , width = 3, color = 'green', icon('calendar-alt')
      ),
      
      valueBox(
        uiOutput(ns("peak_prop_yr")), "Peak Proportion Year"
        , width = 3, color = 'teal', icon('calendar-alt')
      )

    ),
  fluidRow(
    box(
      awesomeRadio(ns('gph_typ'), HTML('<font size="4">Graph View</font>'), c('Frequency', 'Proportion', 'Rank'), inline = TRUE),
      highchartOutput(ns('freq_graph'))
    ,width=12),
    
    box( title=HTML('<b>Table View</b>'),
      uiOutput(ns('pooled_switch')),
      uiOutput(ns('data_table'))
    ,width=12)
  )
  ,actionButton(ns("browser"), "Debugger"),
  tags$script("$('#browser').hide();") #$('#browser').show();
  
  )
  
}

