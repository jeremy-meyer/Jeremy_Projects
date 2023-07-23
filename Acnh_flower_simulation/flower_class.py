import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import random, collections, itertools

class flower(ABC):
  global_color_map = pd.read_csv('acnh_color_map/roses.csv', dtype='str')

  # Subset the color map table to a single species
  @staticmethod
  def subset_global_color_map(species):
    return flower.global_color_map[flower.global_color_map['species']==species.lower()]
  
  # Generic phenotype (color) lookup of from a given map
  @staticmethod
  def genotype_to_color(genotype, color_map):
    return color_map[color_map['genotype']==genotype].color.values[0]
  
  def __init__(self, genotype, visitors=0, water_counter=0):
    self.water_counter = water_counter # Starts at zero
    if any(c not in '012' for c in genotype):
      raise ValueError("Genotype must be represented by trinary digits")
    self.genotype = genotype
    self.visitors = visitors
    self.test_attempts = 0 # Used for test breeds

    if hasattr(self, "color_map"):
      self.color = self.genotype_to_color(self.genotype)
    else:
      self.color = 'undefined'

  # Gets the chance the flower will produce offspring
  def get_breeding_chance(self) -> float:
    counter_chance = min(0.9, 0.05 + max(0.0, 0.05*(self.water_counter - 3))) # cap of 90%
    visitor_bonuses = {0 : 0.0, 1 : 0.2, 2 : 0.3, 3 : 0.45, 4 : 0.6, 5 : 0.75}
    visitor_chance = visitor_bonuses[min(5, self.visitors)]
    return min(1.0, counter_chance + visitor_chance)

  # Simulates watering the plant and incrementing the counter
  def water(self) -> None:
    self.water_counter += 1

  # Resets water counter
  def reset_water_counter(self) -> None:
    self.water_counter = 0

  # Returns a clone of the flower
  def clone(self):
    return type(self)(genotype=self.genotype, visitors=self.visitors)
  
  # Returns a dictionary of possible offspring and their probabilities
  def enumerate_offspring(self, flower2, color=False) -> dict:
    # print(f"Parent ({parent1}) X parent ({parent2})")
    if (type(self)  != type(flower2)) or (len(self.genotype) != len(flower2.genotype)):
      raise TypeError("Parents must be of the same flower species and have the same number of genes")
    parent1 = self.genotype
    parent2 = flower2.genotype
    gene_key = {'0': (0, 0), '1': (1, 0), '2': (1, 1)}
    enumerate_one_gene = lambda p1, p2: \
      [str(sum((x,y))) for x in gene_key[p1[0]] for y in gene_key[p2[0]]] 
    
    individual_enums = tuple(enumerate_one_gene(parent1[i], parent2[i]) for i in range(len(parent1)))
    all_enums = tuple(''.join(x) for x in list(itertools.product(*individual_enums)))
    if color:
      assert hasattr(self, "color_map"), f"Color map undefined for class {type(self)}"
      all_enums = [self.genotype_to_color(x) for x in all_enums]
    d = dict(collections.Counter(all_enums))
    N = sum(d.values())
    return {gene : d[gene] / N for gene in d}
  
  # If reproduction chance is successful, returns a child flower, else returns None
  def breed(self, parent2, breed_chance=None, child_visitors=None):
    if breed_chance is None:
      breed_chance = self.get_breeding_chance()
    if child_visitors is None:
      child_visitors = self.visitors # inherits this from parent if not defined
    
    if random.random() <= breed_chance:
      self.reset_water_counter()
      if parent2 is None:
        # Create a clone
        return self.clone()
      else:
        parent2.reset_water_counter()
        all_outcomes_dict = self.enumerate_offspring(parent2)
        possibilities = list(all_outcomes_dict.keys())
        weights = list(all_outcomes_dict.values())
        cum_weights = [sum(weights[:x]) for x in range(1, len(weights)+1)]
        rand_value = random.random()*sum(weights) # Scale to weights
        child_genotype = possibilities[np.where(rand_value <= np.array(cum_weights))[0][0]]
        return type(self)(genotype=child_genotype, visitors=self.visitors)
    else:
      return None
  
  # eval(repr(obj)) printable representation (for devs)
  def __repr__(self) -> str:
    flower_species = type(self).__name__
    return f"{flower_species}('{self.genotype}', {self.visitors}, {self.water_counter})" 

  # Human-readable string of object (for users)
  def __str__(self) -> str:
    flower_species = type(self).__name__
    return f"{flower_species}(genes: '{self.genotype}', color: {self.color}, watered: {self.water_counter}, visitors: {self.visitors})" 
  

