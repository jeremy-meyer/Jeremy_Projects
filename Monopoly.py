# -*- coding: utf-8 -*-
"""
Created on Sat May 19 14:07:08 2018

@author: jerem
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import functools as ft

NUM_SPACES = 40
JAIL_SPACE = 10
GOTO_JAIL_SPACE = 30

#Random Variable that defines number of spaces 
def N():
    return np.random.choice(range(4),1, p=[.2,.4,.3,.1])[0]

#Use that to generate game board movement
#Take into account chance/community chest cards

#Simulate dice rolls. Returns sum of dice and if it was a double
def rollDice():
    rs = np.random.choice(range(1,7) , 2, replace=True)
    return([sum(rs), rs[0] == rs[1]])
rollDice()

#1000 rolls Using List comprehhensions
rolls = [rollDice()[0] for r in range(1000)]
counts = pd.Series(rolls).value_counts().sort_index(0).to_frame()

plt.hist(counts)
counts.index
plt.bar(counts.index, counts[0])

#Runs 1 "turn". Returns rolls of spaces + number doubles
#If 3 doubles are rolled in a row, they do not move the third time.
def diceSim():
    spaces_moved = np.array([])
    num_dubs = 0
    
    while True:
        roll = rollDice()
        if (roll[1]):
            num_dubs += 1
            if (num_dubs != 3):
                spaces_moved = np.append(spaces_moved, roll[0])
            else: break
        else:
            spaces_moved = np.append(spaces_moved, roll[0])
            break
    
    return(np.array([spaces_moved, num_dubs]))

diceSim()
def simTurns(n):
    return([diceSim() for x in range(n)])

sims = simTurns(10000)
num_dubs = np.array([sims[x][1] for x in range(len(sims))])

#Compare. Going to jail isn't very frequent from dice rolls alone
plt.hist(num_dubs)
plt.show()
np.mean(num_dubs == 3)
1/6**3

#Rolls for those that went to jail
[sims[i][0] for i in np.where(num_dubs == 3)[0]]
[sims[i][0] for i in np.where(num_dubs == 2)[0]][:20] #Those with 2 doubles move 3 times

#Game Board Movement
#Take Cumulative sum of each row
all_rolls = np.concatenate([sims[i][0] for i in range(len(sims))])
cumSum = all_rolls
for i in range(1, len(cumSum)):
    cumSum[i] += cumSum[i-1]

plt.hist(cumSum % NUM_SPACES)
space_freqs = pd.Series(cumSum % NUM_SPACES).value_counts().sort_index(0)
space_freqs #Looks uniform

#Fix: Going to jail on 3rd double or landing on jail space. Jail = 10 spot. 
#Assume we always move ahead
def goToJail(ind): #Returns overall space after moving to jail from current index
    return(np.ceil((ind - JAIL_SPACE) / NUM_SPACES)*NUM_SPACES + JAIL_SPACE)

#Problem: Once they are in jail, they have to roll doubles to get out
#For now, I'll just program it so they go to the jail space and assume they pay right away to get out
#I'm going to have to cumulate spaces in this for loop
nRuns = 50000
turns = simTurns(nRuns)

def simPayOutOfJail(simst): #Assume you pay to get out of jail immeateately. 
    rolls2 = np.array([0]) #Start at GO
    for turn in range(len(simst)):
        cumList = np.concatenate(([rolls2[-1]], simst[turn][0])) #Contains previous space # + new ones
        for r in range(1, len(cumList)): #Accumulates space # from rolls
            cumList[r] += cumList[r-1]
        if(simst[turn][1] == 3): #If three triples are thrown, add the jail space after last roll
            cumList = np.concatenate((cumList, [goToJail(cumList[-1])]))
        rolls2 = np.concatenate((rolls2, cumList[1:])) #Put everything together, but don't include previous space twice
    return(rolls2)

sim1 = simPayOutOfJail(turns) % NUM_SPACES
pd.Series(sim1).value_counts().sort_index(0)

plt.hist(simPayOutOfJail(sims) % NUM_SPACES)
plt.show()

#If every space were uniform, this is the expected # movements per game
(5/6*1+5/36*2+1/36*3)*nRuns #119444
#np.sum(pd.Series(sim1).value_counts().sort_index(0)) #119616
np.mean(pd.Series(sim1).value_counts().sort_index(0)) #2990

l = [np.sum(pd.Series(simPayOutOfJail(simTurns(nRuns)) % NUM_SPACES).value_counts().sort_index(0))/nRuns for i in range(100)]

#Idea: Make it so the number of turns to pay for jail has probabilities. 
#First program it to try once to get out of jail, and then pay

#n is the maximum number of times you will roll to get out of jail
def RollOutOfJail(n):
    non_dubs = 0
    while non_dubs < n:
        roll = rollDice()
        if (roll[1]):
            roll[1] = False
            return(roll)
        non_dubs += 1
    return(rollDice())

plt.hist([RollOutOfJail(2)[0] for i in range(10000)],  bins=11)
#Looks good

# n = 2, dice frequencies
pd.Series([RollOutOfJail(2)[0] for i in range(10000)]).value_counts().sort_index(0)

#Theoretical mean of doubles
1-(5/6)*(5/6)*(5/6)

#n is a random variabule. w/graph
np.random.choice(range(3),1, p=[.2,.4,.3,.1]) 
plt.hist([np.random.choice(range(4),1, p=[.2,.4,.3,.1])[0] for i in range(10000)])

#Histogram of spaces moved after being jailed
plt.hist([RollOutOfJail(np.random.choice(range(4),1, p=[.2,.4,.3,.1])[0])[0] for i in range(10000)], bins=11)

#Proportion of rolls out of jail that are doubles. 
np.mean([RollOutOfJail(np.random.choice(range(4),1, p=[.2,.4,.3,.1])[0])[1] for i in range(10000)])

#Next: Spaces on board / Cards
#Spaces on the board. Index corresponds to space value
SPACES = ["GO", "BRW-Medit", "CC1", "BRW-Baltic", "TAX-Income", "RR-Read", "WHT-Orient",
          "Chance1", "WHT-Verm", "WHT-Connec", "Jail", "PUR-StChar", "UTL-Elect", "PUR-States",
          "PUR-Virg", "RR-Penn", "ORG-StJames", "CC2", "ORG-Tenn", "ORG-NY", "Free-Parking",
          "RED-Kent", "Chance2", "RED-Indiana", "RED-Illi", "RR-B&O", "YEL-Atlantic",
          "YEL-Vent", "UTL-Water", "YEL-Marv", "GoToJail", "GRE-Pacific", "GRE-NC", "CC3",
          "GRE-Penn", "RR-SHLine", "Chance3", "BLU-ParkPl", "TAX-Luxury", "BLU-Boardwalk"]
CHANCE_SPACES = np.where(["Chance" in s for s in SPACES])[0]
CC_SPACES = np.where(["CC" in s for s in SPACES])[0]

for i in range(NUM_SPACES): print(str(i) + " " + SPACES[i])     
  
CHANCE_DECK = [0, 24, 11, "Util", "RR", "NA", "JailFree", "B3", JAIL_SPACE, "NA", "NA", 5, 
              39, "NA", "NA", "NA"]
   
CC_DECK = np.concatenate(([0, "JailFree", JAIL_SPACE] , np.repeat("NA", 13)))


# Find the nearest RR (round to nearest 5)
def nearestRR(space):
    return(np.ceil((space+5)/10)*10-5)

#Nearest Utility @ space 28 and 12. ***Maybe make this more robust with arrays
def nearestUtil(space):
    rounds = np.floor(space / NUM_SPACES)
    sp = space % NUM_SPACES
    if (sp > 12 and sp <= 28):
        return(28 + rounds*NUM_SPACES)
    elif (sp >28):
        return(12+(rounds+1)*NUM_SPACES)
    else:
        return(12 + rounds*NUM_SPACES)

# Returns final location after moving from current spot to a particular space
def goToSpace(curr, space):
    return(int(np.ceil((curr - space) / NUM_SPACES)*NUM_SPACES + space))

# Returns the resulting movement after drawing a chance card, 
# if they are jailed, if they got a jail-free card and the drawn deck
def drawDeck(typDeck, deck, curr):
    if len(deck) == 0:  #Reset and Shuffle the Deck
        deck.extend(typDeck)
    result = [np.nan, False, 0, deck]
    
    from numbers import Number
    card = deck[np.random.randint(0,len(deck),1)[0]]
    print("Card Drawn: {}".format(card))
    if isinstance(card, Number):
        result[:2] = [goToSpace(curr, card), card == JAIL_SPACE]
    elif card == "Util":
        result[0] = nearestUtil(curr)
    elif card == "RR":
        result[0] = nearestRR(curr)
    elif card == "B3":
        result[0] = curr - 3
    elif card == "JailFree":
        result[2] = 1
    deck.remove(card)
    return result

#Explicit functions to avoid mixing them up
def drawChance(deck, curr):
    return drawDeck(CHANCE_DECK, deck, curr)

def drawCC(deck, curr):
    return drawDeck(CC_DECK, deck, curr)



#Now time to put everything together
chdeck = CHANCE_DECK[:] 
ccdeck = list(CC_DECK)
jail_free = 0
spaces = np.array([0])
num_dubs = 0
curr_space = 0
jailed = False

def turn(curr_space, jailed=False):
    spaces = np.array([curr_space])
    print("Starting at space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
    if jailed:
        #Roll out of jail
        print("Rolled out of Jail")
        jailed=False
    else:
        num_dubs = 0
        roll = rollDice()
        print("Rolled a dice total of {}".format(roll[0]))
        if roll[1]:
            num_dubs = 1
            print("Double! Total: {}".format(num_dubs))
        curr_space += roll[0]
        print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
        spaces = np.append(spaces, curr_space)
        #Check Space
        print("Checking Space...")
        while roll[1]:        #If you rolled a double
            roll = rollDice()
            print("Rolled a dice total of {}".format(roll[0]))
            if roll[1]:
                num_dubs += 1
                print("Double! Total: {}".format(num_dubs))
            if (num_dubs < 3):  
                curr_space += roll[0]
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
                spaces = np.append(spaces, curr_space)
                #Check Space
                print("Checking Space...")
            else: #JAILED
                print("Crap! 3 Doubles in a row!")
                curr_space = goToSpace(curr_space, JAIL_SPACE)
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
                spaces = np.append(spaces, curr_space)
                jailed = True
                print("You are now Jailed!")
                break
    return spaces


np.array([spaces, num_dubs])


# CheckSpace function. x = current space
def checkSpace(x):
    space = x % NUM_SPACES
    if space in CHANCE_SPACES:
        res = drawChance(chdeck, x)
        if res[0] != np.nan:    
            spaces = np.append(spaces, res[0])
            space = res[0]
        if res[1]:
            print("Jailed")
            # GO TO JAIL
        jail_free += res[2]
        chdeck = res[3]
    elif space in CC_SPACES:
        res = drawCC(ccdeck, x)
        if res[0] != np.nan: 
            spaces = np.append(spaces, res[0])
            space = res[0]
        if res[1]:
            print("Jailed")
            # GO TO JAIL
        jail_free += res[2]
        ccdeck = res[3]
    if space == GOTO_JAIL_SPACE:
        print("Jailed")
        # GO TO JAIL


        
#        roll = rollDice() 
#        if (roll[1]):  #If you roll a double
#            num_dubs += 1
#            if (num_dubs < 3):
#                curr_space += roll[0]
#                spaces = np.append(spaces, curr_space)
#                #Check space



#Going to jail
#Rolling three doubles
#Landing on space 30
#Drawing a chance/CC
