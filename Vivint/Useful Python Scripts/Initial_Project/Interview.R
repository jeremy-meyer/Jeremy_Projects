
#Problem: Is there sufficient eye surgery volumes around Farmington/S. Jordan that will benefit U of U health?
#Consider: Most optimologists only specialize in 1-2 functions
#Commercial sponsored insurances will cover more and usually are simpler cases
#It is important to have access to U of U health
#We only care about Wastach Front ie Weber, Davis, Salt Lake, Utah, Tooele, Summit co.

#Data that would've been helpful: Zip code of facility. 

library(readxl)
data <- lapply(1:length(excel_sheets('data.xlsx')), function(x) as.data.frame(read_xlsx('data.xlsx', x)))

surg <- data[[1]] #History of all eye surgeries
zip <- data[[2]] #Wasatch Zip code index
insAcc <- data[[3]] #Percentage of people who's insurance has access to U of U health
pop <- data[[4]] #Population of Utah split by M/F and 2016/2021
dist <- data[[5]] #Distance between (Wastach) Residential Zip code centroid and facility


# Research Question 1 -----------------------------------------------------
#About how far do people in the Wasatch Front generally travel for eye surgery? Based on the
#trend(s), how broadly should we define Farmington's market and South Jordan's market?

wZips <- c(as.matrix(zip[,1]))
surg <- surg[as.matrix(surg[,5]) %in% wZips,] #Only surgeries in Wasatch front
pop <- pop[pop$zipcode %in% wZips,]
insAcc <- insAcc[insAcc$zipcode %in% wZips,]


#Converts zip code + id to distance
zip.mi <- function(zip,id){
  indx <- which(dist[,1] == as.character(zip) & dist[,2] == id)
  return(ifelse(length(indx) > 0, dist[indx, 3], NA))
}

#Returns community/munic. from zip code
zip.mun.comm <- function(z){
  zip[zip$zipcode == as.character(z), 2:3]
}

#Adds community/city/distance
surg <- cbind(surg, 'Dist' = sapply(1:nrow(surg), function(x) zip.mi(surg[x,5], surg[x,1])), 
              t(sapply(1:nrow(surg), function(x) zip.mun.comm(surg[x,5]))))
surg$community <- unlist(surg$community)
surg$municipality <- unlist(surg$municipality)

hist(surg[,8], main='Distance Traveled to Eye Surgery', xlab = 'Distance (mi)')
mean(surg[,8], na.rm = TRUE) 
median(surg[,8], na.rm = TRUE) #Median is a better "typical" measurement because it's right skewed.
summary(surg[!is.na(surg[,8]),8])

#Typical Distance: About 7.68 Miles
#Limitations: Assumes everyone lives in/near centroid. Problems arise If centroid is poor representation of zip code population
#Many values (969) are missing. Missing data
sum(is.na(surg[,8]))
929/nrow(surg) #3.8% missing

#Since the median travel distance is 7.68 miles, we could define both markets by a radius of about 7 miles. 
#From Google maps, Layton, Kaysville, and centerville are all within 7 miles of Farmington
#Community: Mid Davis Co.

#South Jordan is within 8 miles of Herriman, W jordan, herriman, Draper, sandy, bluffdale, herriman.
#However, we will use communities that are already defined to allow for fair comparisons and so we don't
#Have to redefine the markets. We'll use what we already have. 
#Communities: South jordan


# Research Question 2 -----------------------------------------------------
#How many eye surgeries annually do people who reside in Farmington's market and South
#Jordan's market currently undergo? How does that compare to other communities/markets?

#Assuming SJ Market: South jordan comminity
#Farmington Market: Mid Davis co. Community

surgSJ <- surg[surg$community %in% c("South Jordan"),]
surgFarm <- surg[surg$community %in% "Mid Davis Co",]
Neighbors <- c('Taylor/W Jordan', 'SE Salt Lake Co', 'SW Salt Lake Co')
neighZips <- unlist(lapply(Neighbors, function(x) comm.zip(x)))

nrow(surgSJ) #765 annually
nrow(surgFarm) #1619 annually

par(mfrow=c(1,2))
hist(surgSJ[,8], br=25, main='S. Jordan travel distance', xlab='miles')
hist(surgFarm[,8], br=20, main='Farmington travel distance', xlab='miles')
#Looking at histograms of the amount of distances those residents already travel, S. Jordan's market may include more people
#Because a large number of people are having to travel 20+ miles. 
#Also S. Jordan has many more neighbors in a 8 mile radius. More market potential. 

tot <- table(surg$community)
as.matrix(tot[order(tot, decreasing = TRUE)])
#The farmington market undergoes more eye surgeries currently than South Jordan. It also ranks 5th 
#compared to all comminuties. However, South Jordan is adjacent to more markets and may undergo more than ~765
#surgeries annually. Mid davis county is fairly isolated. 


