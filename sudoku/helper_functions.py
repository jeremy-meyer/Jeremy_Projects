import pandas as pd
import numpy as np
import os
from functools import reduce
import operator
from math import floor, ceil
from collections import Counter


# Takes a list of lists down to a singe list
def flatten_list(l):
    return reduce(operator.add, l)


def transpose(m):
   return [list(x) for x in zip(*m)]


def combine_strings(s_list, sep=''):
    return sep.join(s_list)


def debug_print(printout, debug):
    if debug:
        print(printout)


# greedy search for index position of a value
def get_matrix_match(m,value):
    for i in range(len(m)):
        for j in range(len(m[i])):
            if m[i][j] == value:
                return (i,j)

# Function that adds trailing spaces so the string is a specified length
def standardize_length(s, length=11):
    return s + ''.join([' ' for x in range(length - len(s))])

# Takes a list of lists (row-wise), and returns the value at a row/column tuple
def get_vals_from_loc(mat, r_c_pairs):
    if type(mat) == list:
        return [mat[r][c] for r,c in r_c_pairs]
    else:
        r,c = r_c_pairs
        return mat[r][c]


# Assigns a value to a matrix, given an r/c location tuple
def assign_val_to_loc(mat, r_c_pair, value):
    r, c = r_c_pair
    mat[r][c] = value


# SUDOKU FUNCTIONS -----------------------------------------------
# Returns locations of a given row, column square partition number
def square_partition_fun(r_pt, c_pt):
    rows_of_part = LOCATIONS_MATRIX[3 * r_pt:(r_pt + 1) * 3]
    cols_of_part = [row[3 * c_pt:(c_pt + 1) * 3] for row in rows_of_part]
    return flatten_list(cols_of_part)


LOCATIONS_MATRIX = [[(r, c) for c in range(9)] for r in range(9)]
ROW_LOCATIONS = LOCATIONS_MATRIX.copy()
COL_LOCATIONS = [[LOCATIONS_MATRIX[r][c] for r in range(9)] for c in range(9)]
SQUARE_LOCATIONS = [square_partition_fun(r_pt, c_pt) for r_pt in range(3) for c_pt in range(3)]


# Turns a 81 character string into a matrix
def create_sudoku_matrix(s):
    return np.array([int(x) for x in [*s]]).reshape((9,9))


# Returns 27 lists of the values in each of the constraints (row/column/square)
# Useful for puzzle verification
def return_27_constraints(m):
    rows = list(m)
    cols = list(m.T)
    squares = [m[3 * r:(r + 1) * 3, 3 * c:(c + 1) * 3].flatten() for r in range(3) for c in range(3)]
    return [*rows, *cols, *squares]


# Verifies each number in the list is unique
def verify_constraint(one_constraint_list):
    l_filled = [x for x in one_constraint_list if x != 0] # Remove 0s (Unfilled)
    return len(set(l_filled)) == len(l_filled)


# Takes a matrix as an input and verifies that the puzzle is valid
def verify_sudoku_puzzle(m):
    constraint_list = return_27_constraints(m)
    return all([verify_constraint(x) for x in constraint_list])


# PRINTING
# Creates 1 row of puzzle for string printing
def prep_row_to_str(row_list, string_length, inside_sep_char='|'):
    row = [standardize_length(x, string_length) for x in row_list]
    row.insert(0, standardize_length('||', string_length))
    row.insert(3+1, standardize_length(inside_sep_char, string_length))
    row.insert(6+2, standardize_length(inside_sep_char, string_length))
    row.append('||')
    return combine_strings(row)


def compress_set_string(potential_values):
    return [
        [str(sorted(val)).replace(' ', '').replace(',', '') for val in row]
        for row in potential_values
    ]


def pretty_print_str(m, replace_blanks='_', changed_vals=[], guessed_vals=[], string_length=4):
    m_str = np.array(m, dtype='U2')
    if len(changed_vals) != 0:
        for r,c in changed_vals:
            m_str[r][c] += '*'
    if len(guessed_vals) != 0:
        print('Guessed values')
        for r,c in guessed_vals:
            m_str[r][c] += '^'
    main_puzzle_list = [
        prep_row_to_str(x, string_length, inside_sep_char=' ').replace('0', replace_blanks)
        for x in m_str
    ]
    print(m_str)
    mid_lines = prep_row_to_str(
        [standardize_length(' ', string_length) for x in range(9)], string_length, inside_sep_char="+"
    )
    horizontal_edge = ''.join([standardize_length('--', string_length) for x in range(9+2)])
    main_puzzle_list.insert(3, mid_lines)
    main_puzzle_list.insert(6+1, mid_lines)
    top_border = standardize_length('//', string_length) + horizontal_edge + '\\\\'
    bottom_border = standardize_length('\\\\', string_length) + horizontal_edge + '//'
    print('\n'.join(['SUDOKU:', top_border, *main_puzzle_list, bottom_border]))




# SOLVER ALGORITHIM
def get_num_empty_spaces(puzzle):
    if isinstance(puzzle, str):
        return len([x for x in s_inc if x=='0'])
    elif isinstance(puzzle, np.ndarray):
        return 9*9 - np.count_nonzero(puzzle)


