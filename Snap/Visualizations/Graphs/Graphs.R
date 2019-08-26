
dat1 <- read.csv('~/Data/data1.csv')[-c(30:33),] # I split the data into 2 files
library(ggplot2)
library(reshape2)
library(snapify)

# Plot 1: Operation GAAP over time
dat1$GAAPPerc <- as.numeric(sub('%', ' ', dat1$Operation.GAAP))
dat1$date <- as.Date(dat1$date, format='%m/%d/%Y')
ggplot(dat1, aes(x = date, y = GAAPPerc)) +
  geom_line(color=snap_green_med, size = 2) +
  scale_x_date(date_breaks = '4 months', date_labels= "%b '%y") +
  scale_y_continuous(breaks=seq(70,100,by=5), labels=seq(70,100,by=5), limits=c(70,100)) +
  ylab('GAAP (%)') + xlab("Date") +
  theme(panel.background =  element_rect(fill = 'grey85'), panel.grid.minor = element_line(color = 'grey91'))


# Plot 2: Scatterplot: GAAP -X vs OPeration-Y (NOT ONLY)
library(egg)
library(grid)
sz <- 5
ols.line <- coef(lm(Operation ~ GAAP, data=dat1))
p2 <- ggplot(dat1, aes(x=GAAP, y=Operation)) + 
  geom_abline(intercept=ols.line[1], slope=ols.line[2], lty=2, col='white') +
  geom_point(size=sz, shape=15, col=snap_blue_light) + geom_point(size=sz, shape=0, col='black')  + 
  theme(panel.background =  element_rect(fill = snap_grey), panel.grid.minor=element_line(color=snap_grey_med)) +
  scale_x_continuous(labels = scales::comma, breaks = seq(2e4,12e4,2e4), limits=c(2e4, 12e4)) + 
  scale_y_continuous(labels = scales::comma, breaks = seq(2e4,12e4,2e4), limits=c(2e4, 12e4))
p_fixed <- egg::set_panel_size(p2, width  = unit(15, "cm"), height = unit(15, "cm")) # Square
grid.newpage()
grid.draw(p_fixed)
 # See if you can make a square graph panel

# Plot 3: Bar Chart: Gap and operation (NOT ONLY)
df3 <- dat1[,c('date','GAAP', 'Operation')]
bars <- melt(df3, id.vars='date')

ggplot(bars, aes(fill=variable, y=value, x=date)) + 
  geom_bar(position="dodge", stat="identity") + scale_fill_manual(values=c(snap_green, snap_blue_med)) +
  scale_x_date(date_breaks = '4 months', date_labels= "%b '%y", expand=c(3e-2, 3e-2)) + 
  scale_y_continuous(limits=c(0, 130e3), expand=c(0,0), breaks = seq(0,150e3, 30e3), labels = scales::comma) +  
  #theme(legend.title = element_blank(), panel.border = element_rect(colour = "black", fill=NA)) +
  theme(legend.title = element_blank())
  theme(axis.ticks.x = element_line(colour = "black", size = 1))
  


# Plot 4: GAAP only CHOFF and both_choff over time
# Do you want this for the whole time period?
dat2 <- read.csv('~/Data/data2.csv')
dat2$date <- as.Date(dat2$Date, format='%m/%d/%Y')
df4 <- cbind.data.frame(dat2[,'date'],apply(dat2[,9:10], 2, function(x) as.numeric(sub('%','',x))))[1:17,]
colnames(df4) <- c('date', sub('.1','',colnames(df4)[-1]))
df4.melt <- melt(df4, id='date')

# (Technically) Past due vs really (operational) past due
# Think orange vs red line
ggplot(df4.melt) +
  geom_line(aes(x=date, y=value, colour=variable), size=2) +
  scale_color_manual(values=c(snap_purple_med, snap_blue_light)) +
  scale_x_date(date_breaks = '2 months', date_labels= "%b '%y") + 
  scale_y_continuous(limits=c(0, 100), expand=c(0,0), breaks=seq(0,100,20)) +
  theme(legend.title = element_blank()) + ylab('Percent (%)') +
  theme(panel.grid.minor = element_line(color='gray96'))
  
  
  
  


