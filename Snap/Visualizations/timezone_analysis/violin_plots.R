library(ggplot2)
library(snapify)

tz <- read.csv('call_volume_by_timezone.csv')
dc.inds <- which(tz$time_zone == "")
tz[dc.inds,1] <- 'US/Eastern' # Impute DC values
tz1 <- tz[-dc.inds,]
tz2 <- tz[dc.inds,]

# Reaggregate values
agg2 <- merge(tz1, tz2, by=union('time_zone', 'call_hr'), all=TRUE, suffixes = c(".US50", ".DC"))
agg2$call_vol2 <- apply(agg2[,-c(1,2)], 1, sum, na.rm=TRUE)

# Fix timezones to numbers
dec <- FALSE # As we go up on graph, does the timezone decrease?
tz_ord <- levels(agg2$time_zone)[c(5,1,7,6,3,4,2)+1]
agg2$tz_num <- match(agg2$time_zone, tz_ord)-11
agg2$tz_diff <- agg2$tz_num+7
agg2 <- agg2[order(agg2$tz_num, decreasing=dec),]
agg2$hr_adj <- (agg2$call_hr + agg2$tz_diff) %% 24 # Adjusts clock from MST. LOCAL TIME
dat <- agg2[agg2$call_vol2 > 100,c(1:2,5:8)] # Filters Volumes that are less than 100

# Frequency counts
row.names(dat) <- NULL
l <- lapply(1:nrow(dat), function(x) cbind(rep(1,dat$call_vol2[x]), dat[x,-3])) # Ignore warnings
tot.dat <- Reduce(rbind, l)

tz.labs <- sub('US/', '', as.character(unique(dat$time_zone)))
xx <- seq(5,24, by=2)
time.labs <- ifelse(xx<12, paste0(xx,'AM'), paste0(xx %%12, 'PM'))

#png('timezone_violin.png', width=7, height=5, units='in', res=96)
#Note: Axes are flipped
p <- ggplot(tot.dat, aes(x=as.factor(tz_num), y=hr_adj, fill=as.factor(tz_num))) + scale_fill_viridis_d() +
  geom_violin(trim=FALSE, draw_quantiles = .5, scale='count', adjust=3.25, linetype = 0) + coord_flip()

#Plot
p + ggtitle('Call Volume in Each US Timezone') + xlab('US Timezone') + ylab('Local Time') + 
  scale_x_discrete(labels= tz.labs) + 
  scale_y_continuous(breaks=xx, labels=time.labs) + 
  theme_bw() + theme(legend.position = "none") + theme(panel.grid.major.x=element_line(color='gray85')) + 
  theme(axis.text.y = element_text(size=11, angle=0, colour = 'Black'))
  # stat_summary(fun.y = "mean", geom = "point", shape = 2, size = 4, color = "black")
#dev.off()