class rose(flower):
  # Global class variables
  color_map = flower.subset_global_color_map('rose')
  n_genes = 4

  @staticmethod
  def genotype_to_color(genotype):
    if len(genotype) != rose.n_genes:
      raise ValueError(f"Rose genotype must be {rose.n_genes} characters")
    return flower.genotype_to_color(genotype, rose.color_map)

  def __init__(self, genotype, visitors=0, water_counter=0):
    super().__init__(genotype, visitors, water_counter)

# class flower_plot:

#   def __init__(self, flower1, flower2=None):
#     if not isinstance(flower1, flower):
#       raise(TypeError('Flower1 must be a type of flower'))
#     if flower2 is not None:
#       if not isinstance(flower2, flower):
#         raise(TypeError('Flower2 must be a type of flower'))
#       self.flower_pair = [flower1, flower2]
#     else:
#       self.flower_pair = [flower1,]
    
#     self.attempts = 0

# Contains a plot of flowers
class flower_field:

  def __init__(self, flower_plots, target_geneotypes, max_size=None, add_pattern=None) -> None:
    self.day_num = 0
    self.unused_offspring = 0
    self.lifetime_children = 0
    self.max_size = max_size
    self.children = []

    self.target_genotypes = target_geneotypes
    if any([len(x) > 2 for x in flower_plots]):
      raise(ValueError('Flower plots should be defined in pairs'))
    if any([any([not isinstance(f, flower) for f in p]) for p in flower_plots]):
      raise(TypeError('Flower plot pairs should be a type of flower'))
    self.flower_plots = flower_plots

    if (add_pattern is None) and (self.size(pairs_only=True)>0):
      self.add_pattern = [f.genotype for f in self.flower_plots[0]] # detect from first parents
    else:
      self.add_pattern = add_pattern
  
  def plot_sizes(self) -> int:
    return [len(x) for x in self.flower_plots]
  
  def size(self, pairs_only=False) -> int:
    if pairs_only:
      return sum([1 for x in self.plot_sizes() if x==2])
    else:
      return len(self.flower_plots)
    
  def get_plot_num(self, i):
    return self.flower_plots[i]
  
  # Waters all flowers in the plot
  def water(self):
    for plots in self.flower_plots:
      for flower_i in plots:
        flower_i.water()
  
  # Returns the indexes of single flowers and their genotypes 
  def check_for_singletons(self):
    singletons = [(i, fp[0].genotype) for i, fp in enumerate(self.flower_plots) if len(fp)==1]
    return singletons
    
  def collect_offspring(self, new_flower):
    if not isinstance(new_flower, flower):
      raise(TypeError('Child must be a flower type'))
    self.lifetime_children +=1
    self.children.append(new_flower)

  def transfer_children_to_field(self, new_field):
    new_field.add_flower_to_field(self.children)
    self.children = []
    
  def __repr__(self) -> str:
    return f"{type(self).__name__}({repr(self.flower_plots)}, {self.target_genotypes}, {self.max_size}, {self.add_pattern})"

  def run_simulation(self, breed_chance=None):
    for pair in self.flower_plots:
      # Skip if not a pair
      if len(pair)==2:
        p1, p2 = pair
        p1.water()
        p2.water()
        child = p1.breed(p2)
        if child is not None:
          if child.genotype in self.target_genotypes:
            self.collect_offspring(child)
          else:
            self.unused_offspring += 1
    self.day_num +=1


  def add_new_plot(self, flower1, flower2=None):
    if not isinstance(flower1, flower):
      raise(TypeError("Object flower1 is not of class flower"))
    if (self.max_size is not None) and (self.size() + 1 > self.max_size):
      return False
    if flower2 is None:
      self.flower_plots.append([flower1,])
    else:
      if not isinstance(flower2, flower):
        raise(TypeError("Object flower2 is not of class flower"))
      self.flower_plots.append([flower1,flower2])
      return True


  def add_to_existing_plot(self, flower_to_add, i):
    N = self.size()
    if i >= N:
      raise IndexError(f"Index {i} greater than the number of flower plots")
    existing = self.get_plot_num(i)
    if not isinstance(flower_to_add, flower):
      raise TypeError("Attempting to add a non-flower object")
    if len(existing)==2:
      raise(ValueError('Plots can only have at most 2 flowers'))
    else:
        self.flower_plots[i].append(flower_to_add)
        return True
    
  def add_flower_to_field(self, flowers, debug=False):
    assert self.add_pattern is not None, "please provide instructions on how to add new flowers"
    if not isinstance(flowers, list):
      flowers = [flowers]
    for f in flowers:
      if f.genotype in self.add_pattern:
        if debug:
          print(f'Adding flower {f} to plot')
        singles = self.check_for_singletons()
        # Check for any single flowers that are available
        if len(singles) != 0:
          if debug:
            print('Single flower plots found')
          single_locs, single_genes = zip(*singles)
          missing_flower_key = {
            self.add_pattern[0] : self.add_pattern[1], self.add_pattern[1]: self.add_pattern[0]
          }
          is_genotype_desired = [(f.genotype in missing_flower_key[x]) for x in single_genes]
          if any(is_genotype_desired):
            first_available = [i for i in range(len(is_genotype_desired)) if is_genotype_desired[i]][0]
            location = single_locs[first_available]
            if debug:
              print(f'Adding flower to plot # {location}')
            return self.add_to_existing_plot(f, location)
        if debug:
          print('Adding flower to new plot')
        return self.add_new_plot(f)
      else:
        if debug:
          print('Skipping flower; pattern is not needed')
          return False


