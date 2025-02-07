# library(shiny)
ui <- fluidPage(
  headerPanel("Central Limit theorem"),  
  radioButtons("dist", "Select a distribution:",
                list(`Gamma(shape, scale=1)` = 'GM',
                     `Uniform(min, max=min+1)` ='UN',
                     `Multi-Modal(numModes, scale=1)` = 'MM')
    ),
  
    uiOutput("ui_params"),
    # numericInput("p1", 'Distribution Parameter', 1), 
    tabsetPanel(
      id = "navbar",
      tabPanel(title = "CLT Slider",
               value = "tab1",
               sliderInput(inputId = "N", label = "Sample Size",
                           value = 4, min = 1, max = 50),
               plotOutput("val1")
      ),
      tabPanel(title = "CLT Size Graph",
               value = "tab2", h1(''),
               textInput("sampSizes", 'Enter desired sample sizes (separated by commas):', '2,5,8,10,15,20,30,50'),
               actionButton('click', label='Generate Graph'),
               plotOutput("plot2")
      )
  )
)


server <- function(input, output) {
  plot.xbars <- function(samp.means){
    hist(samp.means, freq=FALSE, breaks=100, main='Histogram of Sample Means')
    lines(density(samp.means), col='blue')
    curve(dnorm(x, mean(samp.means), sd(samp.means)), add=TRUE, lty=2, main='Sample Means', xlab='Sample Mean')
  }
  
  rMM <- function(n, f, xrang){
    g <- function(x) dunif(x, xrang[1], xrang[2])
    C <- 2
    samps <- rep(NA, n)
    i <- 1
    while (i <= n){
      Y <- runif(1, xrang[1], xrang[2])
      if (runif(1) < f(Y)/(C*g(Y))){
        samps[i] <- Y
        i <- i + 1
      }
    }
    samps
  }
  
  output$ui_params <- renderUI({
    switch(input$dist,
        "GM" = numericInput("p1", "Gamma Shape Parameter", value = 1, min = 1e-5),
        "UN" = numericInput("p1", "Uniform Minimum Parameter", value = 0),
        'MM' = numericInput("p1", "Number of Modes", value=2)
    )
    
  })
  
  
  output$val1 <- renderPlot({
    layout(mat=matrix(c(1,2), nrow=1))
    if(input$dist == "GM"){
      scale <- 1
      p1 <- ifelse(is.null(input$p1),1,input$p1) # Not sure why this is needed
      xrang <- qgamma(c(.001, .999),p1, scale)
      curve(dgamma(x, p1, scale), col='red', lwd=2, xlim=xrang,
            main='Population Distribution', ylab='Density',n=1000)
      samp.means <- replicate(1e4, mean(rgamma(input$N, p1, scale)))
    }

    if(input$dist == "UN"){
      b <- input$p1 + 1
      xrang <- qunif(c(.001, .999), input$p1, b)
      curve(dunif(x, input$p1, b), col='red', lwd=2, xlim=xrang,
            main='Population Distribution', ylab='Density',n=1000)
      samp.means <- replicate(1e4, mean(runif(input$N, input$p1, b)))
    }

    if(input$dist == 'MM'){
      sc <- 1
      norm.const <- 1/(sc*(2*pi-sin(2*pi*input$p1)/input$p1))
      xrang <- c(0, 2*pi*sc)
      f <- function(x) norm.const*(-cos(input$p1*x/sc)+1)
      curve(f, xlim=xrang, col='red', lwd=2,
            main='Population Distribution', ylab='Density',n=100)
      samp.means <- replicate(5e3, mean(rMM(input$N,f, xrang)))
    }
    plot.xbars(samp.means)
  })

    observeEvent(input$click, {
      ns <- rapply(strsplit(gsub(' ', "", input$sampSizes),','), as.numeric)
      Nsim2 <- 5e3
      
      
      output$plot2 <- renderPlot({
        layout(mat=matrix(1, nrow=1))
      
        if(input$dist == "GM"){
          scale <- 1
          xrang <- qgamma(c(.1, .9), input$p1, scale)
          dens <- lapply(ns, function(x) density(replicate(Nsim2, mean(rgamma(x, input$p1, scale)))))
        
        } else if(input$dist == 'UN'){
          b <- input$p1 + 1
          xrang <- qunif(c(.1, .9), input$p1, b)
          dens <- lapply(ns, function(x) density(replicate(Nsim2, mean(runif(x, input$p1, b)))))
        } else if(input$dist == 'MM'){
          scale <- 1
          xrang <- c(0, 2*pi*scale)
          norm.const <- 1/(scale*(2*pi-sin(2*pi*input$p1)/input$p1))
          f <- function(x) norm.const*(-cos(input$p1*x/scale)+1)
          dens <- lapply(ns, function(x) density(replicate(Nsim2, mean(rMM(x, f, xrang)))))
        }
        
        plot(dens[[length(ns)]], col=length(ns), xlim=xrang, lwd=2, main='Sample Mean Distribution', xlab='X')
        legend('topright', title='N', legend=ns, col=1:length(ns), lwd=2, lty=1, cex=.8)
        
        for(i in 1:(length(ns)-1)){
          lines(dens[[i]], col=i, lwd=2)
        }
        
        })
    })


}

shinyApp(ui = ui, server = server)