# Research Question 3 -----------------------------------------------------
#About how many eye surgeries will people in those same markets undergo 5 years from
#now? How will that compare to other communities/markets?

hist(surg[surg$gender == 'M', 'age'])
hist(surg[surg$gender == 'F', 'age']) #These look the same. 
hist(surgSJ$age) #Age is more influencial
mean(surg$gender == 'F') #About 57% are females.
#Note that this eye surgeries are largely dependent on age. Assuming that the average number of surgeries/person in each
#age group is constant, we can calculate the total. We will pool both genders together. 
comms <- rownames(tot)
#Returns list of zip codes for each community
comm.zip <- function(comm){
  zip[zip$community == comm,1]
}
sjZips <- comm.zip("South Jordan")
fZips <- comm.zip("Mid Davis Co")

#Function that predicts 2021 surgeries for any list of zip codes
pred2021.surg <- function(zips){
  pop2016 <- as.matrix(colSums(pop[pop$zipcode %in% zips,-c(1:2)]))[1:36]
  pop2021 <- as.matrix(colSums(pop[pop$zipcode %in% zips,-c(1:2)]))[37:72]
  
  #Aggregate Male/Female together. Assume independence
  age2016 <- pop2016[1:18] + pop2016[19:length(pop2016)]
  names(age2016) <- seq(0,85,5)
  age2021 <- pop2021[1:18] + pop2021[19:length(pop2016)]
  names(age2021) <- seq(0,85,5)
  
  subSurg <- surg[surg$zip_code %in% zips,]
  tot2016 <- c(sum(subSurg$age == 0), tabulate(subSurg$age)[seq(0,85,5)])
  perc2016 <- tot2016/age2016
  #round(perc2016, 5)
  tot <- sum(tot2016)
  
  #matrix multiplication for weighted total.
  list(age2021 %*% perc2016, (age2021 %*% perc2016 - tot)/tot, 'age2016' = age2016, 
       'totSurg' = tot2016, '%popSurg' = perc2016, 'age2021' = age2021) 
}

pop.2016 <- function(z){
  sum(pred2021.surg(z)$age2016)
}
popul <- sapply(comms, function(x) pop.2016(comm.zip(x)))
as.matrix(popul[order(popul, decreasing = TRUE)])

unlist(pred2021.surg(sjZips)[1:2])
#About 930 Surgeries or 21.5% increase in South Jordan
unlist(pred2021.surg(fZips)[1:2])
#About 1927 surgeries or 19% increase in Farmington


pred2021 <- sapply(comms, function(x) pred2021.surg(comm.zip(x))[[1]])
as.matrix(pred2021[order(pred2021, decreasing = TRUE)])
avgSurg <- round(tot / popul,3)
#Note that Mid Davis Co is now ranked 4th (probably due to the older demographic) for the most number of eye surgeries.
#South Jordan remains about the same relative to the other communities/markets


# Research Question 4 -----------------------------------------------------
#What percentage of eye surgeries in those same markets are paid for by commercial
#insurance? How does that compare to other communities/markets?

totIns <- function(z){
  Insurance <- surg[surg$zip_code %in% z,'insurance']
  table(Insurance) / length(Insurance)
}
totIns(sjZips)
totIns(fZips)

insMarket <- as.matrix(t(sapply(comms, function(x) totIns(comm.zip(x)))))
insMarket[order(insMarket[,1]),]
mean(surg$insurance == 'commercial') #Avg 44%

#In 2016, 41.6% of eye surgeries were paid for by commercial insurance in the farmington market, whereas
#54.9% were paid for by commercial insurance in the South Jordan market. South Jordan has one of the highest
#percentage of eye surgeries covered by insurance in the valley. The farmington market is below the average
#for the valley.


# Research Question 5 -----------------------------------------------------
#What percentage of people in those markets have insurance that allows them access to
#UHealth services? How does that compare to other communities/markets?

#Weighted average of zip access populations. Get total population of each zip code
zipPop <- cbind.data.frame(as.character(pop[,1]), rowSums(pop[,3:38]))
colnames(zipPop) <- c('zipcode', 'pop')
zipPAcc <- merge(zipPop, insAcc[,-2], by = 'zipcode', all = TRUE)

zipPAcc[zipPAcc$zipcode %in% sjZips,] #Caution 19,990 of population has unknown data

#Caucluates a weighted average. Returns % access and total number of people with no data
weighted.perc <- function(z){
  t <- zipPAcc[zipPAcc$zipcode %in% z,]
  naPop <- sum(t[is.na(t[,3]) ,2])
  c('Perc' = weighted.mean(t[,3], t[,2], na.rm=TRUE), 'Ignored' = naPop)
}

perc <- as.matrix(t(sapply(comms, function(x) weighted.perc(comm.zip(x)))))
perc[order(perc[,1], decreasing= TRUE),]
mean(perc[,1])