# Add pattern is now a list of possible genotypes to test
# Target genotypes is the result of the test
# Offspring are the sucessful breeds
class test_flower_field(flower_field):

  def __init__(self, flower_plots, target_geneotypes, test_flower, max_size=None, add_pattern=None, max_tries=4) -> None:
    super().__init__(flower_plots, target_geneotypes, max_size, add_pattern)
    
    if not isinstance(test_flower, flower):
      raise(TypeError("Flower to test against must inherit from the flower class"))
    self.test_flower = test_flower.clone()
    self.max_tries = max_tries

    self.total_failed_attempts = 0
    self.successful_attempts = 0
    self.failed_offspring = 0


  def add_flower_to_field(self, flowers, debug=False):
      assert self.add_pattern is not None, "Please provide possible genotypes to be tested/added to field"
      if not isinstance(flowers, list):
        flowers = [flowers]
      for f in flowers:
        if f.genotype in self.add_pattern:
          if debug:
            print(f'Adding flower {f} to plot')
          return self.add_new_plot(f, self.test_flower.clone())
        else:
          if debug:
            print('Skipping flower; pattern is not needed')
            return False
          
  def remove_plot(self, i):
    return self.flower_plots.pop(i)

  def run_simulation(self, breed_chance=None):
    pairs_to_remove = []
    for i, pair in enumerate(self.flower_plots):
      # Skip if not a pair
      if len(pair)==2:
        par1, par2 = pair
        par1.water()
        par2.water()
        child = par1.breed(par2, breed_chance)
        if child is not None:
          if child.genotype in self.target_genotypes:
            # Test successful!
            self.collect_offspring(par1) # Collect parent of interest
            pairs_to_remove.append(i)
            self.successful_attempts += 1
          else:
            # Increase failed attempt counter on the flower
            par1.test_attempts += 1 
            self.total_failed_attempts += 1
            if par1.test_attempts > self.max_tries:
              pairs_to_remove.append(i)
              self.failed_offspring += 1
    
    # Remove failed flowers after loop
    for i_removal in pairs_to_remove:
      print(i_removal)
      self.remove_plot(i_removal)
    pairs_to_remove = []
    self.day_num +=1  



p1 = rose("0200")
p2 = rose("2001")
p3 = rose('0120')
p3_bad = rose('0020')
# p1.get_breeding_chance()
# p1.enumerate_offspring(p2)
# print(p1)

# Breed and collect offspring as usual
# Check if offspring is part of the target, if so collect it!
# Remove the plot for testing. No longer needed! 
# If max tries limit has exceeded, remove plot



# ff = flower_field([[p1.clone(), p2.clone()] for x in range(10)], ['1100'], 50)
# ff_test = test_flower_field([[p3.clone(), rose('0200')]] ,target_geneotypes=['0210'], test_flower=rose('0200'), add_pattern=['0020', '0120'], max_tries=3)
# ff_test.add_flower_to_field(p3_bad.clone(), True)
# ff_test.add_flower_to_field(p3.clone(), True)
# ff_test.size()
# ff_test.run_simulation(1.1)
# ff_test.children
# ff_test



