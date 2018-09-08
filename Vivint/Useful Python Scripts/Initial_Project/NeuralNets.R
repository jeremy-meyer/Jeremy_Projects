library(MASS)
library(neuralnet)

set.seed(0)

ts <- sample(1:nrow(infert), round(nrow(infert)*.3), replace=FALSE)
train <- infert[-ts,]

#FALSE for categorical data
nn <- neuralnet(case ~ age + parity + induced + spontaneous, data = train, 
                hidden = c(2,2), linear.output = FALSE, stepmax = 3e5, rep=1)
#Visual
plot(nn)
nn$weights #Weights for each node

#Results with training data
nn$net.result[[1]]
mean((nn$net.result[[1]] > 0.5) == train[,5]) #75% training Accuracy
test.results <- compute(nn, infert[ts, -c(1,5,7,8)])$net.result
mean(infert[ts,5] == (test.results > 0.5)) #79% Testing Accuracy

#Plots weights for each covariate
par(mfrow=c(2,2))
gwplot(nn, selected.covariate = 'age') #Neutral
gwplot(nn, selected.covariate = 'parity') #Negative
gwplot(nn, selected.covariate = 'induced') #Positive
