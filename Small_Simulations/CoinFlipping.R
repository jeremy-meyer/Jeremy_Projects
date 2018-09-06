
# Suppose you flip a number of coins (l) and want to know the chance of flipping a streak of n Heads
coinflip <- function(l){
  coin <- sample(c('H', 'T'), l, replace = TRUE)
  maxrun <- 1
  streak <- 1
  for (i in 1:(length(coin)-1)){
    if((coin[i] == 'H') & (coin[i+1] == 'H'))
    {
      streak <- streak+1
      maxrun <- max(streak, maxrun)
    } else {
      streak <- 1
    }
  }
  return(list(maxrun, coin))
}

# nCoins = Number of coins to flip. Will find max streak of Heads in the sequences.
nCoins <- 10000
nRuns <- 1000
sims <- sapply(1:nRuns, function(x) coinflip(l=nCoins)[[1]])
# Approximate Monte Carlo Probabilities for a max streak of n
table(sims) / nRuns

# Probability of flipping a streak of n Heads or more:
n <- 15
mean(sims >= n)
