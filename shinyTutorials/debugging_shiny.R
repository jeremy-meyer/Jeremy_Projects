
# Add to your UI: 
actionButton("browser", "Debugger"),
tags$script("$('#browser').hide();")

# Add to your server 
observeEvent(input$browser,{
  browser()
})

# And to show the button in your app, go 
# to your web browser, open the JS console, (CTR+SHIFT+C)
# And type:
$('#browser').show();