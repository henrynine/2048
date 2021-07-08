import board, heuristics, operator, getch, os, bitboard, time, sys
from functools import lru_cache
from collections import Counter

"""
Give the expected value of state, running the algorithm down to the given
depth. Also return the move direction that produces the best value
"""
# imp is the implementation to run with – bitboard or board
@lru_cache(maxsize=1000000)
def expectimax(state, depth, imp):
  if imp.game_over(state):
    # return 0 - non-game over states are boosted by the loss penalty
    return (0, None)
  if depth == 0:
    # return the heuristic value for the given state and no direction
    return (imp.heuristic_value(state), None)

  else:
    # do expected value of all children and multiply by the odds of reaching
    # that child

    ev = {}

    for dir in ["L", "R", "U", "D"]:
      res, _ = imp.move(state, dir)
      if imp.equal(res, state):
        # set the reward for making no move at all to be -infinity
        # this is necessary because the heuristics can give a negative
        # number as an evaluation
        ev[dir] = float("-inf")
        continue
      # sub_evs is a list of the expected values of the children times the odds
      # of that node being reached
      sub_evs = []
      empties = imp.empty_tiles(res)
      for empty_tile in empties:
        # 0.1 - odds of a 4
        # 0.9 - odds of a 2
        sub_evs.append(0.9/len(empties) * expectimax(imp.spawn_manual(res, 2, empty_tile), depth - 1, imp)[0])
        sub_evs.append(0.1/len(empties) * expectimax(imp.spawn_manual(res, 4, empty_tile), depth - 1, imp)[0])
      ev[dir] = sum(sub_evs)

    # TODO might be better to calculate state value based on average value of
    # all possible moves, not the value of the best possible move – not sure
    argmax = max(ev.items(), key = operator.itemgetter(1))[0]
    return ev[argmax], argmax
