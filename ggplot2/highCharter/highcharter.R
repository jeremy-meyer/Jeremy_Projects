library(highcharter)
library(dplyr)
library(tidyr)

births <- read.csv("https://github.com/mine-cetinkaya-rundel/highcharts-in-r/raw/master/data/births.csv")
diff13 <- births %>%
  filter(date_of_month %in% c(6, 13, 20)) %>%
  mutate(day = ifelse(date_of_month == 13, "thirteen", "not_thirteen")) %>%
  group_by(day_of_week, day) %>%
  summarise(mean_births = mean(births)) %>%
  arrange(day_of_week) %>%
  spread(day, mean_births) %>%
  mutate(diff_ppt = ((thirteen - not_thirteen) / not_thirteen) * 100)

hchart(diff13, "scatter", hcaes(x = day_of_week, y = diff_ppt))

highchart() %>%
  hc_add_series(data = round(diff13$diff_ppt, 4), type = "column",
                name = "Difference, in ppt",
                color = "#F0A1EA", showInLegend = FALSE) %>%
  hc_yAxis(title = list(text = "Difference, in ppt"), allowDecimals = FALSE) %>%
  hc_xAxis(categories = c("Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"),
           tickmarkPlacement = "on",
           opposite = TRUE) %>%
  hc_title(text = "The Friday the 13th effect",
           style = list(fontWeight = "bold")) %>%
  hc_subtitle(text = "Difference in the share of U.S. births on 13th of each month
              from the average of births on the 6th and the 20th,
              1994 - 2004") %>%
  hc_tooltip(valueDecimals = 4,
             pointFormat = "Day: {point.x} <br> Diff: {point.y}") %>%
  hc_credits(enabled = TRUE,
             text = "Sources: CDC/NCHS, SOCIAL SECURITY ADMINISTRATION",
             style = list(fontSize = "10px")) %>%
  hc_add_theme(hc_theme_538())



library(nycflights13)
oct_lax_flights <- flights %>%
  filter(month == 10, dest == "LAX")
hchart(oct_lax_flights, "scatter", hcaes(x = dep_delay, y = arr_delay, group = origin))


oct_lax_flights_agg <- oct_lax_flights %>%
  mutate(dep_delay_cat = cut(dep_delay, breaks = seq(-15, 255, 15))) %>%
  group_by(origin, dep_delay_cat) %>%
  summarise(med_arr_delay = median(arr_delay, na.rm = TRUE))
hchart(oct_lax_flights_agg, "line", hcaes(x = dep_delay_cat, y = med_arr_delay, group = origin))
