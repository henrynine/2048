import random, numpy, getch, os, math
from copy import deepcopy
#import copy

# row then  column

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
For now, do board as 2d list of ints, eventually, move to bit representation
Tiles are represented as the number of that tile, or 0 if they're empty
"""
def new_board():
  #return numpy.zeros((4,4)).astype(int)
  return [[0 for n in range(4)] for n in range(4)]

"""
Returns a list of tuples corresponding to the coordinates of all empty squares
in board
"""
def empty_tiles(board):
  return [(x, y) for x in range(len(board))
                 for y in range(len(board[0]))
                 if board[x][y] == 0]

"""
Check if two boards are equal
"""
def equal(b1, b2):
  return numpy.array_equal(b1, b2)

"""
Spawns a tile in a empty space of the board. 90% chance of 2, 10% chance of 4
"""
def spawn_tile(board):
  new_board = deepcopy(board)
  try:
    spawn_x, spawn_y = random.choice(empty_tiles(new_board))
    # 90% chance of 2, 10% chance of 4
    new_board[spawn_x][spawn_y] = (4 if random.random() < 0.1 else 2)
    return new_board
  except IndexError:
    # give a message explaining the error if the board is full
    raise FullBoard("Can't spawn tiles on a full board")

"""
Spawns an n tile at tile t, where t is a tuple (x, y) of coordinates
"""
def spawn_manual(board, n, t):
  new_board = deepcopy(board)
  if new_board[t[0]][t[1]] == 0:
    new_board[t[0]][t[1]] = n
    return new_board
  raise InvalidSpawnLocation("Can't spawn a tile where one already exists")

"""
Helper function for smoothness evaluation
"""
def find_next_tile(board, x, y, dir):
    i = 0
    if dir == 1:
        while(i < 4 and board[x][y + i] == 0):
            i += 1
        return ((x, y + i), board[x][y + i])
    else:
        while(i < 4 and board[x + i][y] == 0):
            i += 1
        return ((x, y + i), board[x][y + i])

"""
Merges a row towards the left and returns the new row and increase in score
"""
def merge(row):
  score_inc = 0
  length = len(row)
  row = [x for x in row if x != 0]
  for i in range(len(row)-1):
    # row gets shorter as merges are made, so check for out of bounds
    if i >= len(row) - 1: break
    if row[i] == row[i+1]:
      row[i] = 2 * row[i]
      # merge made – increase the score
      score_inc += row[i]
      del row[i+1]
  # pad with 0s on the right and add score_inc
  return ((row + [0] * (length - len(row))), score_inc)

"""
Merges a whole board to the left and returns the new board and increase in score
For efficiency reasons, doesn't deepcopy the board because this function is
only called by move() and that function automatically makes copies for 3/4
directions
"""
def merge_left(board):
  score_inc = 0
  for row_idx in range(len(board)):
    board[row_idx], i = merge(board[row_idx])
    score_inc += i
  return (board, score_inc)

"""
Returns the transpose of a board
"""
def trans(board):
  return list(map(list, zip(*board)))

"""
Returns the result of moving board in the given direction (l, r, u, d) and
the increase in score from making that move as tuple (new_board, score_inc)
"""
def move(board, dir):
  if dir == "L":
    # have to make a copy of the board or else it changes the same rows
    # that the board passed as an argument points to
    return merge_left(deepcopy(board))
  elif dir == "R":
    img, score_inc = merge_left([list(reversed(row)) for row in board])
    return ([list(reversed(row)) for row in img], score_inc)
  elif dir ==  "U":
    img, score_inc = merge_left(trans(board))
    return (trans(img), score_inc)
  elif dir == "D":
    img, score_inc = merge_left([list(reversed(row)) for row in trans(board)])
    return (trans([list(reversed(row)) for row in img]), score_inc)
  else:
    # invalid direction given, raise an exception with the given direction
    raise InvalidMoveDirection(dir)

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
Converts the board state to string format
"""
def string_of_board(board):
  # for now, give five digits for each tile
  row_div = "-" + "-" * 6 * (len(board)) + "\n"
  state_string = row_div
  for row in board:
    state_string += "|"
    for i in range(len(row)):
      rep = "" if row[i] == 0 else str(row[i])
      state_string += (rep.rjust(5) + "|")
    state_string += "\n" + row_div
  # trim trailing newline
  return state_string[:-1]







"""
Heuristics below here
"""

heuristic_weights = (73.44, 12.23, 28.89, 54.10, 18.13)

def init(weights = heuristic_weights):
  global heuristic_weights
  heuristic_weights = weights


"""
Returns the board value as sum of all tiles / # of non-0 tiles
"""
def getBoardValue(state):
    sum = 0
    for x in range(4):
        for y in range(4):
            sum = sum + state[x][y]
    return sum / (16 - len(empty_tiles(state)))

