
library(readxl)
library(ggplot2)
library(reshape2)
library(snapify)
library(cowplot)

# This function will plot the payment schedule from a single sheet as read in from an excel file
# date format: yyyy-mm-dd
make.plot <- function(dat, date.range=dat[c(1,nrow(dat)),1]){
  dat[,1] <- as.Date(dat[,'date']) # Date Conversion
  date.range <- as.Date(date.range) 
  d1 <- melt(dat[,1:4], 'date')
  d2 <- melt(dat[,c(1,5:6)], 'date')
  
  labs.1 <- c('GAAP Schedule', 'Adjusted Schedule', 'Customer Payment') # Legend Labels
  labs.2 <- c('GAAP Past Due', 'Operational Past Due')
  
  g1 <- ggplot(d1, aes(x=date, y=value, colour=variable)) + theme_bw() +
    ylab('Cumulative Value ($)') + xlab("") +
    geom_line(na.rm = TRUE, aes(size=variable), alpha=0.85) + 
    scale_size_manual(values=c(1.75,2.5,1.15), labels=labs.1) + 
    scale_color_manual(values=c(snap_orange, snap_yellow, snap_blue_med), labels=labs.1) +
    scale_x_date(date_breaks='2 months', date_labels="%b '%y", limits=date.range) +
    theme(legend.title = element_blank())
  
  g2 <- ggplot(d2, aes(x=date, y=value, colour=variable)) + 
    geom_line(na.rm=TRUE, size=1.15, alpha=0.85) + theme_bw() +
    scale_x_date(date_breaks='2 months', date_labels="%b '%y", limits=date.range) +
    ylab('Days') + theme(legend.title = element_blank(), legend.text = element_text(size=8)) + 
    scale_color_manual(values=c(snap_green, snap_orange), labels=labs.2)
  
  
  plot_grid(g1,g2, align='v', nrow=2,rel_heights=c(2,1)) # From Cowplot package
}

# Example
data <- lapply(1:5, function(x) as.data.frame(read_excel('To plot 2.xlsx', sheet=x))) # 5 Sheets

make.plot(data[[1]], date.range=c('2018-08-18', '2019-01-01'))
make.plot(data[[3]])
lapply(data, make.plot) # 5 plots incoming! 
