library(shiny)
ui <- fluidPage('Hello World!')

server <- function(input, output) {}

shinyApp(ui = ui, server = server)


# library(rsconnect)
# rsconnect::deployApp('path/to/app')