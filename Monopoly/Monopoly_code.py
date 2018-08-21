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
SPACES = ["GO", "BRW-Medit", "CC1", "BRW-Baltic", "TAX_Income", "RR-Read", "WHT-Orient",
          "Chance1", "WHT-Verm", "WHT-Connec", "Jail", "PUR-StChar", "UTL-Elect", "PUR-States",
          "PUR-Virg", "RR-Penn", "ORG-StJames", "CC2", "ORG-Tenn", "ORG-NY", "Free_Parking",
          "RED-Kent", "Chance2", "RED-Indiana", "RED-Illi", "RR-B&O", "YEL-Atlantic",
          "YEL-Vent", "UTL-Water", "YEL-Marv", "GoToJail", "GRE-Pacific", "GRE-NC", "CC3",
          "GRE-Penn", "RR-SHLine", "Chance3", "BLU-ParkPl", "TAX_Luxury", "BLU-Boardwalk"]

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
    s = ""
    if len(deck) == 0:  # Reset and Shuffle the Deck
        s += "{} Deck is empty. Reshuffling Deck!".format(typDeck) + "\n"
        deck.extend(basedeck)
    result = [np.nan, False, 0, deck]

    from numbers import Number
    card = deck[np.random.randint(0,len(deck),1)[0]]
    # print("Card Drawn: {}".format(card))
    if isinstance(card, Number):
        result[:2] = [goToSpace(curr, card), False]
        s += "Card Drawn: Advance to {} (Space {})".format(SPACES[result[0] % NUM_SPACES], result[0] % NUM_SPACES) + "\n"
    elif card == "Util":
        s += "Card drawn: Advance to nearest Utility" + "\n"
        result[0] = nearestUtil(curr)
    elif card == "RR":
        s += "Card drawn: Advance to nearest Railroad" + "\n"
        result[0] = nearestRR(curr)
    elif card == "B3":
        s += "Card drawn: Move backward 3 spaces" + "\n"
        result[0] = curr - 3
    elif card == "Jail":
        s += "Card drawn: Go to Jail!" + "\n"
        result[0] = goToSpace(curr, JAIL_SPACE)
        result[1] = True
    elif card == "JailFree":
        result[2] = 1
    else:
        s += "Card drawn: Payment (no movement)" + "\n"
    deck.remove(card)
    return result, s

# Explicit functions to avoid mixing them up
def drawChance(deck, curr):
    return drawDeck("CHANCE", deck, curr)


def drawCC(deck, curr):
    return drawDeck("CC", deck, curr)


# Now time to put everything together
chdeck = CHANCE_DECK[:]
ccdeck = list(CC_DECK)

# CheckSpace function. x = current space.
# Returns additional spaces moved, if they were jailed, and # of drawn get out of jail cards
def checkSpace(x, chdeck, ccdeck, jail_free):
    spaces = np.array([])
    space = x % NUM_SPACES
    jailed = False
    s = ""

    things_to_check = [space in CHANCE_SPACES, space in CC_SPACES, space == GOTO_JAIL_SPACE]
    while sum(things_to_check) > 0:
        if things_to_check[0] or things_to_check[1]:
            if things_to_check[0]:
                s += "Chance! Draw chance card!" + "\n"
                res, r = drawChance(chdeck, x)
                s += r
                typ = "Chance"
                things_to_check[0] = False
            else:
                s += "Community Chest! Draw community chest card!" + "\n"
                res, r = drawCC(ccdeck, x)
                s += r
                typ = "CC"
                things_to_check[1] = False
            if isinstance(res[0], int):
                x = res[0]
                spaces = np.append(spaces, x)
                s += "Moved to space {} ({}): {} ".format(x % NUM_SPACES, x, SPACES[x % NUM_SPACES]) + "\n"
            if res[1]:  # JAILED
                jailed = True
                s += "You are now Jailed!" + "\n"
            if res[2] == 1:
                jail_free += res[2]
                s += "You got a get out of jail free card! You now have {} total".format(jail_free) + "\n"
            chdeck = res[3]
            s += "{} Deck: {} of {} cards left".format(typ, len(chdeck), len(CHANCE_DECK))+ "\n"
            if res[0] is np.nan:
                return [spaces, jailed, jail_free, s]

        if things_to_check[2]:
            s += "Ouch! Go directly to jail!" + "\n"
            x = goToSpace(x, JAIL_SPACE)
            s += "Moved to space {} ({}): {} ".format(x % NUM_SPACES, x, SPACES[x % NUM_SPACES]) + "\n"
            spaces = np.append(spaces, x)
            jailed = True
            s += "You are now Jailed!" + "\n"
            return [spaces.astype(np.int64), jailed, jail_free, s]

        space = x % NUM_SPACES
        things_to_check = [space in CHANCE_SPACES, space in CC_SPACES, space == GOTO_JAIL_SPACE]

    if not jailed and jail_free == 0 and sum(things_to_check) == 0:
        s += "Nothing to see here...." + "\n"

    return [spaces.astype(np.int64), jailed, jail_free, s]