#South Jordan (55%), Farmington (66%). South Jordan is lower than most markets, but it also has 19,900 people
#that are uncatagorized. Farmington is near the middle compared to other markets.  
#Table showing number of people in South Jordan Zip codes who went to UHealth. 
table(surgSJ[surgSJ$facility_name == 'university of utah health','zip_code'])

# Research Question 6 -----------------------------------------------------
#What is UHealth's current market share in those markets? How does that compare to other communities/markets?

market.share <- function(z){
  surgSub <- surg[surg$zip_code %in% z,]
  t <- table(surgSub$facility_name)
  as.numeric(t['university of utah health'] / sum(t))
}

shares <- sapply(comms, function(x) market.share(comm.zip(x)))
as.matrix(shares[order(shares, decreasing = TRUE)])

#UHealth's market shares are 48% for South Jordan and 21% for farmington. Both markets are about average
#when compared to other markets. When ranked, they divide the whole industry into thirds. 

# Research Question 7 -----------------------------------------------------
#What facilities are UHealth's main competition in the markets of Farmington and South Jordan?

sjFac <- table(surgSJ$facility_name)
fFac <- table(surgFarm$facility_name)

#Ratios to UHealth share
as.matrix(sort(sjFac, decreasing = TRUE)) / as.numeric(sjFac['university of utah health'])
as.matrix(sort(fFac, decreasing = TRUE)) / as.numeric(fFac['university of utah health'])


#For South Jordan: U of U health dominates the market, but Intermountain Medical center 
#and partially alta view hospital/st. marks are sources of competition. 
#For Farmington: Davis Hospital & Medical center (has more market shares), mountain west surgical center, 
#Mckay Dee surgical center, and mount Ogden surgical center are soruces of competition. 


# Research Question 8 -----------------------------------------------------

table(surgSJ$service) #These are relatively balanced. May require many different optomologists
table(surgFarm$service) #Most of these are cataracts. We can capitalize on this!

#From Question 1-2:
#Farmington has more annually, but SJ could potentially have more from surrounding markets. 
nrow(surgSJ) #765 annually
nrow(surgFarm) #1619 annually

hist(surgSJ[,8], br=25, main='S. Jordan travel distance', xlab='miles')
round(as.matrix(table(surgSJ[surgSJ$Dist > 10, 'facility_name']) / nrow(surgSJ[surgSJ$Dist > 10,])),4) 
#Most people (70%) who travel more than 10 miles in SJ are already going to UHealth.


hist(surgFarm[,8], br=20, main='Farmington travel distance', xlab='miles')
as.matrix(table(surgFarm[surgFarm$Dist > 10, 'facility_name'])/ nrow(surgFarm[surgFarm$Dist > 10,]))
#About 42% of people that travel far go to Uhealth
metrics <- cbind('NumSurg'= tot, popul, 'avgSurg' = avgSurg)
metrics[order(metrics[,1], decreasing=TRUE),]
#Mid Davis co. compares well. S. Jordan isn't as high, but it has more neighbors. 

#From Question 3
#Assuming that the average # of surgeries is constant with each age group.
predMetrics <- cbind('pred2021' = round(pred2021,1), 'growth' = round(100*(pred2021/tot-1),1))
predMetrics[order(predMetrics[,1], decreasing = TRUE),]
#Both are expected to increase by about 20%. Mid Davis co. has far more volumes of surgeries available and
#is now 4th largest in the Wastach front area. South Jordan has potential for growth. 

#Question 4
round(insMarket[order(insMarket[,1], decreasing = TRUE),],4)*100
#South Jordan has more that take commercial insurance (54%), whereas Farmington's market only has 41%. South
#Jordan has the 2nd highest 

#Question 5
round(perc[order(perc[,1], decreasing= TRUE),],4)
#About 66% of people in Mid Davis co. have access to UHealth through their insurance, compared to 55% from 
#South Jordan. However, 19,975 people we don't have data for. If everyone of those has insurance:
(.47*906+45119*.5519+1*19975)/(906+19975+45519)#68%
(.47*906+45119*.5519+0*19975)/(906+19975+45519) #38% if none have insurance
19975/(906+19975+45519) #30% missing

#Question 6
round(as.matrix(shares[order(shares, decreasing = TRUE)]),4)
#UHealth's market shares are 48% for South Jordan and 21% for farmington. Both markets are about average
#when compared to other markets. When ranked, they the whole industry into thirds. Winner: Farmington

#Question 7
as.matrix(sort(sjFac, decreasing = TRUE)) 
as.matrix(sort(fFac, decreasing = TRUE))
#For South Jordan: U of U health dominates the market, but Intermountain Medical center 
#and partially alta view hospital/st. marks are sources of competition. 
#For Farmington: Davis Hospital & Medical center (has more market shares), mountain west surgical center, 
#Mckay Dee surgical center, and mount Ogden surgical center are soruces of competition. 
