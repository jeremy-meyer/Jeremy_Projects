# sapply(2009:2017, function(x) which((babynames %>% filter(year==x, sex=='M') %>% arrange(desc(n)) %>% select(name)) == 'Aaban')) # Checking ranks

server <- function(input, output) {
  callModule(mod_name_analysis_server, 'id-nameAnalysis1')
  

}