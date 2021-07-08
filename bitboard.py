import random, board, itertools, math
from functools import lru_cache

"""
Custom exceptions
"""
class FullBoard(Exception):
  pass

class InvalidMoveDirection(Exception):
  pass

class InvalidSpawnLocation(Exception):
  pass


"""
Table initialization
"""

move_left_table = {}
move_right_table = {}
score_table = {}
heuristic_table = {}
loss_penalty = 0

heuristic_weights = (3.5, 11, 4, 47, 700, 270, 200000)

# special-case exponentiation where 2^0 = 0
def exp(n):
  return 0 if n == 0 else 2 ** n

# converts a vector representing the numbers in a row to the corresponding
# 2 bytes representing that row
def row_to_bits(row):
  res = 0
  for n in row:
    # Shift over by a tile
    res <<= 4
    # Or in the value for the current tile
    res |= int(math.log(n, 2) if n != 0 else 0)
  return res

"""
Create move tables
"""
def init_moves():
  for vector in itertools.product(range(16), repeat = 4):
    # convert the vector into the corresponding 2 bytes representing that row
    row = 0
    for n in vector:
      row <<= 4
      row |= n


    """ Move table creation """
    # define the tables of the row – merging operates on non-logs, so have
    # to exponentiate
    new_vec_left, score_table[row] = board.merge([exp(n) for n in vector])
    new_vec_right = list(reversed(board.merge([exp(n) for n in reversed(vector)])[0]))

    move_left_table[row] = row_to_bits(new_vec_left)
    move_right_table[row] = row_to_bits(new_vec_right)


# initiate heuristic table
# takes a list of heuristic weights
# weights has definitions of:
#   idx 0: power scale for sum penalty
#   idx 1: weight for sum penalty
#   idx 2: power scale for monotonicty
#   idx 3: weight for monotonicty
#   idx 4: weight for smoothness
#   idx 5: weight for empty tiles
#   idx 6: loss penalty
def init_heuristics(weights = heuristic_weights):
  supower, suweight, mpower, mweight, sweight, eweight, loss_penalty = weights
  for vector in itertools.product(range(16), repeat = 4):

    """
    Heuristic table creation
    Four heuristics: want high-value tiles, smoothness, empty tiles, and monotonicity
    """

    row = 0
    for n in vector:
      row <<= 4
      row |= n

    sum = smoothness = mono_left = mono_right = empty = 0

    # score tile values and emptiness
    for n in vector:
      sum += n ** supower
      if n == 0: empty += 1

    # score smoothness
    counter = 0
    for i in range(3):
      # might want to do difference of exponents, but probably not
      if vector[i] == vector[i+1]:
        counter += 1
      elif counter > 0:
        sum += 1 + counter
        counter = 0

    if counter > 0: sum += 1 + counter

    # score monotonicity
    for i in range(3):
      if vector[i] > vector[i+1]:
        mono_left += vector[i] ** mpower - vector[i+1] ** mpower
      else:
        mono_right += vector[i+1] ** mpower - vector[i] ** mpower

    heuristic_table[row] = loss_penalty + \
                           empty * eweight - \
                           smoothness * sweight - \
                           min(mono_left, mono_right) * mweight - \
                           sum * suweight

def init(weights=heuristic_weights):
  init_moves()
  init_heuristics(weights)

@lru_cache(maxsize = 1000000)
def heuristic_value(board):
  total_value = 0
  # do rows
  for offset in (0, 16, 32, 48):
    total_value += heuristic_table[(board >> offset) & 0xFFFF]
  # do columns
  for n in range(4):
    cur_col = 0
    for offset in (0, 16, 32, 48):
      # shift to the current tile
      cur_col <<= 4
      # or in the value of the tile at col index n
      cur_col |= (board >> (offset + 4 * n)) & 0xF
    total_value += heuristic_table[cur_col]
  return total_value









# boards are represented as an integer of up to 64 bits
# every four bits is the log of the value of a cell - first four bits are the
# first cell, first 16 bits are the first row, etc. a 0 represents an emtpy tile

def new_board(): return 0

"""
Check if two boards are equal
"""
def equal(b1, b2):
  return b1 == b2

