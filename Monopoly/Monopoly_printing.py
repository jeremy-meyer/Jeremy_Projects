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


# Random Variable that defines number of spaces
def N(card=False):
    if not card:
        return np.random.choice(range(4),1, p=[.2,.4,.3,.1])[0]
    else:
        return np.random.choice(range(4), 1, p=[.5, .2, .1, .2])[0]


# Simulate dice rolls. Returns sum of dice and if it was a double
def rollDice():
    rs = np.random.choice(range(1,7) , 2, replace=True)
    return [sum(rs), rs[0] == rs[1]]


# Spaces on the board. Index corresponds to space value
SPACES = ["GO", "BRW-Medit", "CC1", "BRW-Baltic", "TAX-Income", "RR-Read", "WHT-Orient",
          "Chance1", "WHT-Verm", "WHT-Connec", "Jail", "PUR-StChar", "UTL-Elect", "PUR-States",
          "PUR-Virg", "RR-Penn", "ORG-StJames", "CC2", "ORG-Tenn", "ORG-NY", "Free-Parking",
          "RED-Kent", "Chance2", "RED-Indiana", "RED-Illi", "RR-B&O", "YEL-Atlantic",
          "YEL-Vent", "UTL-Water", "YEL-Marv", "GoToJail", "GRE-Pacific", "GRE-NC", "CC3",
          "GRE-Penn", "RR-SHLine", "Chance3", "BLU-ParkPl", "TAX-Luxury", "BLU-Boardwalk"]

CHANCE_SPACES = np.where(["Chance" in s for s in SPACES])[0]
CC_SPACES = np.where(["CC" in s for s in SPACES])[0]

CHANCE_DECK = [0, 24, 11, "Util", "RR", "NA", "JailFree", "B3", "Jail", "NA", "NA", 5,
              39, "NA", "NA", "NA"]

CC_DECK = np.concatenate(([0, "JailFree", "Jail"], np.repeat("NA", 13)))


# Find the nearest RR (round to nearest 5)
def nearestRR(space):
    return int(np.ceil((space+5)/10)*10-5)


# Nearest Utility @ space 28 and 12. ***Maybe make this more robust with arrays
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
    assert typDeck == "CHANCE" or typDeck == "CC", "ERROR: Invalid type of deck!"
    if typDeck.upper() == "CHANCE":
        basedeck = CHANCE_DECK
    elif typDeck.upper() == "CC":
        basedeck = CC_DECK

    if len(deck) == 0:  # Reset and Shuffle the Deck
        print("{} Deck is empty. Reshuffling Deck!".format(typDeck))
        deck.extend(basedeck)
    result = [np.nan, False, 0, deck]

    from numbers import Number
    card = deck[np.random.randint(0,len(deck),1)[0]]
    # print("Card Drawn: {}".format(card))
    if isinstance(card, Number):
        result[:2] = [goToSpace(curr, card), False]
        print("Card Drawn: Advance to {} (Space {})".format(SPACES[result[0] % NUM_SPACES], result[0] % NUM_SPACES))
    elif card == "Util":
        print("Card drawn: Advance to nearest Utility")
        result[0] = nearestUtil(curr)
    elif card == "RR":
        print("Card drawn: Advance to nearest Railroad")
        result[0] = nearestRR(curr)
    elif card == "B3":
        print("Card drawn: Move backward 3 spaces")
        result[0] = curr - 3
    elif card == "Jail":
        print("Card drawn: Go to Jail!")
        result[0] = goToSpace(curr, JAIL_SPACE)
        result[1] = True
    elif card == "JailFree":
        result[2] = 1
    else:
        print("Card drawn: Payment (no movement)")
    deck.remove(card)
    return result

# Explicit functions to avoid mixing them up
def drawChance(deck, curr):
    return drawDeck("CHANCE", deck, curr)


def drawCC(deck, curr):
    return drawDeck("CC", deck, curr)


# Now time to put everything together
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
    print("Starting at space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))

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
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))
                spaces = np.append(spaces, curr_space)
                # Check Space
                print("Checking Space...")
                cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                if len(cs[0]) != 0:
                    curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                spaces = np.concatenate((spaces, cs[0]))
                jailed = cs[1]
                jail_free = cs[2]
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
        print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))
        spaces = np.append(spaces, curr_space).astype(np.int64)
        # Check Space
        print("Checking Space...")
        cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
        if len(cs[0]) != 0:
            curr_space = cs[0][-1]  # Last number of the sequence becomes current space
        spaces = np.concatenate((spaces, cs[0]))
        jailed = cs[1]
        if jailed:
            return spaces
        jail_free = cs[2]

        while roll[1]:        # If you rolled a double
            roll = rollDice()
            print("Rolled a dice total of {}".format(roll[0]))
            if roll[1]:
                num_dubs += 1
                print("Double! #{}".format(num_dubs))
            if (num_dubs < 3):
                curr_space += roll[0]
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))
                spaces = np.append(spaces, curr_space).astype(np.int64)
                # Check Space
                print("Checking Space...")
                cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                if len(cs[0]) != 0:
                    curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                spaces = np.concatenate((spaces, cs[0]))
                jailed = cs[1]
                if jailed:
                    return spaces
                jail_free = cs[2]
            else:  # JAILED
                print("Crap! 3 Doubles in a row!")
                curr_space = goToSpace(curr_space, JAIL_SPACE)
                print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))
                spaces = np.append(spaces, curr_space).astype(np.int64)
                jailed = True
                print("You are now Jailed!")
                break
    return spaces


