# Project Code


# Data Cleaning\ ----------------------------------------------------------
weather <- read.csv('provo_snow.csv')[,-c(1,8)] # Only took years after 2008
snow_days <- weather[(weather$SNOW != 0) & (!is.na(weather$SNOW) ) & (weather$YEAR >= 2008), c(1:3)]
snow <- snow_days[,3]
hist(snow, breaks=20, main='Provo Snowfall (Jan 2008 - Apr 2018)', xlab = 'Inches', col='lightsteelblue')
hist(snow, breaks=20,freq=FALSE, xlab='Inches', main='Reported Snowfall', col='lightsteelblue2')


# Gamma -------------------------------------------------------------------
llik.gamma <- function(x, data=snow){
  alp <- x[1]
  lam <- x[2]
  if( alp <= 0 || lam <= 0) return(-Inf)
  -sum(dgamma(data, alp, lam, log=TRUE))
}
gam.par <- optim(c(1,1), function(x) llik.gamma(x))$par #MLE 1.32, .684
curve(dgamma(x, gam.par[1], gam.par[2]), col='red', add=TRUE, lwd=2)



# Lognormal ---------------------------------------------------------------

llik.ln <- function(x, data=snow){
  mu <- x[1]
  sigma <- x[2]
  if( sigma <= 0) return(-Inf)
  -sum(dlnorm(data, mu, sigma, log=TRUE))
}
ln.par <- optim(c(1,1), function(x) llik.ln(x))$par # MLE .238, .966
curve(dlnorm(x,ln.par[1] , ln.par[2]), col='blue', add=TRUE, lwd=2)



# Burr --------------------------------------------------------------------
dburr <- function(x, c, k, log=FALSE) {
  if (length(x) > 1) return(sapply(x, function(t) dburr(t, c,k,log)))
  if (x > 0){
    l <- log(c) + log(k) + (c-1)*log(x) - (k+1)*log(1+x^c)
  } else{
    l <- -Inf
  }
  if (!log) return(exp(l))
  return(l)
}
pburr <- function(x,c,k) (1-(1+x^c)^(-k))*(x>0)

llik.burr <- function(x, data=snow){
  c <- x[1]
  k <- x[2]
  if( c <= 0 || k <= 0) return(-Inf)
  -sum(dburr(data, c, k, log=TRUE))
}
burr.par <- optim(c(1,1), function(x) llik.burr(x))$par #c=1.91, k=.783
curve(dburr(x, burr.par[1], burr.par[2]), col='green', add=TRUE, lwd=2)
legend('topright', c('Gamma', 'Lognormal', 'Burr'), col=c('red', 'blue', 'green'), lwd=2, cex=.9)



# Analysis ----------------------------------------------------------------

library(goftest)
ksad.test <- function(data, title='Emperical CDF (data)', plotit=FALSE){
  stats <- matrix(NA,nrow=6, ncol=2)
  
  stats[1,] <- unlist(ks.test(data, 'pgamma', shape=gam.par[1], rate=gam.par[2])[1:2])
  stats[4,] <- unlist(ad.test(data, 'pgamma', shape=gam.par[1], rate=gam.par[2])[1:2])
  stats[2,] <- unlist(ks.test(data, 'plnorm', meanlog=ln.par[1], sdlog=ln.par[2])[1:2])
  stats[5,] <- unlist(ad.test(data, 'plnorm', meanlog=ln.par[1], sdlog=ln.par[2])[1:2])
  stats[3,] <- unlist(ks.test(data, pburr, c=burr.par[1], k=burr.par[2])[1:2])
  stats[6,] <- unlist(ad.test(data, pburr, c=burr.par[1], k=burr.par[2])[1:2])
  row.names(stats) <- c("Gamma-KS", "Lognorm-KS","Burr-KS", "Gamma-AD", "Lognorm-AD", "Burr-AD")
  colnames(stats) <- c("D.Stat", "P.Value")
  if(plotit){
    plot(ecdf(data), main=title)
    curve(pgamma(x, gam.par[1], gam.par[2]), col='red', add=TRUE, lwd=2)
    curve(plnorm(x, ln.par[1], ln.par[2]), col='blue', add=TRUE, lwd=2)
    curve(pburr(x, burr.par[1], burr.par[2]), col='green', add=TRUE, lwd=2)
    legend('right', c('Gamma', 'Lognormal', 'Burr'), col=c('red', 'blue', 'green'), lwd=2, cex=.7)
    stats[,2] <- round(stats[,2], 8)
  }
  stats
}

ksad.test(snow) # Lognormal is best for both


# Simulation Study --------------------------------------------------------

rburr <- function(n, c, k) (runif(n)^(-1/k)-1)^(1/c)
g <- c(2, .5)
l <- c(1, .5)
b <- c(.5, 2)



tests.sim <- function(){
  gams <- rgamma(length(snow), gam.par[1], gam.par[2])
  lns <- rlnorm(length(snow), ln.par[1], ln.par[2])
  burs <- rburr(length(snow), burr.par[1], burr.par[2])
  
  list(ksad.test(gams, 'Gamma Data ECDF'), 
       ksad.test(lns, 'LogNorm Data ECDF' ),
       ksad.test(burs, 'Burr Data ECDF'))
}
Nsim <- 1e4
runs <- lapply(1:Nsim, function(x) tests.sim())
tally <- function(m){
  k <- as.numeric(which.max(m[1:3,2]))
  a <- as.integer(which.max(m[4:6,2]))
  tal <- numeric(6)
  tal[k] <- tal[3+a] <- 1
  tal
}

# Gamma Results
Gs <- lapply(runs, function(x) x[[1]]) 
Reduce('+', Gs)/Nsim # Average
Reduce('+', lapply(Gs, function(x) tally(x)))/Nsim # Proportion Correct
cbind(round(Reduce('+', Gs)/Nsim,4), '% Best' = Reduce('+', lapply(Gs, function(x) tally(x)))*100/Nsim)

# Lognormal
Ls <- lapply(runs, function(x) x[[2]])
cbind(round(Reduce('+', Ls)/Nsim,4), '% Best' = Reduce('+', lapply(Ls, function(x) tally(x)))*100/Nsim)

# Burr
Bs <- lapply(runs, function(x) x[[3]])
cbind(round(Reduce('+', Bs)/Nsim,4), '% Best' = Reduce('+', lapply(Bs, function(x) tally(x)))*100/Nsim)

set.seed(0)
ksad.test(gams, 'Gamma Sample ECDF', plotit=TRUE) # Gamma is best for both
ksad.test(lns, 'LogNorm Sample ECDF', plotit=TRUE) #Lognormal is best for both
ksad.test(burs, 'Burr Sample ECDF', plotit=TRUE) # Burr is best for both!




