# -*- coding: utf-8 -*-
"""
Created on Wed May 23 16:47:03 2018

@author: jerem
"""
import numpy as np
import pandas as pd

uno_deck = np.concatenate([np.ones(8), np.zeros(100)])
nRuns = 10000

#Samples without replacement n cards from uno_deck
def dealHand(h):
    return(np.random.choice(uno_deck, h, replace=False))

#Deal an uno hand and sum the # of wilds. Repeat for nRuns. k is # wilds in hand. 
#Compare k to each trial and spits out T/F. True = 1, False = 0
#By averaging the 1s and 0s, we obtain the probability ( 1s + 0s) / (number of trials)
    
def prob(k):    
    return(np.mean([sum(dealHand(7)) for r in range(nRuns)] == np.repeat(k,nRuns)))
    #1 entry of value.counts() / nRuns => return(np.mean([sum(dealHand(7)) for r in range(nRuns)] == np.repeat(k,nRuns)))
    
#Map applies a function to every element in a list
#List is 0 through 7. The funciton prob is applied to each element in this list (each k).
list(map(prob, range(8))) # value.counts() / nRuns


#Note:
#type() returns the class of the object/defined varibule
#dir() Everything you can put after a period after an object/library
#help() gives you the written documentation. Also tells you what 
#       the dir() post-script functions do

#Function 1: Deck is created with deck size, # wild cards, hand size
def probs(w,n,h, nRuns = 10000):
    deck = np.concatenate([np.ones(w), np.zeros(n-w)])

    def dealHand(h):
        return(np.random.choice(deck, h, replace=False))

    def prob(k):    
        return(np.mean([sum(dealHand(h)) for r in range(nRuns)] == np.repeat(k,nRuns)))
    
    return(list(map(prob, range(h+1))))

probs(8,108,7,1000000)

#Function 2: Takes a deck vector and hand size
uno_deck = np.concatenate([np.ones(8), np.zeros(100)])
def probs2(h, deck, nRuns=10000):
    
    def dealHand(h):
        return(np.random.choice(deck, h, replace=False))

    def prob(k):    
        return(np.mean([sum(dealHand(h)) for r in range(nRuns)] == np.repeat(k,nRuns)))

#Map applies a function to every element in a list 
    return(list(map(prob, range(h + 1))))

probs2(7, uno_deck,100000)


# #NewWay

def prob3(w,n,h,nRuns = 10000):
    uno_deck = np.concatenate([np.ones(w), np.zeros(n-w)])

    def dealHand(h):
        return(np.random.choice(uno_deck, h, replace=False))
 
    return(pd.Series(np.zeros(w)) + pd.Series([sum(dealHand(h)) for r in range(nRuns)]) \
            .value_counts() / nRuns )
    #pd.Series([14,14,15,19,14,15]).value_counts() / 6 This is value_counts()
    #This tabulates (makes a table) the frequency for each value of k
        
prob3(8,108,7, 100000)

def prob4(w,n,h,nRuns=10000):
    return(pd.Series(np.zeros(w)) + pd.Series([sum(np.random.choice(np.concatenate([np.ones(w), np \
        .zeros(n-w)]), h, replace=False)) for r in range(nRuns)]).value_counts() / nRuns)

prob4(8,108,7, 1000000)

# #Challenge Accepted
pd.Series(np.zeros(8)) + pd.Series([sum(np.random.choice(np.concatenate([np.ones(8), np \
    .zeros(100)]), 7, replace=False)) for r in range(1000000)]).value_counts() / 10000

#Old Code
import numpy as np
import pandas as pd

uno_deck = np.concatenate([np.ones(8), np.zeros(100)])
nRuns = 100000

#Samples without replacement n cards from uno_deck
def dealHand(h):
    return(np.random.choice(uno_deck, h, replace=False))

def prob(k):    
    return(np.mean([sum(dealHand(7)) for r in range(nRuns)] == np.repeat(k,nRuns)))

#Map applies a function to every element in a list 
list(map(prob, range(8)))

import scipy.stats as scps

rv = scps.hypergeom(8, 7, 108)
x = np.arange(0, 7+1)
pmf_dogs = rv.pmf(x)

import scipy.stats


#Probs: 19.46035 #Creates everything
#Probs2: 18.81744 #Deck Vector
#Prob3: 2.47752 #New Way
#Prob4: 3.812 #Because it re-cereates the dealHand function

import time
start_time = time.time()
def main(): #Defining main()
    prob4(8,108,7, 100000) #Testing code
main() #Calling main()
print("--- %s seconds ---" % (time.time() - start_time))