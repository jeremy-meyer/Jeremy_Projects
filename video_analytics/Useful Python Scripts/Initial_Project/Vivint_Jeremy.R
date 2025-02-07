
dat <- read.csv('OpensAndLocks_edited.csv', stringsAsFactors = FALSE)
#Note: In the excel file, I added a column called date2 that is the numerical value for the excel's date and normalized it. 
#They are stored as the decimal equilavent in days for all the dates. Useful for calculations. 

colnames(dat)[1:4] <- c('ID', 'Event', 'EvtVal','date')
unique(dat$ID)
unique(dat$DeviceName)
table(dat[dat$ID == 34,'DeviceName']) #135 = Back Door, 275 Man Door, 31 = interior garauge, 33 Kitchen, 34 Garauge
#32/102 = Front: Lock + Sensor on front door

#Problem 1
unique(dat[,c('ID', 'DeviceType', 'DeviceName')]) 
#Not Front Door b/c dup name. Kitchen door = back door, 
#man door = Exterior garauge? Probs interior garage door

#A Door will have a sensor and lock installed if the lock takes place frequently soon after the door closes
#OR unlock takes place frequently just before door opens. 


#Door is being unlocked if Locked -> FALSE

ulock135 <- dat[(dat$EvtVal == FALSE & dat$Event == "locked") & dat$ID == 135,] #Unlocks for ID 135
ulock275 <- dat[(dat$EvtVal == FALSE & dat$Event == "locked") & dat$ID == 275,] #Unlocks for ID 275
ulock102 <- dat[(dat$EvtVal == FALSE & dat$Event == "locked") & dat$ID == 102,]


sens33 <- dat[(dat$EvtVal == TRUE & dat$Event == "open") & dat$ID == 33,] #Sensors for ID 33
sens31 <- dat[(dat$EvtVal == TRUE & dat$Event == "open") & dat$ID == 31,]
sens34 <- dat[(dat$EvtVal == TRUE & dat$Event == "open") & dat$ID == 34,]
sens32 <- dat[(dat$EvtVal == TRUE & dat$Event == "open") & dat$ID == 32,]

#Find the time (seconds) after door is unlocked-> Opening
find.nearestOP <- function(ul, sens){ 
  timediff <- sens[,"Date2"] - ul
  timediff <- timediff[timediff > 0]
  timediff[which.min(timediff)]*24*60^2
}

#Checking Front Doors
t32_102 <- sapply(ulock102[,5],function(x) find.nearestOP(x, sens32))
mean(t32_102 < 60) #80% less than a minute
hist(t32_102, br=50)  #Looks Coorelated, so front door (sensor)= front door (lock)!

# 33 and 135
#Check every Unlock of 135, see if openings of 33 occur soon after
t33_135 <- sapply(ulock135[,5],function(x) find.nearestOP(x, sens33))
mean(t33_135 < 60) #87% less than a minute
hist(t33_135, br=50)  #Looks Coorelated Kitchen door = Back door

#33 + 275
t33_275 <- sapply(ulock275[,5],function(x) find.nearestOP(x, sens33))
mean(t33_275 < 60) #None less than a minute. No match
hist(t33_275, br=50) 

#31 + 275
t31_275 <- sapply(ulock275[,5],function(x) find.nearestOP(x, sens31))
mean(t31_275 < 60) #None less than a minute. 
hist(t31_275, br=50)

#34 + 275
t34_275 <- sapply(ulock275[,5],function(x) find.nearestOP(x, sens34))
mean(t34_275 < 60) #Both within seconds, so Exterior Garauge is prob Man Door
hist(t34_275, br=50)

#Door that doesn't have a match is the interior garauge door (ID 31). This is the one with a sensor and without a lock.


# Problem 2 ---------------------------------------------------------------
#A product manager believes there is a correlation between the opening of the exterior garage door and 
#the kitchen door on Saturdays. Do you agree? Justify your response.


#First find dates that are on saturday
raw <- unlist(strsplit(dat[,'date'], ' '))[c(TRUE, FALSE)]
dates <- as.Date(raw, '%m/%d/%Y')
sat <- dat[weekdays(dates) == "Saturday",]

#Find openings of Ext. Garauge door (34)and Kitchen (33)
opExt <- sat[sat$ID == 34 & sat$EvtVal,] #Door opens of ext. garauge
opKit <- sat[sat$ID == 33 & sat$EvtVal,] #Door opens of Kitchen door

opExt[,5]
opKit[,5]

#Note that all saturday openings of the exterior Garauge door only occured on 6/17. The kitchen door
#opened on many other saturdays, which is evidence against correlation. Even on 6/17, the opening times
#were at least 20 minutes apart and much more frequent for the exterior garauge. 



# Problem 3 ---------------------------------------------------------------

#I would use powerpoint slides or a written report and do the following:
#1. Introduce the claim that the product manager has about coorelation on saturdays
#2. Remain neutral. Start by referencing the data that we have through visuals or tables.  
#2a. In this case, show the opening times of the kitchen/Exterior Garauge doors of saturdays only.
#    Since there are few data points, a table with all the times/dates will work. 
#3 Explain that since the only openings of the exterior garauge were on 6/17 and the kitchen door opened several times
#  on other days, we have evidence against correlation. 
#4 Also explain that even on 6/17, there was no pattern to the respective door openings
#5 Conclude that there isn't evidence in the data for the claim and there may even be evidence against it. 

# Problem 4 ---------------------------------------------------------------

#Before anything, making sure you understand the data is crucial before you can find patterns. Finding patterns
#is much more difficult without field knowledge or initial research questions in mind. Visuals are a good start to quickly 
#finding patterns to the data. Plotting different variables against each other while considering their different levels helps 
#find some links. As you get deeper into the analysis, making predictive models using things like regression or neural networks
#can also help find patterns between variabules. 


