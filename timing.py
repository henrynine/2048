import time, minimax, expectimax, board, random, bitboard, itertools, \
       heuristics, timeit, functools, client, sys
from collections import Counter

def test_all_boards(boards):
  for b in boards:
    # print("\n\n\n")
    # print(b)
    # print("\n\n\n")
    # print(board.string_of_board(b))
    # print("\n\n\n")

    h = heuristics.heuristicValue(b, 73.43918545, 12.22572185, 28.88739512, 54.09755752, 18.12526243)

def test_all_bitboards(boards):
  for b in boards:
    h = bitboard.heuristic_value(b)

# convert a bit board to a 2d list board
def bit_to_list(b):
  new_b = []
  while b:
    row = []
    b_row = b & 0xFFFF
    while b_row:
      row.insert(0, 2**(b_row & 0xF))
      b_row >>= 4
    while len(row) < 4:
      row.insert(0, 0)
    new_b.insert(0, row)
    b >>= 16
  while (len(new_b)) < 4:
    new_b.insert(0, [0 for x in range(4)])
  return new_b

# Necessary because a 64 bit int is too large for base python random
def random_bit_board():
  res = 0
  for offset in (0, 16, 32, 48):
    res |= (random.choice(range(0xFFFF + 1)) << offset)
  return res

def test_heuristics_all_rows(nboards):
  bitboard.init()
  # generate n random boards
  bit_bs = [random_bit_board() for n in range(nboards)]
  og_bs = list(map(bit_to_list, bit_bs))
  bit_time = timeit.timeit(lambda: test_all_bitboards(bit_bs), number = 1)
  og_time = timeit.timeit(lambda: test_all_boards(og_bs), number = 1)
  print("Original time: ", str(og_time))
  print("Bit time: ", str(bit_time))

def time_runs(mode, run_count, imp, depth):
  imp.init()

  res = []
  start = time.time()
  for n in range(run_count):
    main, moves, t, m = client.run_iteration(mode, imp, depth, prints = False)
    end = time.time() - start
    res.append([moves, t, end, imp.max_tile(main)])
    print("Iteration ", str(n+1), " complete...")
    start = time.time()

  maxes = [x[3] for x in res]
  total_time = sum([x[2] for x in res])
  total_score = sum([x[1] for x in res])
  total_moves = sum([x[0] for x in res])

  print("Ran ", str(run_count), " ", mode, " games in ", round(total_time, 2), " seconds.")
  print("Average moves/sec: ", round(total_moves/total_time, 2))
  print("Average final score: ", round(total_score/run_count, 2))
  print("Max final tile distribution:")

  occs = Counter(maxes)

  for v in sorted(occs.keys(), reverse = True):
    print("  * ", str(v), ": ", occs[v])

  return res

if __name__ == "__main__":
  if len(sys.argv) != 5:
    print("Usage: timing.py [mode] [run_count] [implementation] [depth]")
  else:
    imp = (board if sys.argv[3] == "board" else bitboard)
    time_runs(sys.argv[1], int(sys.argv[2]), imp, int(sys.argv[4]))