"""
Return a list of ints corresponding to the points where empty tiles begin.
Works right to left, i.e. 0 means the bottom right tile is empty, 1 means
the second-from right tile in the bottom row is empty, etc.
"""
def empty_tiles(board):
  empty_pos = []
  for cur_pos in range(16):
    if not ((board >> (cur_pos * 4)) & 0xF): empty_pos.append(cur_pos)
  return empty_pos

"""
Returns board with a tile randomly spawned.
"""
def spawn_tile(board):
  try:
    spawn_pos = random.choice(empty_tiles(board))
    # log values, so 2 is 4 and 1 is 2
    tile = 2 if random.random() < 0.1 else 1
    return board | (tile << 4 * spawn_pos)
  except IndexError:
    raise FullBoard("Can't spawn tiles on a full board")

def spawn_manual(board, value, loc):
  real_value = int(math.log(value, 2))
  return board | (value << (4 * loc))

"""
Returns board moved in the given direction - L, R, U, or D, along with the
increase in score for moving in that direction
"""
def move(board, dir):
  res = 0
  score_inc = 0
  if dir == "L":
    for offset in (0, 16, 32, 48):
      cur_row = (board >> offset) & 0xFFFF
      res |= move_left_table[cur_row] << offset
      score_inc += score_table[cur_row]

  elif dir == "R":
    for offset in (0, 16, 32, 48):
      cur_row = (board >> offset) & 0xFFFF
      res |= move_right_table[cur_row] << offset
      score_inc += score_table[cur_row]

  elif dir == "U":

    for n in range(4):
      cur_col = 0
      for offset in (0, 16, 32, 48):
        # shift to the current tile
        cur_col <<= 4
        # or in the value of the tile at col index n
        cur_col |= (board >> (offset + 4 * n)) & 0xF
      # look up the replacement for the current column
      replacement_col = move_right_table[cur_col]
      # increment the score
      score_inc += score_table[cur_col]
      # or the replacement column into res
      for offset in (0, 16, 32, 48):
        # 48 - offset + adjust because the col has to put back in reverse
        res |= ((replacement_col >> (int(offset / 4))) & 0xF) << (48 - offset + 4 * n)

  elif dir == "D":
    for n in range(4):
      cur_col = 0
      for offset in (0, 16, 32, 48):
        # shift to the current tile
        cur_col <<= 4
        # or in the value of the tile at col index n
        cur_col |= (board >> (offset + 4 * n)) & 0xF
      # look up the replacement for the current column
      replacement_col = move_left_table[cur_col]
      # increment the score
      score_inc += score_table[cur_col]
      # or the replacement column into res
      for offset in (0, 16, 32, 48):
        # 48 - offset + adjust because the col has to put back in reverse
        res |= ((replacement_col >> (int(offset / 4))) & 0xF) << (48 - offset + 4 * n)

  else:
    # invalid direction given, raise an exception with the given direction
    raise InvalidMoveDirection(dir)

  return res, score_inc

"""
Returns True if no further moves are possible and False otherwise
"""
def game_over(board):
  # easiest but probably not most efficient solution is to just
  # move in every direction and check for changes

  # for speed, check if the board is empty first: quicker than moving
  # in all four directions
  if len(empty_tiles(board)) > 0: return False
  for dir in ("L", "R", "U", "D"):
    if (move(board, dir))[0] != board: return False
  # board is full and no moves are possible – game is over
  return True

"""
Returns the maximum tile present on a board
"""
def max_tile(board):
  max = 0
  while board:
    if board & 0xF > max: max = board & 0xF
    board >>= 4
  return (0 if max == 0 else 2**max)

"""
Converts the board state to string format
"""
def string_of_board(board):
  # for now, give five digits for each tile
  row_div = "-" + "-" * 6 * (4) + "\n"
  state_string = row_div
  for offset in (48, 32, 16, 0):
    state_string += "|"
    for i in (12, 8, 4, 0):
      cur = (board >> offset + i) & (0xF)
      rep = "" if cur == 0 else str(2**cur)
      state_string += (rep.rjust(5) + "|")
    state_string += "\n" + row_div
  # trim trailing newline
  return state_string[:-1]
