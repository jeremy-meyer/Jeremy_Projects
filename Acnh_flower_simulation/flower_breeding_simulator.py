import numpy as np
import random, collections, itertools

# Method 1: 

# Genes - Red - Yellow - White - Special
# Blue rose - 2220
# seed red - 2001
# seed white - 0010
# seed yellow - 0200
# Chance is 5%, but there is a counter that goes up by 5% for each water after 4 times


# Selects a random gene from the parent
def inherit_trait(x):
  if x=='2':
    # Parent has both dominant genes
    return 1
  elif x=='0':
    # Parent has both recessive genes
    return 0
  elif x=='1':
    # Parent has both dominant and recessive gene
    return random.randint(0,1)

# Generates a child flower
def breed_offspring(parent1, parent2):
  return ''.join(
    str(inherit_trait(parent1[x]) + inherit_trait(parent2[x])) for x in range(len(parent1))
    )

# Use punnet square mechanics to generate exact probabilities for the parent gene sequences
def enumerate_probabilities(parent1, parent2):
  print(f"Parent ({parent1}) X parent ({parent2})")
  gene_key = {'0': (0, 0), '1': (1, 0), '2': (1, 1)}
  def enumerate_one_gene(p1, p2): 
    return [str(sum((x,y))) for x in gene_key[p1[0]] for y in gene_key[p2[0]]] 
  
  individual_enums = tuple(enumerate_one_gene(parent1[i], parent2[i]) for i in range(len(parent1)))
  all_enums = tuple(''.join(x) for x in list(itertools.product(*individual_enums)))
  d = dict(collections.Counter(all_enums))
  N = sum(d.values())
  return {gene : d[gene] / N for gene in d}


# Samples from a categorical distribution, rescales weights to 1
# Takes a dictionary of values : weights
def random_by_weight(prob_dict, chance_of_value=0.05):
  if random.random() >= chance_of_value:
    return None
  possibilities = list(prob_dict.keys())
  weights = list(prob_dict.values())
  cum_weights = [sum(weights[:x]) for x in range(1, len(weights)+1)]
  rand_value = random.random()*sum(weights) # Scale to weights
  return possibilities[np.where(rand_value <= np.array(cum_weights))[0][0]]
ini


# Starting simulation
SEED_YELLOW_WHITE_START = 10 # Pairs
SEED_WHITE_WHITE_START = 10 # Pairs
SEED_RED_YELLOW_START = 5 # Pairs
BASE_BREEDING_RATE = 0.05 # Higher for more visits

seed_yellow = '0200'
seed_white = '0010'
seed_red = '2001'

# Initialize values
DAY_NUM = 0
FLOWER_TOTALS = {
  'white_0110' : 0,
  'purple_0020' : 0,
  'orange_1100' : 0,
  'purple_unknown' : 0,
  'purple_0120' : 0,
  'orange_1210' : 0,
  'red_1220' : 0,
  'blue_2220' : 0,
}

# Stage 1: Seed yellow vs seed white
stage1_yw_probs = enumerate_probabilities(seed_yellow, seed_white)
# Stricture level: [plot1[parent1, parent2], plot2[parent1, parent2], ...]
stage1_yw_table = [
  [[seed_yellow, 0], [seed_white, 0]] for x in range(SEED_YELLOW_WHITE_START)
]
[random_by_weight(stage1_yw_probs) for x in range(SEED_YELLOW_WHITE_START)]

[]








parent1 = '0011'
parent2 = '0212'
prob_dict = enumerate_probabilities(parent1, parent2)


N = 100000
simulations = dict(collections.Counter([breed_flower(parent1, parent2) for x in range(N)]))


{
  genes : simulations[genes]/N
  for genes in simulations
}










     
        
