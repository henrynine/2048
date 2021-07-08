import board, getch, os, math, copy, numpy

"""
Returns the board value as sum of all tiles / # of non-0 tiles
"""
def getBoardValue(state):
    sum = 0
    for x in range(4):
        for y in range(4):
            sum = sum + state[x][y]
    return sum / (16 - len(board.empty_tiles(state)))

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
def heuristicValue(state, smooth, empty, mono, max, corner):
    sum = 0
    sum += smoothness(state) * smooth
    if len(board.empty_tiles(state)) != 0:
        sum += math.log(len(board.empty_tiles(state))) * empty
    sum += monotonicity(state) * mono
    sum += maxTile(state) * max
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
                    (targetloc, target) = board.find_next_tile(state, x, y, direction)
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
def maxTile(state):
    max = 0
    for x in range(4):
        for y in range(4):
            if state[x][y] > max:
                max = state[x][y]
    return max
