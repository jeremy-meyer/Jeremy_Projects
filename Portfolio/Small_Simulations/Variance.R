# Have you ever wondered why we divide by n-1 to calculate the sample variance?
# It turns out dividing by n is a biased estimator. Why? 

# We'll sample from a normal population with mean 0 and "true" variance 1
variance <- function(n, sigma2=1){
  samp <- rnorm(n, 0, sigma2^.5)
  sum((samp-mean(samp))^2/n)
}

varSamp <- function(n, sigma2=1){
  samp <- rnorm(n, 0, sigma2^.5)
  sum((samp-mean(samp))^2/(n-1))
}

pop <- sapply(1:10000, function(x) variance(3))
samp <- sapply(1:10000, function(x) varSamp(3))
mean(pop)    # Note the discrepency
mean(samp) 

n <- c(2,5,10,20,30,50,100,1000)
pop <- sapply(n, function(t) mean(sapply(1:10000, function(x) variance(t))))
samp <- sapply(n, function(t) mean(sapply(1:10000, function(x) varSamp(t)))) 
matrix <- rbind(pop, samp)
colnames(matrix) <- n
rownames(matrix) <- c('Divide by n', 'Divide by n-1')
matrix
#
#      n                2         5        10        20        30        50       100      1000
# Divide by n   0.5026168 0.8038945 0.9066078 0.9491368 0.9657380 0.9792069 0.9912328 0.9991137
# Divide by n-1 0.9995935 1.0025879 1.0053346 1.0026477 0.9979024 1.0009388 1.0028268 0.9997446

# Note that by dividing by n-1, on average, we get closer estimates for the sample vairance. 
