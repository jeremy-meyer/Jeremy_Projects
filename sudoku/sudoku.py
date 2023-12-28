# os.chdir('/Users/jerem/Personal_Projects/sudoku/') # Do I need this?

# IMPORT FUNCTIONS
from helper_functions import *
importlib.import_module('functions') # Figure this out later
execfile('helper_functions.py')

# Make a sukoku board object. Can just be string of 81 numbers
puzzles = pd.read_csv('examples/sudoku_0.csv', dtype={'puzzle': str, 'solution': str})
hard_puzzle = [
    [7,5,2,0,0,0,0,0,8],
    [4,0,0,2,0,0,0,7,0],
    [9,0,1,0,7,8,4,0,0],
    [5,0,6,0,0,0,0,0,0],
    [0,7,0,0,0,0,0,8,0],
    [0,0,0,0,0,0,1,0,7],
    [0,0,7,9,1,0,5,0,3],
    [0,9,0,0,0,3,0,0,6],
    [6,0,0,0,0,0,7,4,9],
]


s = puzzles['solution'][0]
s_inc = puzzles['puzzle'][0]
all([verify_sudoku_puzzle(create_sudoku_matrix(x)) for x in puzzles['solution']]) # All valid?
solved_puzzles = [solve_puzzle(create_sudoku_matrix(puzzles['puzzle'][x])) for x in range(1000)]

unsolved_puzzles =[x for x in solved_puzzles if not x['puzzle_solved']]
unsolved_example = unsolved_puzzles[0]


m = create_sudoku_matrix(s)
m_inc = create_sudoku_matrix(s_inc)
checks = return_27_constraints(m)


pretty_print_str(m, string_length=4) # Prints puzzle
pretty_print_str(m_inc, '_', string_length=4) # Prints Incomplete Puzzle


# Basic Solver --------------------

result_hard = solve_puzzle(unsolved_example['result'], debug=True) #solve_puzzle(np.array(hard_puzzle), debug=True) #
potential_values = result_hard['potential_values'][-1].copy() # potential values in each cell
pretty_print_str(compress_set_string(potential_values),string_length=8)

# Takes a potential values matrix of sets and returns a potential "guess" with its location
# Currently takes the cell with the fewest # of potential values, and then by the frequency the value set appears
def guess_missing_value(result_matrix):
    potential_values = get_all_possible_values(result_matrix)
    all_potential_sets = [(frozenset(item), len(item)) for item in flatten_list(potential_values)]
    min_set_length = min([x[1] for x in all_potential_sets if x[1]!=0])
    guess_values = Counter([x[0] for x in all_potential_sets if x[1] == min_set_length]).most_common(1)[0][0]
    location = get_matrix_match(potential_values, guess_values)
    guess_values_list = list(guess_values)
    return {'guess' : guess_values_list[-1], 'location' : location, 'potential_values' : guess_values_list}


# make a guess_list = [(guess, loc, potential_values)]
# add a field for has_guesses
all_guesses = []
all_results = result_hard.copy()
result_matrix = all_results['result'].copy()
make_new_guess = True


# Make initial guess and assign to matrix
while not all_results['puzzle_solved']:
    if make_new_guess:
        guess = guess_missing_value(result_matrix)
        all_guesses.append(guess)
    print(f"Trying value {guess['guess']} at location {guess['location']}...")
    assign_val_to_loc(result_matrix, guess['location'], guess['guess'])

    # Next check to see if any new values can be assigned
    all_results = solve_puzzle(
        result_matrix,
        True,
        init_values=all_results,
    )
    result_matrix = all_results['result']
    print(all_guesses)

    if not all_results['valid_puzzle']:
        # If a guess fails, Get most recent guess, remove the potential value sampled
        print('Guess produced invalid puzzle, trying a different value...')
        assign_val_to_loc(result_matrix, all_guesses[-1]['location'], 0)
        all_guesses[-1]['potential_values'].remove(all_guesses[-1]['guess'])
        # If we've exhausted potential guesses, go back to previous guess and retry
        while len(all_guesses[-1]['potential_values']) == 0:
            all_guesses = all_guesses[:-1]
            assert len(all_guesses) != 0, 'Greedy solver failed, exhausted all potential solutions'
            assign_val_to_loc(result_matrix, all_guesses[-1]['location'], 0)
            all_guesses[-1]['potential_values'].remove(all_guesses[-1]['guess'])
        # Assign new guess based on leftover potential values
        all_guesses[-1]['guess'] = all_guesses[-1]['potential_values'][0]
        guess = all_guesses[-1]
        make_new_guess = False






# Potential values
pretty_print_str(compress_set_string(get_all_possible_values(result2['result'])), string_length=8)

# Step 1: List all potential values in each cell (if 1, then fill) - DONE
# Step 2:Look at all potential values in the 27 configurations. (If a single number, then fill) - DONE

# Step 3: Iterate guessing algorithim
# Greedy search
# Enumeration

# Ideas: Start by guessing where there are 2 options and/or repeated patterns
#


# result_hard2 = result_hard.copy()
# for loc, value in values_to_assign_deduped:
#     assign_val_to_loc(result_hard2, loc, value)


# Step 3: Guess and check. Iterate until a solution is found

potential_values = \

    [str(sorted(s)).replace(' ', '').replace(',','') for val in potential_values[0]]
[str(sorted(s)).replace(' ', '').replace(',','') for val in result_hard['potential_values'][0][0]]


unsolved = create_sudoku_matrix(puzzles['puzzle'][0])






# 27 "Equations" or checks (9 rows, 9 columns, 9 squares)
# 81 values (1-9)
# each value is represented in 3 equations
# each equation has N-1 degrees of freedom





# How to generate random sudoku puzzles?
# What is the minimum number of initial values needed for a solvable puzzle?
# How can we relate this to degrees of freedom?
# How many unique soduku (solved) boards are there?
# Can we generalize to other sizes?
# Make a solver via basic iteration

# Sudoku obkect
# Stores string, matrix for easy storage compute. Has isValid

# Class storage (is it possible to just store pointers)
# Efficiency


