library(highcharter)
mapdata <- get_data_from_map(download_map_data("countries/us/us-all"))
# glimpse(mapdata)


data_fake <- mapdata %>% 
  select(code = `hc-a2`) %>% 
  mutate(value = 1e5 * abs(rt(nrow(.), df = 10)))

# glimpse(data_fake)

hcmap("countries/us/us-all", data = data_fake, value = "value",
      # joinBy = c("hc-a2", "code"), name = "Dataset",
      # dataLabels = list(enabled = TRUE, format = '{point.name}'),
      # borderColor = "#FAFAFA", borderWidth = 0.1,
      tooltip = list(valueDecimals = 2, valuePrefix = "$", valueSuffix = " USD")) 


setwd("C:/Users/jmeyer/Work_Code/highCharter")
state.pop <- read.csv('states.csv', header=TRUE)[,-c(2:3)]
state.pop[,-1] <- apply(state.pop[,-1], 2, function(x) as.numeric(gsub(',','', x)))

YEAR <- paste0('X', 2018)
data <- state.pop[,c('X', YEAR)]
hcmap("countries/us/us-all", data = data, value = YEAR,
      joinBy = c("woe-name", "X"), name = "State Population", fillColor = '#FF0000')
      # dataLabels = list(enabled = TRUE, format = '{point.name}'),
      # borderColor = "#FAFAFA", borderWidth = 0.1,) 
