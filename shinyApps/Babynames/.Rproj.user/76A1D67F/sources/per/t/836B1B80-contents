library(shiny)
library(shinydashboard)
library(shinyWidgets)
library(highcharter)
library(dplyr)
library(DT)
library(babynames)



# Global Functions
cap.1let <- function(name){
  # Verify all names have 1 capital letter
  # isUpper <- function(n) length(unlist(gregexpr("[A-Z]", n))) != 1
  # nCaps <- sapply(unlist(c(names)), isUpper)
  # sum(nCaps)
  paste0(toupper(substr(name,1,1)), tolower(substr(name, 2, nchar(name))))
}

format.perc <- function(num, ndig=2, isPerc=FALSE){
  paste0(format(round(num*ifelse(isPerc, 1, 100),2), nsmall = 2), '%')
}

styleTable <- function(df, dom = 'Bfrtip',selection = 'multiple', extensions= c("Buttons"),pageLength = 12, escape=TRUE, ...){
  datatable(
    df
    , rownames = FALSE
    , selection = selection
    , escape = escape
    , filter = "top"
    , extensions = extensions
    , options = list(
      buttons = c('pageLength', 'colvis', 'excel', 'pdf')
      , dom = dom
      , scrollX = TRUE
      , lengthMenu = list(c(10,25,50,100,-1), c('10','25','50','100','All'))
      , pageLength = pageLength
      , searchHighlight = TRUE
      ,...
    )
  )
  
  
}
# source all modules
invisible(sapply(paste0('Modules/', list.files('Modules')), source))



# Add visual to display the amount of data known
# Cumulative graphs at what % of cohort lives to age 10,20,ect
# Death analysis Hazard function graphs, death probability (% of people that die that year), % of people left alive, 
# switch to show overall line