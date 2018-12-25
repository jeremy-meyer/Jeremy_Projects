
# Suppose the prices in a stock market can be modeled by S = So * e ^ (u + sigma*Z)
# Where:
# S  = price of current day
# So = Price of previous day
# u  = .002 (fixed)
# sig = .03 (fixed)
# Z ~ Random Normal(0,1) (use rnorm)

# Write a function that takes a starting value, parameter u, parameter sigma, and t = number of days to simulate
# Part a ------------------------------------------------
simStock <- function(so, alp, sigma, t){
  stocks <- numeric(t)
  stocks[1] <- so
    
  for(i in 2:t){
    stocks[i] <- stocks[i-1]*exp(alp+sigma*rnorm(1))
  }
  stocks
}

# Let's say the stock starts at So=100, and you're interested in the price after 90 days
# Plot one (or a few) simulated stocks in one graph (use lines() to do multiple plots)
# Part b ------------------------------------------------
path <- simStock(100,.002,.03,90)
path2 <- simStock(100,.002,.03,90)
path3 <- simStock(100,.002,.03,90)
plot(1:90, path, main='Stock path of 90 days', xlab='Day', ylab='Stock', type='l', ylim=c(80,150))
lines(1:90, path2, col='red')
lines(1:90, path3, col='blue')
abline(h=100, lty=2)

# If you have to sell after 90 days, would this be a worthwile investment?
# (Hint: Simulate stock time series prices for 90 days and take the last one 10000 times)
# Part c ------------------------------------------------
Nsim <- 1e4
day <- 90
set.seed(0)
draws <- sapply(1:Nsim, function(x) simStock(100, .002, .03, day)[day])
mean(draws)+c('est' = 0, 'lwr'=-1, 'upr'=1)*qt(.975, Nsim-1)*sd(draws)/sqrt(Nsim)
mean(draws > 100) # 73% above orginial price! 
# We estimate a mean of about 124.28 

# Plot a histogram of the possible values of the stock after 90 days. 
# Part d ------------------------------------------------
hist(draws, main="Stock Price Density Estimate after 90 days", xlab="Stock Price", breaks=30)
abline(v=100, col='red', lwd=2)