# Returns a list of possible values the cell
def get_possible_values(m, r, c):
    rows = m[r]
    cols = m[:,c]
    squares = m[3*floor(r/3):(floor(r/3)+1)*3, 3*floor(c/3):(floor(c/3)+1)*3].flatten()
    return set(range(1,9+1)) - set(rows) - set(cols) - set(squares)


def get_all_possible_values(m, unknown_val=0):
    result = [[set() for x in range(9)] for y in range(9)]
    for r in range(9):
        for c in range(9):
            cell_value = m[r,c]
            if cell_value == unknown_val:
                result[r][c] = get_possible_values(m, r, c)
            else:
                result[r][c] = set()
    return result


# Step 2:Look at all potential values in the 27 configurations. (If a single number, then fill)
def check_for_single_potential_values(potential_value_matrix):

    # Check for a single potential value in a given list
    def check_for_single_numbers(potential_values_matrix, locations):
        potential_values_box = get_vals_from_loc(potential_values_matrix, locations)
        combined_list = [list(s) for s in potential_values_box]
        tabulated = {x: reduce(operator.add, combined_list).count(x) for x in range(1, 9 + 1)}
        single_nums = [num for num, num_total in tabulated.items() if num_total == 1]
        num_values_to_fill = len(single_nums)
        if num_values_to_fill > 0:
            find_index_fun = lambda num: [i for i, p_v in enumerate(potential_values_box) if num in p_v][0]
            single_indexes = [find_index_fun(x) for x in single_nums]
            vals_to_fill = {locations[single_indexes[i]]: single_nums[i] for i in range(num_values_to_fill)}
            return vals_to_fill
        else:
            return dict()

    row_singles = [check_for_single_numbers(potential_value_matrix, x) for x in ROW_LOCATIONS]
    col_singles = [check_for_single_numbers(potential_value_matrix, x) for x in COL_LOCATIONS]
    square_singles = [check_for_single_numbers(potential_value_matrix, x) for x in SQUARE_LOCATIONS]

    # Merge all single potential matches and dedupe (LATER WORK ON THIS)
    list_of_singles_duped = row_singles + col_singles + square_singles
    values_to_assign_list = flatten_list([list(d.items()) for d in list_of_singles_duped])
    values_to_assign_deduped = list(set(values_to_assign_list))
    return values_to_assign_deduped


def solve_puzzle(
        sudoku_matrix,
        debug=False,
        init_values={'iterations': 0, 'locations_changed': [], 'locations_guessed': []},
        working_from_guess = False,
):
    # Set Up
    og_matrix = sudoku_matrix.copy()
    result_matrix = og_matrix.copy()
    iteration = init_values['iterations']
    changed_cells = init_values['locations_changed'].copy()
    guessed_cells = init_values['locations_guessed'].copy()
    unsolved_cells = get_num_empty_spaces(result_matrix)
    puzzle_solved = unsolved_cells == 0

    if debug:
        single_valued = []
        only_1_number = []
        potential_values_debug = []

    while unsolved_cells > 0:
        iteration += 1
        debug_print(f'Starting iteration {iteration} with {unsolved_cells} unsolved cells', debug)
        potential_values = get_all_possible_values(result_matrix)
        num_potential_values = [[len(c) for c in r] for r in potential_values]

        # Cells where there is only 1 potential value (Is this even necessary?)
        cells_with_1_potential_value = flatten_list([
            [((r, c), list(potential_values[r][c])[0]) for c in range(9) if num_potential_values[r][c] == 1]
                for r in range(9)
        ])

        # Cells where a value can only occur at the location
        cells_with_only_numeric_value = check_for_single_potential_values(potential_values)

        cells_to_assign = set(cells_with_only_numeric_value + cells_with_1_potential_value)

        if debug:
            single_valued.append(cells_with_1_potential_value)
            only_1_number.append(cells_with_only_numeric_value)
            potential_values_debug.append(potential_values)

        num_cells_to_assign = len(cells_to_assign)

        for r_c, value in cells_to_assign:
            assign_val_to_loc(result_matrix, r_c, value)
            # result_matrix[r,c] = value
            if working_from_guess:
                guessed_cells.append((r,c))
            else:
                changed_cells.append((r_c))
            debug_print(f'Assigned {r_c} to value {value}', debug)

        unsolved_cells = get_num_empty_spaces(result_matrix)

        if (num_cells_to_assign == 0) and (unsolved_cells>0):
            debug_print('Unable to fully finish puzzle solver', debug)
            break
        elif unsolved_cells == 0:
            debug_print(f'Successfully solved Puzzle after {iteration} iterations!', debug)
            puzzle_solved = True
        else:
            debug_print(f'After iteration {iteration}, {unsolved_cells} cells left to solve', debug)
        if debug:
            pretty_print_str(result_matrix, changed_vals=changed_cells, guessed_vals=guessed_cells, string_length=4)

    return_dict = {
        'result': result_matrix,
        'locations_changed': changed_cells,
        'locations_guessed': guessed_cells,
        'iterations': iteration,
        'valid_puzzle': verify_sudoku_puzzle(result_matrix),
        'puzzle_solved': puzzle_solved,
    }
    if debug:
        return_dict['single_potential_values'] = single_valued
        return_dict['only_number_occurance'] = only_1_number
        return_dict['potential_values'] = potential_values_debug

    return return_dict