"""
Returns the board value as a gradient matrix * the current board
"""
def getBoardValue2(state):
    gradients = [[[ 3,  2,  1,  0],[ 2,  1,  0, -1],[ 1,  0, -1, -2],[ 0, -1, -2, -3]],[[ 0,  1,  2,  3],[-1,  0,  1,  2],[-2, -1,  0,  1],[-3, -2, -1, -0]],[[ 0, -1, -2, -3],[ 1,  0, -1, -2],[ 2,  1,  0, -1],[ 3,  2,  1,  0]],[[-3, -2, -1,  0],[-2, -1,  0,  1],[-1,  0,  1,  2],[ 0,  1,  2,  3]]]
    gradients2 = [[[ 3,  0,  0,  0],[ 0,  0,  0, -0],[ 0,  0, -0, -0],[ 0, -0, -0, -3]],[[ 0,  0,  0,  3],[-0,  0,  0,  0],[-0, -0,  0,  0],[-3, -0, -0, -0]],[[ 0, -0, -0, -3],[ 0,  0, -0, -0],[ 0,  0,  0, -0],[ 3,  0,  0,  0]],[[-3, -0, -0,  0],[-0, -0,  0,  0],[-0,  0,  0,  0],[ 0,  0,  0,  3]]]
    values = [0, 0, 0, 0]
    for i in range(4):
        for x in range(4):
            for y in range(4):
                values[i] += gradients[i][x][y]*state[x][y]
    return max(values)

"""
Returns the heuristic value of all heuristic functions combined multiplied by
their weights
"""
def heuristic_value(state):
    smooth, empty, mono, max, corner = heuristic_weights
    sum = 0
    sum += smoothness(state) * smooth
    if len(empty_tiles(state)) != 0:
        sum += math.log(len(empty_tiles(state))) * empty
    sum += monotonicity(state) * mono
    sum += max_tile(state) * max
    sum += getBoardValue2(state) * corner
    return sum

"""
Returns the smoothness penalty of a board
"""
def smoothness(state):
    smoothness = 0
    for x in range(4):
        for y in range(4):
            if state[x][y] != 0:
                value = math.log(state[x][y] / math.log(2))
                for direction in range(1,3):
                    (targetloc, target) = find_next_tile(state, x, y, direction)
                    targetValue = math.log(target) / math.log(2)
                    smoothness -= abs(value - targetValue)

    return smoothness

"""
Returns the monotonicity penalty of a board
"""
def monotonicity(state):
    up = 0.
    down = 0.
    left = 0.
    right = 0.
    boardArray = numpy.array(state)
    #up
    current = 0
    next = current + 1
    for x in range(3):
        while next < 3 and state[x][next] == 0:
            next += 1
        next = next - 1 if next >=4 else next
        currentValue = math.log(state[x][current]) / math.log(2) if state[x][current] !=0 else 0
        nextValue = math.log(state[x][next]) / math.log(2) if state[x][next] !=0 else 0
        if (currentValue > nextValue):
            up += nextValue - currentValue
        current = next
        next += 1

    #down
    current = 0
    next = current + 1
    for x in reversed(range(3)):
        while next < 3 and state[x][next] == 0:
            next += 1
        next = next - 1 if next >=4 else next
        currentValue = math.log(state[x][current]) / math.log(2) if state[x][current] !=0 else 0
        nextValue = math.log(state[x][next]) / math.log(2) if state[x][next] !=0 else 0
        if (nextValue > currentValue):
            down += currentValue - nextValue
        current = next
        next += 1

    #right
    current = 0
    next = current + 1
    for y in range(3):
        while next < 3 and state[next][y] == 0:
            next += 1
        next = next - 1 if next >=4 else next
        currentValue = math.log(state[current][y]) / math.log(2) if state[current][y] !=0 else 0
        nextValue = math.log(state[next][y]) / math.log(2) if state[next][y] !=0 else 0
        if (currentValue > nextValue):
            right += nextValue - currentValue
        current = next
        next += 1

    #left
    current = 0
    next = current + 1
    for y in reversed(range(3)):
        while next < 3 and state[next][y] == 0:
            next += 1
        next = next - 1 if next >=4 else next
        currentValue = math.log(state[current][y]) / math.log(2) if state[current][y] !=0 else 0
        nextValue = math.log(state[next][y]) / math.log(2) if state[next][y] !=0 else 0
        if (nextValue > currentValue):
            left += currentValue - nextValue
        current = next
        next += 1

    return max(up, down) + max(left, right)

"""
Returns the max tile value of a board
"""
def max_tile(state):
    max = 0
    for x in range(4):
        for y in range(4):
            if state[x][y] > max:
                max = state[x][y]
    return max