def sim(nTurns, curr_space=0, jailed=False):
    jail_free = 0
    non_dubs = 0
    num_dubs = 0
    n = N()
    spaces = np.array([curr_space])
    recs = []

    movement = np.array([])
    jailed_turns = 0
    still_jailed = 0
    paid_jailed = 0
    dubs_jailed = 0
    jailfree_jailed = 0
    back_in_jail = []
    jailed_spaces = []
    jailed_spaces_curr = []
    go_skips = 0

    chdeck = CHANCE_DECK[:]
    ccdeck = list(CC_DECK)
    
    for turn in range(nTurns):
        s = ""
        s += "Turn #{}: ".format(turn+1) + "\n"
        start_space = curr_space
        got_outjail = False
        if jailed:
            assert curr_space % NUM_SPACES == JAIL_SPACE, "ERROR: You must be on the jail space to be jailed"
        assert curr_space % NUM_SPACES != GOTO_JAIL_SPACE, "ERROR: You can't start on the Go to Jail space"
    
        s += "You have {} get out of jail free card(s)".format(jail_free) + "\n"
        # print(str(type(curr_space)) + " " + str(curr_space))
        s += "Starting at space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]) + "\n"
    
        if jail_free > 0 and jailed:
            s += "You are Jailed!" + "\n"
            jailed_turns += 1
            jail_free -= 1
            s += "You used a get out of Jail Free card! {} jail-free cards left".format(jail_free) + "\n"
            s += "You are out of Jail!" + "\n"
            got_outjail = True
            jailfree_jailed += 1
            jailed = False
    
        if jailed:
            # Roll out of jail
            s += "You are Jailed!" + "\n"
            s += "You've rolled {} out of a max of {} rolls before you'll pay.".format(non_dubs, n) + "\n"
            jailed_turns += 1
            if non_dubs < n:
                roll = rollDice()
                if roll[1]:
                    s += "You got out of jail! You rolled a double! Move {} spaces".format(roll[0]) + "\n"
                    got_outjail = True
                    jailed = False
                    dubs_jailed += 1
                    curr_space += roll[0]
                    s += "Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]) + "\n"
                    spaces = np.append(spaces, curr_space).astype(np.int64)
                    # Check Space
                    s += "Checking Space..." + "\n"
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    spaces = np.concatenate((spaces, cs[0]))
                    jailed = cs[1]
                    jail_free = cs[2]
                    non_dubs = 0
                    n = N()
                    s += cs[3]
                    if jailed:
                        back_in_jail.append(turn)
                        s += "Back in Jail!" + "\n"
                        jailed_spaces.append(start_space)
                        jailed_spaces_curr.append(spaces[-2])
                        if spaces[-2] % NUM_SPACES > JAIL_SPACE:
                            go_skips += 1
                            s += "Skipped Go!" + "\n"
                    s += "Next time you'll roll a max number of {} times to get out of jail".format(n) + "\n\n"
                    recs.append(s)
                    movement = np.append(movement, curr_space - start_space)
                    continue
                else:
                    non_dubs += 1
                    still_jailed += 1
                    s += "Still in Jail! Did not roll a double. So far, tried {} times".format(non_dubs) + "\n"
    
            else:
                s += "You've hit your max number of turns. Pay to get out of Jail!".format(non_dubs) + "\n"
                jailed=False
                paid_jailed += 1
                s += "You are now a free citizen (out of jail)!" + "\n"
                got_outjail = True
                non_dubs = 0
                n = N()
                s += "Next time you'll roll a max number of {} times to get out of jail".format(n) + "\n"
    
        if not jailed:
            num_dubs = 0
            roll = rollDice()
            s += "Rolled a dice total of {}".format(roll[0]) + "\n"
            if roll[1]:
                num_dubs = 1
                s += "Double! #{}".format(num_dubs) + "\n"
            curr_space += roll[0]
            s += "Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]) + "\n"
            spaces = np.append(spaces, curr_space)
            # Check Space
            s += "Checking Space..." + "\n"
            cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
            if len(cs[0]) != 0:
                curr_space = cs[0][-1]  # Last number of the sequence becomes current space
            spaces = np.concatenate((spaces, cs[0]))
            jailed = cs[1]
            s += cs[3]
            if jailed:
                if got_outjail:
                    s += "Back in Jail!" + "\n"
                    back_in_jail.append(turn)
                if spaces[-2] % NUM_SPACES > JAIL_SPACE:
                    go_skips += 1
                    s += "Skipped Go!" + "\n"
                jailed_spaces.append(start_space)
                jailed_spaces_curr.append(spaces[-2])
                movement = np.append(movement, curr_space - start_space)
                s += "\n"
                recs.append(s)
                continue
            jail_free = cs[2]
    
            while roll[1]:        # If you rolled a double
                roll = rollDice()
                s += "Rolled a dice total of {}".format(roll[0]) + "\n"
                if roll[1]:
                    num_dubs += 1
                    s += "Double! #{}".format(num_dubs) + "\n"
                if (num_dubs < 3):
                    curr_space += roll[0]
                    s += "Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[curr_space % NUM_SPACES]) + "\n"
                    spaces = np.append(spaces, curr_space)
                    # Check Space
                    s += "Checking Space..." + "\n"
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    spaces = np.concatenate((spaces, cs[0]))
                    s += cs[3]
                    jailed = cs[1]
                    if jailed:
                        if got_outjail:
                            s += "Back in Jail!" + "\n"
                            back_in_jail.append(turn)
                        if spaces[-2] % NUM_SPACES > JAIL_SPACE:
                            go_skips += 1
                            s += "Skipped Go!" + "\n"
                        jailed_spaces.append(start_space)
                        jailed_spaces_curr.append(spaces[-2])
                        break
                    jail_free = cs[2]
                else:  # JAILED
                    s += "Crap! 3 Doubles in a row!" + "\n"
                    curr_space = goToSpace(curr_space, JAIL_SPACE)
                    s += "Moved to space {} ({}): {} ".format(curr_space % NUM_SPACES, curr_space, SPACES[int(curr_space % NUM_SPACES)]) + "\n"
                    spaces = np.append(spaces, curr_space)
                    jailed = True
                    if spaces[-2] % NUM_SPACES > JAIL_SPACE:
                        go_skips += 1
                        s += "Skipped Go!" + "\n"
                    s += "You are now Jailed!" + "\n"
                    if got_outjail:
                        s += "Back in Jail!" + "\n"
                        back_in_jail.append(turn)
                    jailed_spaces.append(start_space)
                    jailed_spaces_curr.append(spaces[-2])
                    break
        movement = np.append(movement, curr_space - start_space)
        recs.append(s)

    # Jail Statistics. Check to make sure we don't divide by zero
    if jailed_turns == 0:
        jail1stats = [0]*4
    else:
        jail1stats = np.array([still_jailed, paid_jailed, dubs_jailed, jailfree_jailed]) / jailed_turns
    if jailed_turns-still_jailed == 0:
        jail2stat = [0]
    else:
        jail2stat = [len(back_in_jail)/(jailed_turns-still_jailed)]
    jail_stat = np.concatenate(([jailed_turns/nTurns], jail1stats, jail2stat))

    collect_go = int(spaces[-1] // NUM_SPACES - go_skips)
    collect_go = [collect_go, nTurns / collect_go]

    return [spaces, movement, jail_stat, np.array([jailed_spaces, jailed_spaces_curr]), recs, back_in_jail, collect_go]

nturns = 30000

test = sim(nturns)
# t[0] Spaces landed on
# t[1] Movements each turn
# t[2] Jail statistics
# t[3] Spaces before going to jail (t[3][0] starting, t[3][1] ending)
# t[4] String result of each turn for debugging

freqs = pd.Series(test[0] % NUM_SPACES).value_counts().sort_index()
names = pd.Series(SPACES)[freqs.index.astype(int)]
freqs.index = [str(freqs.index[x]) + " - " + names[x] for x in range(len(freqs))]
plt.hist(test[0] % NUM_SPACES, bins=40)
plt.show()
print(sorted(freqs))
freqs.sort_values(ascending=False) / nturns *100

# Average Movement per turn
print(np.mean(test[1]))
print(np.mean(test[1] > 40))    # Proportion that make over a full circle.
print(max(test[1]))  # Furthest moved around board
print(test[4][np.argmax(test[1])])  # What turn that was
pd.Series(test[1]).value_counts().sort_index(0)
plt.hist(test[1], bins=int(max(test[1]))+1)
plt.show()

# Jail Statistics. Strongly dependent on N() where p=.2,.4,.3,.1
print("Proportion of turns in jail: %.4f" % test[2][0])
print("Prob(Staying in Jail):       %.4f" % test[2][1])  # All conditional on being in jail. Investigate this stat
print("Prob(Paying to get out):     %.4f" % test[2][2])
print("Prob(Escaping by doubles):   %.4f" % test[2][3])
print("Prob(Use jail-free card):    %.4f" % test[2][4])
print("Prob(Thrown back into jail): %.4f" % test[2][5])  # Given in jail, chance of getting out and getting jailed again
# Turns of those unfortunate enough to land back in jail:
for x in test[5]:
    print(test[4][x])

# Based on given starting space, what's the probability of going to jail by end of turn? Look at meaningful metrics
# Out of all the times you've been on this space, here are the % that have gone to jail
s = pd.Series(test[3][0] % NUM_SPACES).value_counts()
s = s.append(pd.Series(0, index={GOTO_JAIL_SPACE})).sort_index(0)
s / (test[2][0]*nturns)
plt.hist(test[3][0] % NUM_SPACES, bins=NUM_SPACES)
plt.show()
plt.bar(np.arange(NUM_SPACES), s / freqs.values * 100)
plt.show()

# Based on last space before being sent to jail
sl = pd.Series(test[3][1] % NUM_SPACES).value_counts()
sl = sl.append(pd.Series(0, index={JAIL_SPACE})) / (test[2][0]*nturns)
plt.hist(test[3][1] % NUM_SPACES, bins=NUM_SPACES)
plt.show()

# Number of times passing go:
print("Collected Go Money: {} times".format(test[6][0]))
print("number of turns to passing Go ratio: %.3f" % (test[6][1]))

# Number turns to hit every property
# All properties have a "-" sign in them
properties = np.where([x.find('-') != -1 for x in SPACES])[0]

def updateList(targ_matrix, newsp, turn):
    for x in newsp:
        try:
            col_ind = np.where(targ_matrix[0] == x)[0][0]
            if targ_matrix[1, col_ind] == -1:
                targ_matrix[1, col_ind] = turn
        except IndexError:
            pass
    return targ_matrix

# Does not include starting space
def hit_all_spaces(targets, curr_space=0):
    jailed = False
    jail_free = 0
    non_dubs = 0
    num_dubs = 0
    n = N()
    # all_spaces = []

    turn = 1
    chdeck = CHANCE_DECK[:]
    ccdeck = list(CC_DECK)
    targ_matrix = np.vstack((targets, np.repeat(-1, len(targets))))

    while -1 in targ_matrix[1]:
        turn_spaces = []
        if jailed:
            assert curr_space % NUM_SPACES == JAIL_SPACE, "ERROR: You must be on the jail space to be jailed"
        assert curr_space % NUM_SPACES != GOTO_JAIL_SPACE, "ERROR: You can't start on the Go to Jail space"

        if jail_free > 0 and jailed:
            jail_free -= 1
            jailed = False

        if jailed:
            if non_dubs < n:
                roll = rollDice()
                if roll[1]:
                    jailed = False
                    curr_space += roll[0]
                    turn_spaces.append(curr_space)
                    # Check Space
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    turn_spaces.extend(cs[0])
                    jailed = cs[1]
                    jail_free = cs[2]
                    non_dubs = 0
                    n = N()
                    updateList(targ_matrix, np.array(turn_spaces) % NUM_SPACES, turn)
                    # all_spaces.append(turn_spaces)
                    turn += 1
                    continue
                else:
                    non_dubs += 1
            else:
                jailed = False
                non_dubs = 0
                n = N()

        if not jailed:
            num_dubs = 0
            roll = rollDice()
            if roll[1]:
                num_dubs = 1
            curr_space += roll[0]
            turn_spaces.append(curr_space)
            cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
            if len(cs[0]) != 0:
                curr_space = cs[0][-1]  # Last number of the sequence becomes current space
            turn_spaces.extend(cs[0])
            jailed = cs[1]
            if jailed:
                updateList(targ_matrix, np.array(turn_spaces) % NUM_SPACES, turn)
                # all_spaces.append(turn_spaces)
                turn += 1
                continue
            jail_free = cs[2]

            while roll[1]:  # If you rolled a double
                roll = rollDice()
                if roll[1]:
                    num_dubs += 1
                if (num_dubs < 3):
                    curr_space += roll[0]
                    turn_spaces.append(curr_space)
                    # Check Space
                    cs = checkSpace(curr_space, chdeck, ccdeck, jail_free)
                    if len(cs[0]) != 0:
                        curr_space = cs[0][-1]  # Last number of the sequence becomes current space
                    turn_spaces.extend(cs[0])
                    jailed = cs[1]
                    if jailed:
                        break
                    jail_free = cs[2]
                else:  # JAILED
                    curr_space = goToSpace(curr_space, JAIL_SPACE)
                    turn_spaces.append(curr_space)
                    jailed = True
                    break
        updateList(targ_matrix, np.array(turn_spaces) % NUM_SPACES, turn)
        # all_spaces.append(turn_spaces)
        turn += 1
    return targ_matrix[-1], turn-1,  # all_spaces

# One trial
h = hit_all_spaces(properties)
h[0].transpose()
print(h[1])  # It took this number of turns to circle the board

# Repeated trials
results = [hit_all_spaces(properties) for x in range(1000)]  # Takes 20 secs...
max_turns = [x[1] for x in results]  # Strips the maximum numbers
np.mean(max_turns)  # About 125 turns for you to hit every property
np.min(max_turns)
plt.hist(max_turns, bins=25)
plt.show()

# Viewing for each space
prop_matrix = np.array([[x[0][i] for x in results] for i in range(len(properties))])
prop_stats = {properties[x]: prop_matrix[x] for x in range(len(properties))}

# Ex. 39: Boardwalk
first_turn39 = prop_stats[39]
plt.hist(first_turn39, bins=50)
plt.show()
np.mean(first_turn39 <= 15)  # 34% within first 15 turns
np.median(first_turn39)  # Median: 23 Turns

def first_turn(space, stats):
    assert space in stats, "ERROR: Must specify an existing space number"
    name = "# Of turns it takes to land on " + SPACES[space]
    med = np.median(stats[space])
    plt.hist(stats[space], bins=50)
    plt.title(name)
    plt.ylabel('Frequency out of ' + str(len(stats[space])) + " trials")
    plt.axvline(med, color='red')
    plt.xlabel('median # turns: ' + str(med), color='red')
    plt.show()

first_turn(15, prop_stats)
np.mean(prop_stats[15] <= 15)  # 42% are within 15 turns

# Space that has the longest median turn:
meds = pd.Series({SPACES[properties[x]]: np.median(prop_matrix[x]) for x in range(len(properties))})
meds.sort_values(ascending=False)

#loading bar, heat map