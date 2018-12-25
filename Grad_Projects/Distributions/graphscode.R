
# Hypergeometric Graph

cols <- c('blue', 'steelblue', 'turquoise2')
cols42 <- c('blue', 'steelblue', 'turquoise2', 'seaGreen')
cols4 <- c('red', 'orange', 'blue', 'magenta')

# Bernouli Graph
ps <- c(.1,.5,.75)
xs <- c(-.05,0,.05,.95,1,1.05)
plot(xs, c(dbinom(0,1,ps), dbinom(1,1,ps)), type='h', xlim=c(-.1, 1.1), xaxt = 'n',
     xlab = 'X', ylab = 'P(X=x)', main='Bernoulli(p)', col=cols, lwd=3)
axis(side = 1, at = c(0,1))
legend('top', legend=ps, col=c('steelblue1', 'steelblue', 'turquoise3'), lwd=2.5)

# Binomial Graph
n <- c(15, 15, 40, 40)
ps <- c(.5, .2, .5, .8)
bin.pmf <- sapply(1:length(n), function(x) dbinom(0:n[x], n[x], ps[x]))

plot(0:n[4], bin.pmf[[4]], pch=19, ylim=c(0,.3),
     xlab = 'X', ylab = 'P(X=x)', main='Binomial(n,p)', col='turquoise3', type='b', lty=3)
points(0:n[1], bin.pmf[[1]], pch=19, col='red', type='b', lty=3)
points(0:n[2], bin.pmf[[2]], pch=19, col='orange', type='b', lty=3)
points(0:n[3], bin.pmf[[3]], pch=19, col='blue', type='b', lty=3)
legend('topright', c('n=15, p=.5', 'n=15, p=.2', 'n=40, p=.5', 'n=40, p=.8'), col=c('orange', 'red', 'blue', 'turquoise3'),
       pch=19, lty=3)

# Poisson
lam <- c(1, 5, 10)
xs <- 0:15
y <- sapply(lam, function(x) dpois(xs, x))
plot(xs, y[,1], pch=19,
     xlab = 'X', ylab = 'P(X=x)', main=expression(paste('Poisson(',lambda, ')')), col=cols[1], type='b', lty=3)
points(xs, y[,2], pch=19, col=cols[2], type='b', lty=3)
points(xs, y[,3], pch=19, col=cols[3], type='b', lty=3)
legend('topright',title=expression(lambda), legend=lam, col=cols, lty=3, pch=19)

# Hypergeometric
N <- 50
M <- c(15,15,25,25)
k <-c(5,15,5,15)

hyp.pmf <- sapply(1:4, function(x) dhyper(0:k[x], M[x], N-M[x], k[x]))
plot(0:k[4], hyp.pmf[[4]], pch=19, ylim=c(0, 0.36),
     xlab = 'X', ylab = 'P(X=x)', main='Hypergeometric(M,N,k)', col=cols4[4], type='b', lty=3)
points(0:k[1], hyp.pmf[[1]], pch=19, col=cols4[1], type='b', lty=3)
points(0:k[2], hyp.pmf[[2]], pch=19, col=cols4[2], type='b', lty=3)
points(0:k[3], hyp.pmf[[3]], pch=19, col=cols4[3], type='b', lty=3)
legend('topright', c('M=15, k=5', 'M=15, k=15', 'M=25, k=5', 'M=25, k=15'), col=cols4,
       pch=19, lty=3, title='N=50', cex=.8)


# Negative Binomial
p <- c(0.3, 0.3, 0.7, 0.7)
r <- c(4,8,4,8)

xs <- 0:25
nb.pmf <- sapply(1:length(p), function(x) dnbinom(xs, r[x], p[x]))
plot(xs, nb.pmf[,4], pch=19, ylim=c(0, 0.3),
     xlab = 'X = # failures', ylab = 'P(X=x)', main='Negative_Binomial(p,r)', col=cols4[4], type='b', lty=3)
points(xs, nb.pmf[,1], pch=19, col=cols4[1], type='b', lty=3)
points(xs, nb.pmf[,2], pch=19, col=cols4[2], type='b', lty=3)
points(xs, nb.pmf[,3], pch=19, col=cols4[3], type='b', lty=3)
legend('topright', c('p=0.3, r=4', 'p=0.3, r=8', 'p=0.7, r=4', 'p=0.7, r=8'), col=cols4,
       pch=19, lty=3)

# Geometric
p <- c(0.2, 0.5, 0.8)
xs <- 0:10
geom.pmf <- sapply(1:length(p), function(x) dnbinom(xs, 1, p[x]))
plot(xs, geom.pmf[,3], pch=19, ylim=c(0, 0.8),
     xlab = 'X = # failures', ylab = 'P(X=x)', main='Geometric(p)', col=cols[3], type='b', lty=3)
