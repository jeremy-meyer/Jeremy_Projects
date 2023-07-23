os.chdir("github_repos\\Jeremy_Projects\\Acnh_flower_simulation\\")
from flower_class import flower, rose, flower_field, test_flower_field

# Starting simulation
SEED_YELLOW_WHITE_START = 10 # Pairs
SEED_WHITE_WHITE_START = 10 # Pairs
SEED_RED_YELLOW_START = 5 # Pairs
MAX_SIZE = 30

seed_yellow = '0200'
seed_white = '0010'
seed_red = '2001'

# Initialize values
# Stricture level: [plot1[parent1, parent2], plot2[parent1, parent2], ...]
# TODO: figure out how to pass cached probabilities to save simulation time
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

# Rename to successful offspring
# TODO: Set target colors
# rework singleton return dict
# keep track of all children statistics (for genotypes) in the flower fields
# Program color -> genotype into dictionary
# stats for each plot?


DAY_NUM = 0
stage1 = [stage1_yw, stage1_ww, stage1_yr]
while DAY_NUM < 100:
  
  # Run simlulation on the seed-based flowers
  for x in stage1:
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
  stage4_rr.reuse_children() # (stage4_rr, remove_extras=False) # Can also reuse reds

  
  # Final stage
  stage4_oo.transfer_children_to_field(final_target_field)

  DAY_NUM +=1
DAY_NUM