# CheckSpace function. x = current space.
# Returns additional spaces moved, if they were jailed, and # of drawn get out of jail cards
def checkSpace(x, chdeck, ccdeck, jail_free):
    # jail_free=0
    spaces = np.array([])
    space = x % NUM_SPACES
    jailed = False

    things_to_check = [space in CHANCE_SPACES, space in CC_SPACES, space == GOTO_JAIL_SPACE]
    while sum(things_to_check) > 0:
        if things_to_check[0] or things_to_check[1]:
            if things_to_check[0]:
                print("Chance! Draw chance card!")
                res = drawChance(chdeck, x)
                typ = "Chance"
                things_to_check[0] = False
            else:
                print("Community Chest! Draw community chest card!")
                res = drawCC(ccdeck, x)
                typ = "CC"
                things_to_check[1] = False
            if isinstance(res[0], int):
                x = res[0]
                spaces = np.append(spaces, x)
                print("Moved to space {} ({}): {} ".format(x % NUM_SPACES, x, SPACES[x % NUM_SPACES]))
            if res[1]:  # JAILED
                jailed = True
                print("You are now Jailed!")
            if res[2] == 1:
                jail_free += res[2]
                print("You got a get out of jail free card! You now have {} total".format(jail_free))
            chdeck = res[3]
            print("{} Deck: {} of {} cards left".format(typ, len(chdeck), len(CHANCE_DECK)))
            if res[0] is np.nan:
                return [spaces, jailed, jail_free]

        if things_to_check[2]:
            print("Ouch! Go directly to jail!")
            x = goToSpace(x, JAIL_SPACE)
            print("Moved to space {} ({}): {} ".format(x % NUM_SPACES, x, SPACES[x % NUM_SPACES]))
            spaces = np.append(spaces, x)
            jailed = True
            print("You are now Jailed!")
            return [spaces.astype(np.int64), jailed, jail_free]

        space = x % NUM_SPACES
        things_to_check = [space in CHANCE_SPACES, space in CC_SPACES, space == GOTO_JAIL_SPACE]

    if not jailed and jail_free == 0 and sum(things_to_check) == 0:
        print("Nothing to see here....")

    return [spaces.astype(np.int64), jailed, jail_free]

#turn(28+40)

def sim(nTurns, curr_space=0):
    jailed=False
    jail_free = 0
    non_dubs = 0
    num_dubs = 0
    n = N()
    spaces = np.array([curr_space])
    
    chdeck = CHANCE_DECK[:]
    ccdeck = list(CC_DECK)
    
    for turn in range(nTurns):
        print("Turn #{}: ".format(turn+1))

        if jailed:
            assert curr_space % NUM_SPACES == JAIL_SPACE, "ERROR: You must be on the jail space to be jailed"
        assert curr_space % NUM_SPACES != GOTO_JAIL_SPACE, "ERROR: You can't start on the Go to Jail space"
    
        print("You have {} get out of jail free card(s)".format(jail_free))
        # print(str(type(curr_space)) + " " + str(curr_space))
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
                    spaces = np.append(spaces, curr_space).astype(np.int64)
                    # Check Space
                    print("Checking Space...")
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    spaces = np.concatenate((spaces, cs[0]))
                    jailed = cs[1]
                    jail_free = cs[2]
                    non_dubs = 0
                    n = N()
                    if jailed:
                        print("Back in Jail!")
                    print("Next time you'll roll a max number of {} times to get out of jail".format(n))
                    print()
                    continue
                else:
                    non_dubs += 1
                    print("Still in Jail! Did not roll a double. So far, tried {} times".format(non_dubs))
    
            else:
                print("You've hit your max number of turns. Pay to get out of Jail!".format(non_dubs))
                jailed=False
                print("You are now a free citizen (out of jail)!")
                non_dubs = 0
                n = N()
                print("Next time you'll roll a max number of {} times to get out of jail".format(n))
    
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
            # Check Space
            print("Checking Space...")
            cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
            if len(cs[0]) != 0:
                curr_space = cs[0][-1]  # Last number of the sequence becomes current space
            spaces = np.concatenate((spaces, cs[0]))
            jailed = cs[1]
            if jailed:
                print()
                continue
            jail_free = cs[2]
    
            while roll[1]:        # If you rolled a double
                roll = rollDice()
                print("Rolled a dice total of {}".format(roll[0]))
                if roll[1]:
                    num_dubs += 1
                    print("Double! #{}".format(num_dubs))
                if (num_dubs < 3):
                    curr_space += roll[0]
                    print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]))
                    spaces = np.append(spaces, curr_space)
                    # Check Space
                    print("Checking Space...")
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    spaces = np.concatenate((spaces, cs[0]))
                    jailed = cs[1]
                    if jailed:
                        break
                    jail_free = cs[2]
                else:  # JAILED
                    print("Crap! 3 Doubles in a row!")
                    curr_space = goToSpace(curr_space, JAIL_SPACE)
                    print("Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]))
                    spaces = np.append(spaces, curr_space)
                    jailed = True
                    print("You are now Jailed!")
                    break
        print()
    return spaces

import sys

class SuppressPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

def sim2(nturns):
    if nturns > 100:
        with SuppressPrints():
            test = sim(nturns)
    else:
        sim(nturns)


with SuppressPrints():
    test = sim(100000)
freqs = pd.Series(test % NUM_SPACES).value_counts().sort_index()
names = pd.Series(SPACES)[freqs.index.astype(int)]
freqs.index = [str(freqs.index[x]) + " - " + names[x] for x in range(len(freqs))]
plt.hist(test % NUM_SPACES, bins=40)
print(sorted(freqs))
freqs.sort_values(ascending=False)

# Stats to consider
# Number of turns in jail
# Probability of being thrown in jail
# Number of times passing Go
# Average Movement per turn
# Number turns to hit every space

#Heat Map, loading bar