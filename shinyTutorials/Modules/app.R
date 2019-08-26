library(shiny)

# load module functions
source("hello_world.R")

ui <- fluidPage(
  
  titlePanel("Using of Shiny modules"),
  
  fluidRow(
    # Call interface function of module "hello_world"
    hello_worldUI(id = "id_1")
  )
  
)

server <- function(input, output, session) {
  
  # Call logic server function of module "hello_world"
  callModule(module = hello_world, id = "id_1")
  
}

shinyApp(ui = ui, server = server)