
# Monte Carlo Simulation basics -------------------------------------------

# Sometimes we don't have data because it's too expensive, will take too long to collect, or the event hasn't happened yet.
# BUT, we still want to make inferences and predictions. One approach is to create the data ourselvs through simulation
# studies. While it depends on the complexity of the problem, computers can often do thousands of runs in a few seconds.

# Caveat: Due to the randomness of simulations, the estimates will be subject to a small error (called monte carlo error).
# As a result, our estimates will not be exact, but close approximations. 


# Halloween Problem -------------------------------------------------------
# It's halloween night! However, you are a lazy citizen and are tired of repeatedly getting up to answer the door every 5 minutes.
# Instead, you decide to leave your candy outside and leave a note to take two, but your know full well people will take more than that.
# Your goal is to model the amount of people that come and candy they take so that you'll have just enough for everyone. 


# We'll need to model: 
# Number of people that come per night (rounded normal)
# Number of pieces of candy they take poisson + 1
# 5% chance someone takes 10 more pieces of candy than usual. 

# On average, how much candy would you hand out in one night?
halloween.night <- function(){
  numpeople <- rnorm(1, 300, 20)
  tot.candy <- 0
  for (i in 1:numpeople){
    candy <- 0
    candy <- rpois(1, 1.5) + 1
    if (runif(1) < .05){
      candy <- candy + 10
    }
    tot.candy <- tot.candy + candy
  }
  tot.candy
}
Nsim <- 10000
nights <- sapply(1:10000, function(x) halloween.night())

hist(nights)
mean(nights)
# How much candy should you buy so that you won't run out? 
# (You want to be 95% sure, meaning you would have enough for 95% of the simulated nights)
quantile(nights, .95) #1020


# Simulation Practice -----------------------------------------------------

# Back to the dice example
roll.dice <- function(nRolls, nSides=6){     # User specifies amount rolled, number of sides by default is 6
  sample(1:nSides, nRolls, replace = TRUE)   
}

# Strategy: 
# 1) Use roll.dice to make a function that returns the result after 1 trial
# 2) Use sapply/for loop to run the simulation many times (100000+)
# 3) Count the proportion of trails that meet the specified criteria


# Example: You roll 4 dice, what's the aprox. probability at least one of them is a 6? ---------------------------------
# This will compare for each roll, and sum will add the Trues, counting the number of 6s 
count6s <- function(nDice){
  sum(roll.dice(nDice) == 6) 
}

set.seed(0)
results <- sapply(1:10000, function(x) count6s(4))
mean(results > 0) # Mean of trues and falses = proportion of Trues

set.seed(0) # Can also do this on one line
mean(sapply(1:10000, function(x) (sum(roll.dice(4) == 6))) > 0)

# You roll 3 dice, what is the approx. probability that you roll a sum of 7? -------------------------------------------
mean(sapply(1:10000, function(x) sum(roll.dice(3))) == 7) #6.8%


# You roll 5 dice, what is the approx. probability of rolling a full house (3 of 1 number, 2 of another) ---------------
# (Hint: Table function may be useful)
full.house <- function(roll){
  freqs <- as.vector(table(roll.dice(5)))
  print(freqs)
  if ((3 %in% freqs) & (2 %in% freqs)){
    print("Full House")
    return(TRUE)
  }
    return(FALSE)
}
mean(sapply(1:10000, function(x) full.house(roll.dice(5)))) #4%


# What's the approx. probability of rolling 3 of the same number in a row in a sequence of 10 rolls?--------------





