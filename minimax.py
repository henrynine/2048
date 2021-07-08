import board, getch, os, math, copy, numpy, heuristics, bitboard
from functools import lru_cache

@lru_cache(maxsize = 1000000)
def maximize(state, d, alpha, beta, imp):
    # print("max at depth " + str(d))
    bestChild = None
    maxValue = float("-inf")
    minbest = None

    if imp.game_over(state):
        return (None, 0, None)

    if d == 0:
        return (None, imp.heuristic_value(state), None)

    d = d - 1

    for x in ['L', 'R', 'U', 'D']:
        newboard = copy.deepcopy(state)
        img,_ = imp.move(newboard, x)
        if not imp.equal(img, newboard):
            (minMove, newValue) = minimize(img, d, alpha, beta, imp)
            if newValue > maxValue:
                maxValue = newValue
                bestChild = x
                minbest = minMove
            if maxValue >= beta:
                break
            if maxValue > alpha:
                alpha = maxValue

    return (bestChild, maxValue, minbest)

@lru_cache(maxsize = 1000000)
def minimize(state, d, alpha, beta, imp):
    # print("min at depth " + str(d))
    bestChild = None
    minValue = float("inf")
    bestNum = 0
    if imp.game_over(state):
        return (None, 0)

    if d == 0:
        return (None, imp.heuristic_value(state))

    d = d - 1

    empty_tiles = imp.empty_tiles(state)
    for loc in empty_tiles:
        for i in range(1,3):
            newboard = copy.deepcopy(state)
            if i == 1:
                newboard = imp.spawn_manual(newboard, 2, loc)
            else:
                newboard = imp.spawn_manual(newboard, 4, loc)
            (_, newValue, _) = maximize(newboard, d, alpha, beta, imp)
            if newValue < minValue:
                minValue = newValue
                bestChild = (loc, (i * 2))
            if minValue <= alpha:
                break
            if minValue < beta:
                beta = minValue

    return (bestChild, minValue)
