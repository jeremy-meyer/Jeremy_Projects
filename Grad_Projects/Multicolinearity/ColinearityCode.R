# 535 Project

# Motivating example: Y = Time = Bridge time prediction (days)
# Helpful for budgeting and internal/external scheduling purposes

# Covariates:
# x1 = DArea = Deck area of bridge (000 sq ft)
# x2 = CCost = Construction cost ($000)
# x3 = Dwgs = Number of structural drawings
# x4 = Length = Length of bridge (ft)
# x5 = Spans = Number of spans

library(alr3)
Nsim <- 1e3
bridge <- read.table('http://gattonweb.uky.edu/sheather/book/docs/datasets/bridge.txt', header=TRUE)
fit <- lm(log(Time) ~ log(DArea) + log(CCost) + log(Dwgs) + log(Length) + log(Spans), data=bridge)
plot(fit) # These all look fine, except for a few leverage points

par(mfrow=c(1,3))
plot(fit, which=2)
plot(fit, which=3)
plot(fit, which=5)

pairs(cbind('log(Time)' = log(bridge$Time), model.matrix(fit)[,-1])) # All the Xs are correlated
summary(fit)
# Problems: Because the xs are carrying similar information, it's hard for the regression model
# to distinguish the effects between the covariates.
# 1) A couple of the covariates now have negative estimates!
# 2) ANOVA test with intercept only model (reduced) and full model is highly significant,
# but only 1 covariate is significant.


# VIF ---------------------------------------------------------------------
vif(fit) # Variance inflation factors
X <- model.matrix(fit)[,-1]
1/(1-summary(lm(X[,1] ~ X[,2] + X[,3] + X[,4] + X[,5]))$r.squared)

# Simulation Study --------------------------------------------------------

# Reserach question: What is an appropriate cutoff for the Variance inflation factor so
# the significance tests for the betas are still reasonable?

# Consider the model y ~ b0 + b1*x1 + b2*x2 + b3*x3 + b4*x4 + b5*x5 + eps, eps ~ N(0,sigma2*I)
# Only one of the betas (beta1) is significant. Other Xs are correlated.

# Calculates appropriate r^2 for a given vif
getR2 <- function(VIF){
  1-1/VIF
}

# Assume the variances between the Xs/correlations are the same
getCovMatr <- function(dim, rho.x, sigma2){
  covMatr <- matrix(sigma2, nrow=dim, ncol=dim)
  for(i in 1:dim){
    for(j in i:dim){
      if (i != j){
        covMatr[i,j] <- covMatr[j,i] <- covMatr[i,j]*rho.x
      }
    }
  }
  covMatr

}

# Generating data
p <- 5
sigma2 <- 1

getX <- function(n, p, rho){
  X <- matrix(NA, nrow=n,ncol=p)
  for (i in 1:n){
    X[i,] <-t(t(chol(getCovMatr(p, rho, sigma2)))%*%matrix(rnorm(p), ncol=1))
  }
  X
}

VIF <- diag(solve(cor(getX(45, 5, 0))))
mean(sapply(1:2000, function(x) mean(diag(solve(cor(getX(nrow(bridge), 5, .99)))))))

pow1 <- function(beta1,p,rho,n=nrow(bridge)){
  beta <- matrix(0, nrow=(p+1))
  beta[2] <- beta1

  X <- cbind(1, getX(n,p,rho))
  Xr <- X[,-2]
  Y <- rnorm(nrow(X), X %*% beta, sigma2^.5)

  fullSSE <- sum((Y-X%*%(solve(t(X)%*%X)%*%t(X)%*%Y))^2)
  redSSE <- sum((Y-Xr%*%(solve(t(Xr)%*%Xr)%*%t(Xr)%*%Y))^2)

  df1 <- (nrow(Xr) - ncol(Xr)) - (nrow(X) - ncol(X))
  df2 <- (nrow(X) - ncol(X))

  F.stat <-( (redSSE - fullSSE) / df1 ) / ( fullSSE/df2)
  1-pf(F.stat, df1, df2)
}

getPower <- function(b1, p, rho, Nsim=2e3){
  mean(sapply(1:Nsim, function(x) pow1(b1,p,rho)) < 0.05)
}

beta1s <- seq(0,2,.1)
plot(beta1s, rep(.05, length(beta1s)), type='l', lty=3, ylim=c(0,1), col='red',
    main=expression(paste('Power Curve for ', beta[1])), ylab='Power',
    xlab=expression(paste(beta[1])))

VIFs <- c(1, 3, 5, 7.5, 10, 15, 20, 100)
rhos <- sapply(VIFs, getR2)
rhos <- c(0, .690, .815, .877, .907, .938, .954, .991)
cols <- c('Black', 'Purple', 'Blue', 'turquoise3', 'green', 'yellow3','orange', 'red')

powers <- matrix(NA, nrow=length(beta1s), ncol=length(rhos))
colnames(powers) <- VIFs
row.names(powers) <- beta1s
for(i in 1:length(rhos)){
  #powers[,i] <- sapply(beta1s, function(x) getPower(x, p, rhos[i]))
  lines(beta1s, powers[,i], col=cols[i], lwd=2)
}

entry <- paste0(format(rhos, nsmall=2, digits=2), ' (', VIFs, ")")
legend('topleft', title=expression(paste(rho, " (VIF)")), legend=entry,lty=1, col=cols, cex=.6, seg.len = 1.5, lwd=2)
powers.old <- powers



# Do more than 100 Nsim
# Choose different values of Rho.
# Table check for type 1 errors

