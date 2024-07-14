# Example Problems

# 1. Create and store a vector of numbers from 1 to 100. Multiply each value by 5
ans1 <- 5*(1:100)
print(ans1)

# 2. Remove the 10th element from the above vector
ans1[-10] # 50 is missing

# 3. Load in a dataframe called mtcars (should be already stored). Print all rows with mpg<15. 
# How many rows are there?
ans3 <- mtcars[mtcars$mpg < 15,]
print(ans3)
print(nrow(ans3)) # 5 rows

# 4. What is the average mpg value for each gear value (3,4,5)?
aggregate(mpg ~ gear, data = mtcars, FUN = mean) # fun(value) ~ groups

# 5 Make a basic plot between the mpg and hoursepower (hp) values in mtcars.
# What is the correlation? Is this expected?
plot(mtcars$hp, mtcars$mpg)
cor(mtcars$hp, mtcars$mpg) # -0.776
# Yes, in general, powerful cars are less fuel efficient at normal driving speeds!
# This is due to higher hp cars being tuned more to performance rather than efficiency and having bulkier engines. 


# 6. Write a for loop / conditional to print out all even numbers between 1-50
for (i in 1:50){
  if (i %% 2 == 0) {
    print(i)
  }
}


# 7. Use for loops to print all pairs of integers that multiply to get 60.
for (i in 1:sqrt(60)){
  if (60 %% i == 0) {
    print(paste0("(", i, ", ", 60/i, ")"))
  }
}

# 8. Write a coin flip function that returns "H" or "T" with 50% probability
coinFlip <- function(){
  # sample(c('T', 'H'), 1, prob = c(0.5, 0.5))
  if (runif(1) < 0.5) {
    return('H')
  } else {
    return('T')
  }
}

# 9. To check your function, plot a basic histogram of the total number of heads/tails
# after running your function 1000 times.
flips1000 <- sapply(1:1000, function(x) coinFlip()) # Can also use replicate()
results <- table(flips1000)
library(ggplot2)
barplot(results)

# 10. Create a simulation to determine the approximate probability of flipping
# exactly 6 heads out of 20 flips.
coinFlipInt <- function(){
  if (runif(1) < 0.5) {
    return(1)
  } else {
    return(0)
  }
}

# Converting to integer (1=Success, 0=failure) allows us to sum the series to get # heads
# sum(replicate(20, coinFlipInt()))

nsim <- 5e4 # 50k
nheads_simulation <- replicate(nsim, sum(replicate(20, coinFlipInt())))
# this will create a vector of trues and falses.
# R converts these to 0s and 1s where 1 = Event of interest.
# Taking avg gets the % of successes

print(paste("Simluated estimate:", mean(nheads_simulation == 6)))
print(paste("Theoretical answer:", choose(20, 6) * (0.5)^6 * (0.5)^(20-6))) # 3.697%



# 11. (Harder) Suppose that you flip 100 coins. Create a simulation and determine
# an approximate probability of flipping consecutive 5+ heads somewhere within the 100 flip sequence? 
# What about 8+ in a row?

# Solution:
# Let 1 = Heads, 0 = Tails
# Assume that a streak of 5 1s indicates success.
# One solution: using a moving (rolling) sum/avg with 5 term window.
# If rolling sum equals 5 at any point in the series --> 5 consecutive heads
# Could also check moving avg = 1

# Method 1: No external libraries
check_consecutive <- function(consec, series_length){
  flips <- replicate(series_length, coinF)
  # Create vector ahead of time for efficiency
  n_full_terms_in_roll_sum <- series_length - consec + 1
  roll_sum <- rep(NA, n_full_terms_in_roll_sum)
  for (i in 1:(n_full_terms_in_roll_sum)){
    roll_sum[i] <- sum(flips[i:(i + consec - 1)])
  }
  return(max(roll_sum)) # Return the max rolling sum in the sequence
}
mean(replicate(10000, check_consecutive(5, 100))==5)
mean(replicate(10000, check_consecutive(8, 100))==8)



# Method2: Using external library (one liner)
library(zoo)
nsim <- 1e4 # 10k
consecutive_int <- 8
mean(replicate(nsim, max(rollmean(replicate(100, coinFlipInt()), consecutive_int))) == 1)

# 5 -> ~81.0%
# 8 -> ~17.1%
