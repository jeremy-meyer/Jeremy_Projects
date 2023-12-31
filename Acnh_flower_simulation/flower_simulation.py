import os
# os.chdir("github_repos\\Jeremy_Projects\\Acnh_flower_simulation\\")
from flower_class import flower, rose, flower_field, test_flower_field

seed_yellow = '0200'
seed_white = '0010'
seed_red = '2001'

# Initialize values
# Stricture level: [plot1[parent1, parent2], plot2[parent1, parent2], ...]
# TODO: figure out how to pass cached probabilities to save simulation time

def run_folklore_simulation(
    SEED_YELLOW_WHITE_START = 32, # Pairs
    SEED_WHITE_WHITE_START = 32, # Pairs
    SEED_RED_YELLOW_START = 32, # Pairs
    MAX_SIZE = 40, # Max number of pairs to test at once for a given stage
    ):

  DAY_NUM = 0

  # Stage 1:
  # Seed yellow x seed white
  stage1_yw = flower_field(
    flower_plots=[[rose(seed_yellow), rose(seed_white)] for x in range(SEED_YELLOW_WHITE_START)],
    target_geneotypes=['0110'], 
    max_size=MAX_SIZE,
  )

  # Seed white x seed white
  stage1_ww = flower_field(
    flower_plots=[[rose(seed_white), rose(seed_white)] for x in range(SEED_WHITE_WHITE_START)],
    target_geneotypes=['0020'], 
    max_size=MAX_SIZE,
  )

  # Seed white x seed white
  stage1_yr = flower_field(
    flower_plots=[[rose(seed_yellow), rose(seed_red)] for x in range(SEED_RED_YELLOW_START)],
    target_geneotypes=['1100'], 
    max_size=MAX_SIZE,
  )

  # white (sy X sw) x purple(sw X sw)
  stage2_pw = flower_field(
    flower_plots=[],
    target_geneotypes=['0020', '0120'], 
    max_size=MAX_SIZE,
    add_pattern=['0110', '0020']
  )

  stage2_pp_test = test_flower_field(
    flower_plots=[],
    target_geneotypes=['0210'],
    max_size=MAX_SIZE,
    add_pattern=['0120', '0020'],
    test_flower=rose('0200'),
  )

  stage3_po = flower_field(
    flower_plots=[],
    target_geneotypes=['1210'],
    max_size=MAX_SIZE,
    add_pattern=['1100', '0120'],
  )

  stage4_oo = flower_field(
    flower_plots=[],
    target_geneotypes=['2220', '1220'],
    max_size=MAX_SIZE,
    add_pattern=['1210', '1210'],
  )

  stage4_rr = flower_field(
    flower_plots=[],
    target_geneotypes=['2220', '1220'],
    max_size=MAX_SIZE,
    add_pattern=['1220', '1220'],
  )

  final_target_field = flower_field(
    flower_plots=[],
    target_geneotypes=['2220'],
    max_size=MAX_SIZE,
    add_pattern=['2220', '2220'],
  )

  while DAY_NUM < 1000:
    DAY_NUM +=1
    # Run simlulation on the seed-based flowers
    for x in [stage1_yw, stage1_ww, stage1_yr]:
      x.run_simulation()

    # Stage 2 - Transfer Upstream children & Run
    stage1_ww.transfer_children_to_field(stage2_pw)
    stage1_yw.transfer_children_to_field(stage2_pw)
    
    stage2_pw.run_simulation()

    # Stage 2 - Test output flower
    stage2_pw.transfer_children_to_field(stage2_pp_test)
    stage2_pp_test.run_simulation()

    # Stage 3 - Purple and orange
    stage1_yr.transfer_children_to_field(stage3_po)
    stage2_pp_test.transfer_children_to_field(stage3_po)
    
    stage3_po.run_simulation()

    # Stage 4 - Orange and Orange and R/R (optional)
    stage3_po.transfer_children_to_field(stage4_oo)
    stage4_oo.run_simulation()

    stage4_oo.transfer_children_to_field(stage4_rr, remove_extras=False) # Transfer reds
    stage4_rr.run_simulation()

    if any(x.genotype=='2220' for x in stage4_rr.children):
      break # Got a blue!

    stage4_rr.transfer_children_to_field(stage4_rr, remove_extras=False)

    # Check for Blues
    stage4_oo.transfer_children_to_field(final_target_field)
    stage4_rr.transfer_children_to_field(final_target_field)

    if final_target_field.size(False) > 0:
      break # Got a blue rose
  return DAY_NUM

results = [run_folklore_simulation() for x in range(200)]
np.percentile(results, q=[50, 95])





# Rename to successful offspring
# TODO: Set target colors
# rework singleton return dict
# keep track of all children statistics (for genotypes) in the flower fields
# Program color -> genotype into dictionary
# stats for each plot?


# Check
# stage4_oo.add_flower_to_field(rose('1210'))
# stage4_oo.children = [rose('1220', 0, 0), rose('2220', 0, 0)]
# stage4_oo.transfer_children_to_field(stage4_rr, remove_extras=False)

# # Check reds mechanic
# stage4_rr.add_flower_to_field(rose('1220'))
# stage4_rr.run_simulation(breed_chance=1)

# stage4_rr.children