points(xs, geom.pmf[,1], pch=19, col=cols[1], type='b', lty=3)
points(xs, geom.pmf[,2], pch=19, col=cols[2], type='b', lty=3)
legend('topright', c('p=0.2','p=0.5', 'p=0.8'), col=cols,
       pch=19, lty=3)

# Gamma
alp <- c(0.5, 2, 4, 40)
bet <- c(2, 0.5, 2, 20)

xs <- seq(0, 10, .1)
curve(dgamma(x, alp[1], bet[1]), xlim=c(0,8), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Gamma(',alpha, ', rate=', beta, ')')))
sapply(2:length(alp), function(t) curve(dgamma(x, alp[t], bet[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', c('G(0.5, 2)','G(2, 0.5)', 'G(4, 2)', 'G(40, 20)'), col=cols4,
       lwd=2)

# Inverse gamma
library(invgamma)
alp <- c(0.5, 0.5, 4, 4)
bet <- c(0.5, 2, 2, 0.5)
curve(dinvgamma(x, alp[1], bet[1]), xlim=c(0,6), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('InvGamma(',alpha, ', rate=', beta, ')')), ylim=c(0,2))
sapply(2:length(alp), function(t) curve(dinvgamma(x, alp[t], bet[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', c('IG(0.5, 0.5)','IG(0.5, 3)', 'IG(4, 2)', 'IG(4, 0.5)'), col=cols4,
       lwd=2)

# Exponential
lam <- c(0.5, 1, 2)
curve(dexp(x, lam[1]), xlim=c(0,6), lwd=2, col=cols[1], xlab='X', ylab='density',
      main=expression(paste('Exponential(rate =', lambda, ')')), ylim=c(0,2))
sapply(2:length(alp), function(t) curve(dexp(x, lam[t]), lwd=2, col=cols[t], add=TRUE))
legend('topright', c(expression(paste(lambda,' = ', 0.5, "   ")),expression(paste(lambda,' = ', 1)), expression(paste(lambda,' = ', 2))), col=cols,
       lwd=2)

# Normal
mu <- c(-1,-1,5,5)
sigma <- c(1,3,1,3)
curve(dnorm(x, mu[1], sigma[1]), xlim=c(-6,11), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Normal(',mu, ',', sigma, ')')), ylim=c())
sapply(2:length(alp), function(t) curve(dnorm(x, mu[t], sigma[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(mu,' = ', -1, ',', sigma, ' = ', 1,"      ")),
         expression(paste(mu,' = ', -1, ',', sigma, ' = ', 3)),
         expression(paste(mu,' = ', 5, ',', sigma, ' = ', 1)),
         expression(paste(mu,' = ', 5, ',', sigma, ' = ', 3))
         ))

# Beta
alp <- c(0.5,3,2,8)
beta <- c(0.5,3,8,2)
curve(dbeta(x, alp[1], beta[1]), xlim=c(0,1), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Beta(',alpha, ',', beta, ')')), ylim=c(0,3.5))
sapply(2:length(alp), function(t) curve(dbeta(x, alp[t], beta[t]), lwd=2, col=cols4[t], add=TRUE))
legend('top', col=cols4, lwd=2, cex=.75,
       c(expression(paste(alpha,' = ', 0.5, ',', beta, ' = ', 0.5,"      ")),
         expression(paste(alpha,' = ', 3, ',', beta, ' = ', 3)),
         expression(paste(alpha,' = ', 2, ',', beta, ' = ', 10)),
         expression(paste(alpha,' = ', 10, ',', beta, ' = ', 2))
       ))

# Cauchy
mu <- c(-1,-1,4,4)
sigma <- c(1,3,1,3)
curve(dcauchy(x, mu[1], sigma[1]), xlim=c(-5,10), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Cauchy(',mu, ',', sigma, ')')))
sapply(2:length(alp), function(t) curve(dcauchy(x, mu[t], sigma[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(mu,' =', -1, ',', sigma, ' = ', 1,"      ")),
         expression(paste(mu,' =', -1, ',', sigma, ' = ', 3)),
         expression(paste(mu,' =   ',4, ',', sigma, ' = ', 1)),
         expression(paste(mu,' =   ',4, ',', sigma, ' = ', 3))
       ))

# Chi Squared
df <- c(1, 2, 3, 6)
curve(dchisq(x, df[1]), xlim=c(0,8), lwd=2, col=cols42[1], xlab='X', ylab='density',
      main=expression(paste('Chi-Squared ',chi['(k)']^2)), ylim=c(0, 0.8))
sapply(2:length(df), function(t) curve(dchisq(x, df[t]), lwd=2, col=cols42[t], add=TRUE))
legend('topright', title="k (df)",legend=df, col=cols42,
       lwd=2)

# Lognormal
mu <- c(0,0,1,-0.5)
sigma <- c(1,.5,1,1)
curve(dlnorm(x, mu[1], sigma[1]), xlim=c(0,5), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Lognormal(',mu, ',', sigma, ')')), ylim=c(0, 1.1))
sapply(2:length(alp), function(t) curve(dlnorm(x, mu[t], sigma[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(mu,' = ', 0, ', ', sigma, ' = ', 1,"        ")),
         expression(paste(mu,' = ', 0, ', ', sigma, ' = ', 0.5)),
         expression(paste(mu,' = ', 1, ', ', sigma, ' = ', 1)),
         expression(paste(mu,' =', -.5, ',', sigma, ' = ', 1))
       ))

# Double Exponential
ddexp <- function(x, mu, b){
  1/(2*b)*exp(-1/b*abs(x-mu))
}

mu <- c(0,0,1,-1)
sigma <- c(1,0.5,1,2)
curve(ddexp(x, mu[1], sigma[1]), xlim=c(-4,4), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Laplace(',mu, ', b)')), ylim=c(0, 1.1))
sapply(2:length(alp), function(t) curve(ddexp(x, mu[t], sigma[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(mu,' = ', 0, ', ', "b = 1")),
         expression(paste(mu,' = ', 0, ', ', "b = 2")),
         expression(paste(mu,' = ', 1, ', ', "b = 1")),
         expression(paste(mu,' =', -1, ',', "b = 0.5    "))
       ))

# F distribution
d1 <- c(5,2,10,10)
d2 <- c(2,5,10,100)
curve(df(x, d1[1], d2[1]), xlim=c(0,4), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('F(',df[1], ',', df[2], ')')), ylim=c(0, 1.1))
sapply(2:length(alp), function(t) curve(df(x, d1[t], d2[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(df[1],' = ', 5, ', ', df[2], ' = ', 2,"        ")),
         expression(paste(df[1],' = ', 2, ', ', df[2], ' = ', 5)),
         expression(paste(df[1],' = ', 10, ', ', df[2], ' = ', 10)),
         expression(paste(df[1],' =', 10, ',', df[2], ' = ', 100))
       ))

# T-dist
d1 <- c(1,5,30)
curve(dt(x, d1[1]), xlim=c(-4,4), lwd=2, col=cols[1], xlab='X', ylab='density',
      main=expression(paste(t[df])), ylim=c(0, 0.45))
sapply(2:length(alp), function(t) curve(dt(x, d1[t]), lwd=2, col=cols[t], add=TRUE))
curve(dnorm(x), add=TRUE, lty=2, lwd=1.5)
legend('topright', col=c(cols, 'black'), lwd=c(2,2,2,1), cex=.75, lty=c(1,1,1,2),
       c(expression(paste(df,' = ', 1)),
         expression(paste(df,' = ', 5)),
         expression(paste(df,' = ', 30)),
         'Norm(0,1)'
       ))

# Weibull(k,lamb)
shape <- c(0.5,1,2,4)
scale <- c(1,2,0.5,2)

curve(dweibull(x, shape[1], scale[1]), xlim=c(0,4), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Weibull(', gamma, ',', beta, ')')), ylim=c(0,2))
sapply(2:length(shape), function(t) curve(dweibull(x, shape[t], scale[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(gamma,' = ', 0.5, ', ', beta, ' = ', 1,"        ")),
         expression(paste(gamma,' = ', 1, ', ', beta, ' = ', 1)),
         expression(paste(gamma,' = ', 2, ', ', beta, ' = ', 0.5)),
         expression(paste(gamma,' =', 4, ',', beta, ' = ', 2))
       ))

# Pareto
dpareto <- function(x,a,b) b*a^b/x^(b+1)*(x>a)

alp <- c(0.5,1,1,2)
beta <- c(0.5,1,2,10)
curve(dpareto(x, alp[1], beta[1]), xlim=c(0,5), lwd=2, col=cols4[1], xlab='X', ylab='density',
      main=expression(paste('Pareto(',alpha, ',', beta, ')')), ylim=c(0,3.5))
sapply(2:length(alp), function(t) curve(dpareto(x, alp[t], beta[t]), lwd=2, col=cols4[t], add=TRUE))
legend('topright', col=cols4, lwd=2, cex=.75,
       c(expression(paste(alpha,' = ', 0.5, ', ', beta, ' = ', 0.5,"      ")),
         expression(paste(alpha,' = ', 1, ', ', beta, ' = ', 1)),
         expression(paste(alpha,' = ', 1, ', ', beta, ' = ', 2)),
         expression(paste(alpha,' = ', 2, ', ', beta, ' = ', 10))
       ))