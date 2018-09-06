# This models the total number of minecraft tool uses with different levels of enxhants. 
# We can model the total number of uses using a negative binomial distrubition.

#Using Iron Pickaxe. Durability = 251. Diamond 1562 uses. Elytra = 431
#Unbreaking I = 50% chance to reduce durability. 
TOOL_DUR  <- 1562
UB1 <- 0.5
UB2 <- 1/3
UB3 <- 0.25
xx <- 0:(TOOL_DUR *4) #Range of values

numUses <- data.frame(xx + TOOL_DUR)
numUses <- cbind(numUses, as.numeric(numUses[,1] == TOOL_DUR), dnbinom(xx, TOOL_DUR, UB1), 
                dnbinom(xx, TOOL_DUR, UB2), dnbinom(xx, TOOL_DUR, UB3))
colnames(numUses) <- c('uses', 'None', 'UB1', 'UB2', 'UB3')

plot(numUses[,1],numUses[,'UB1'], col='red', type='l', xlab='Uses', ylab = 'Probability')
abline(v=TOOL_DUR)
lines(numUses[,1],numUses[,'UB2'], col='green', type='l')
lines(numUses[,1],numUses[,'UB3'], col='blue', type='l')

EX <- function(r,p){ #Gives expected failures, r=num sucesses, p=p(success)
  r * (1-p)/p
}
VarX <- function(r,p){ #Variance of number of uses. Note: Shifting on the x-axis doesn't affect variance
    r * (1-p)/p^2
}