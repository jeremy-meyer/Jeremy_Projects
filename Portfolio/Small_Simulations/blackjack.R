
# Blackjack (21)
# Goal is to get as close to 21 points as possible without busting in a single run. This uses a standard 52 card face card deck.
# Many variations to the game, I'll use the one where you start with 2 face-up cards and choose to have another card dealt
# Face cards are worth 10 points, Aces are worth either 1 or 11. All others are worth their numeric value.
# If you go over 21 points, you "bust" and recieve no points. 

# To make things easier, I'll treat everything as it's point value and if we get NA, that's an Ace. 
deck <- rep(c(2:10, 10, 10, 10, NA), 4)

# Note: Aces are valued as 11, unless that would result in a bust, then it is a 1. Ace values can change based on drawn cards.
# Quesiton: Given that you have x points, what's the probability of "busting" if you choose to be dealt another card?

calc.Ace.Values <- function(nAces, nonApoints){
  aceVals <- rep(1, nAces)
  avail.points <- 21 - nonApoints - (nAces-1)
  aceVals[1] <- ifelse(avail.points %/% 11, 11, 1)
  aceVals
}


blackjack <- function(deck){
  aceValues <- c()
  points <- 0
  turns <- 0
  deck <- sample(deck) # Shuffles deck
  cards <- deck[1:2]

  turn_board <- matrix(0,ncol=4, nrow=0)
  
  turns <- -1
  while(points < 21){
    turns <- turns + 1
    cards <- deck[1:(2+turns)]
    nAces <- sum(is.na(cards))
    if (nAces == 0){
      points <- sum(cards)
    } else{
      nonAPoints <- sum(cards[!is.na(cards)])
      aceValues <- calc.Ace.Values(nAces, nonAPoints)
      points <- sum(aceValues) + nonAPoints
    }
    turn_board <- rbind(turn_board,c(points, deck[turns+3], points >21, points==21))
  }
  if (nrow(turn_board) != 1){
    turn_board[nrow(turn_board)-1,3:4] <- turn_board[nrow(turn_board),3:4]
    turn_board <- turn_board[-nrow(turn_board),] #removes 'busted' row
  } else{
    turn_board[nrow(turn_board), 2] <- 0
  }
  turn_board <- matrix(turn_board, ncol=4)
  colnames(turn_board) <- c('Points', 'Card Drawn', 'Bust', 'Blackjack')
  list(turn_board, turns)
}

blackjack(deck)

Nsim <- 20000
tests <- lapply(1:Nsim, function(x) blackjack(deck))
bust_data <- Reduce(rbind, lapply(tests, function(x) x[[1]]))

prob.totals <- cbind(aggregate(Bust ~ Points, data=bust_data, mean), 
                     'BlackJk'=aggregate(Blackjack ~ Points, data=bust_data, mean)[,-1])
print(round(cbind(prob.totals, 'Ending' = apply(prob.totals[,-1], 1, sum)),5), row.names = FALSE)
plot(prob.totals[7:17,-3], type='b', main='Pr(Ending | X Points)', ylab='Prob', xlab='Points', col='red')
lines(prob.totals[7:17,-2], type='b', col='blue')
legend('topleft', lty=1, pch=1, col=c('red','blue'), c('P(Busting | Points)', 'P(Blackjack | Points)'))

# What gives? Why is the conditional probability of Pr(Blackjack) constant?
head(bust_data[bust_data[,1] == 20,], 10) # These are the trials where we had 20 points
table(bust_data[(bust_data[,1] == 20) & (bust_data[,4] == 1),2], useNA = 'ifany') # All of these are Aces!
table(bust_data[(bust_data[,1] == 15) & (bust_data[,4] == 1),2], useNA = 'ifany') # All of these are 6s!
# Only one card will result in a blackjack with any amount of points (except 11).


# Number of turns it takes to end game. # Turns = # Cards drawn
turns <- table(unlist(lapply(tests, function(x) x[[2]])))
plot(names(turns), as.vector(turns)/Nsim, main='Number of turns to end the game', type='h', xlab='# Turns', ylab='Prob')
cumsum(turns)/Nsim #CDF approximation. 
# about 50% take are under 2 turns, 
# 4% take no turns (dealt a blackjaack), 
# 3% go beyond 3 turns


# Strategy time:when should we stop: ---------------------------------------------------

blackjack_points <- function(deck, STOPPING_VAL=21){
  aceValues <- c()
  points <- 0
  turns <- 0
  deck <- sample(deck) # Shuffles deck
  cards <- deck[1:2]
  
  turns <- -1
  while(points < STOPPING_VAL){
    turns <- turns + 1
    cards <- deck[1:(2+turns)]
    nAces <- sum(is.na(cards))
    if (nAces == 0){
      points <- sum(cards)
    } else{
      nonAPoints <- sum(cards[!is.na(cards)])
      aceValues <- calc.Ace.Values(nAces, nonAPoints)
      points <- sum(aceValues) + nonAPoints
    }
  }
  #ifelse(points > 21, 0, points)
  ifelse(points > 21, 0, ifelse(points==21, 42, points))
}

est.avg.points <- function(val, d=deck, Nsim=10000) mean(sapply(1:Nsim, function(x) blackjack_points(d, val)))
cutoffs <- 9:21
cbind(cutoffs, 'Avg(Points)'=sapply(cutoffs, est.avg.points, Nsim=15000)) # Optimal wo/weight: 13


