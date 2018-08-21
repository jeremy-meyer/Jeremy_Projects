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

def N_Card():
    return np.random.choice(range(4),1, p=[.5,.2,.1,.2])[0]

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
  
CHANCE_DECK = [0, 24, 11, "Util", "RR", "NA", "JailFree", "B3", "Jail", "NA", "NA", 5,
              39, "NA", "NA", "NA"]
   
CC_DECK = np.concatenate(([0, "JailFree", "Jail"] , np.repeat("NA", 13)))


# Find the nearest RR (round to nearest 5)
def nearestRR(space):
    return int(np.ceil((space+5)/10)*10-5)

#Nearest Utility @ space 28 and 12. ***Maybe make this more robust with arrays
def nearestUtil(space):
    rounds = np.floor(space / NUM_SPACES)
    sp = space % NUM_SPACES
    if (sp > 12 and sp <= 28):
        return int(28 + rounds*NUM_SPACES)
    elif (sp >28):
        return int(12+(rounds+1)*NUM_SPACES)
    else:
        return int(12 + rounds*NUM_SPACES)

# Returns final location after moving from current spot to a particular space
def goToSpace(curr, space):
    return int(np.ceil((curr - space) / NUM_SPACES)*NUM_SPACES + space)

# Returns the resulting movement after drawing a chance card, 
# if they are jailed, if they got a jail-free card and the drawn deck
def drawDeck(typDeck, deck, curr):
    if len(deck) == 0:  #Reset and Shuffle the Deck
        deck.extend(typDeck)
    result = [np.nan, False, 0, deck]
    
    from numbers import Number
    card = deck[np.random.randint(0,len(deck),1)[0]]
    # print("Card Drawn: {}".format(card))
    if isinstance(card, Number):
        result[:2] = [goToSpace(curr, card), False]
        print("Card Drawn: Move to {}: space {}".format(SPACES[result[0]], result[0]))
    elif card == "Util":
        print("Card drawn: Move to nearest Utility")
        result[0] = nearestUtil(curr)
    elif card == "RR":
        print("Card drawn: Move to nearest Railroad")
        result[0] = nearestRR(curr)
    elif card == "B3":
        print("Card drawn: Move backward 3 spaces")
        result[0] = curr - 3
    elif card == "JailFree":
        result[2] = 1
    elif card == "Jail":
        print("Card drawn: Go to Jail!! ")
        result[1] = True
    elif card == np.nan:
        print("Card drawn: Payment (no movement)")
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
non_dubs = 0
n = N()
curr_space = 0
jailed = False

def turn(curr_space, jailed=False, jail_free=0, non_dubs=0, n=N()):
    if jailed:
        assert curr_space % NUM_SPACES == JAIL_SPACE, "ERROR: You must be on the jail space to be jailed"
    assert curr_space % NUM_SPACES != GOTO_JAIL_SPACE, "ERROR: You can't start on the Go to Jail space"

    spaces = np.array([curr_space])
    print("You have {} get out of jail free card(s)".format(jail_free))
    print("Starting at space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
    
    if jail_free > 0 and jailed:
        print("You are Jailed!")
        jail_free -= 1
        print("You used a get out of Jail Free card! {} jail-free cards left".format(jail_free))
        print("You are out of Jail!")
        jailed = False
        
    if jailed:
        # Roll out of jail
        print("You are Jailed!")
        print("You've rolled {} out of a max of {} rolls before you'll pay.".format(non_dubs, n))
        if non_dubs < n:
            roll = rollDice()
            if roll[1]:
                print("You got out of jail! You rolled a double! Move {} spaces".format(roll[0]))
                jailed = False
                curr_space += roll[0]
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
                spaces = np.append(spaces, curr_space)
                # Check Space
                print("Checking Space...")
                non_dubs = 0
                n = N()
                print("Next time you'll roll a max number of {} times to get out of jail".format(n))
                return spaces   # End Turn
            else:
                non_dubs += 1
                print("Still in Jail! Did not roll a double. So far, tried {} times".format(non_dubs))
                
        else:
            print("You've hit your max number of turns. Pay to get out of Jail!".format(non_dubs))
            jailed=False
            print("You are now a free citizen (out of jail)!")
            
            
    if not jailed:
        num_dubs = 0
        roll = rollDice()
        print("Rolled a dice total of {}".format(roll[0]))
        if roll[1]:
            num_dubs = 1
            print("Double! #{}".format(num_dubs))
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
                print("Double! #{}".format(num_dubs))
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

# Checking resonableness of getting out of jail
ls = np.array([len(turn(50, True, 1,2)) for x in range(1000)])
np.mean(ls > 1)


# CheckSpace function. x = current space. 
# Returns additional spaces moved, if they were jailed, and # of drawn get out of jail cards
def checkSpace(x):
    jail_free = 0
    spaces = np.array([])
    space = x % NUM_SPACES
    jailed = False
    chdeck = CHANCE_DECK[:]
    ccdeck = list(CC_DECK)

    things_to_check = [space in CHANCE_SPACES, space in CC_SPACES, space == GOTO_JAIL_SPACE]

    if things_to_check[0]:
        print("Chance! Draw chance card!")
        res = drawChance(chdeck, x)
        if isinstance(res[0], int):
            # print("Card Drawn: Move to {}: space {}".format(SPACES[res[0]], res[0]))
            x = goToSpace(x, res[0])
            spaces = np.append(spaces, x)
            print("Moved to space {} ({}): {} ".format(x % NUM_SPACES, x, SPACES[x % NUM_SPACES]))
        # elif res[0] == np.nan:
            # print("Card drawn: Payment (no movement)")
        if res[1]:  # JAILED
            # print("You drew: Go to Jail!")
            curr_space = goToSpace(x, JAIL_SPACE)
            print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
            spaces = np.append(spaces, x)
            jailed = True
            print("You are now Jailed!")
        if res[2] == 1:
            jail_free += res[2]
            print("You got a get out of jail free card! You now have {} total".format(jail_free))
        chdeck = res[3]
        print("Deck: {} of {} cards left".format(len(chdeck), len(CHANCE_DECK)))

    if things_to_check[1]:
        res = drawCC(ccdeck, x)
        if res[0] != np.nan: 
            spaces = np.append(spaces, res[0])
            space = res[0]
        if res[1]:
            print("Jailed")
            # GO TO JAIL
        jail_free += res[2]
        ccdeck = res[3]
    if things_to_check[2]:
        print("Jailed")
        # GO TO JAIL
    if sum(things_to_check) == 0:
        print("Nothing to see here....")
    return [spaces, jailed, jail_free]

[str(r) + " " + str(isinstance(r, int)) for r in CHANCE_DECK]
        
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
