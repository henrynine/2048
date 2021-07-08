import bitboard, getch, os, minimax, expectimax, sys, random, board

directions = {
  'w': "U",
  'a': "L",
  's': "D",
  'd': "R"
}

# run an iteration of the game until it ends in the given mode
def run_iteration(mode, imp, depth, prints = True, debug = False):
  main = imp.new_board()
  total_score = 0
  for n in range(2): main = imp.spawn_tile(main)

  move_count = 0

  try:
    while not imp.game_over(main):

      if prints:
        os.system('clear')
        print(imp.string_of_board(main))
        print("Score: " + str(total_score))
        if debug:
          print("Board heuristic score: ", str(imp.heuristic_value(main)))

      if mode == "minimax_random" or mode == "minimax_antagonistic":
        (move, _, min_input) = minimax.maximize(main, depth, -float("-inf"), float("inf"), imp)
      elif mode == "expectimax":
        _, move = expectimax.expectimax(main, depth, imp)
      elif mode == "random":
        move = random.choice(["L", "R", "U", "D"])
      elif mode == "manual":
        m = getch.getch()
        while m not in ['w', 'a', 's', 'd']:
          m = getch.getch()
        move = directions[m]

      img,score_inc = imp.move(main, move)

      # if no change happened, don't update the score or try to spawn a tile
      if imp.equal(img, main):
        continue

      main = img
      move_count += 1

      total_score += score_inc
      if mode == "minimax_antagonistic":
        if min_input[1] == 2:
          main = imp.spawn_manual(img, 2, min_input[0])
        else:
          main = imp.spawn_manual(img, 4, min_input[0])
      else:
        main = imp.spawn_tile(main)

  finally:
    if prints:
      print("\r\n")
      print(imp.string_of_board(main))

  if prints:
    print("\r\n")

  return main, move_count, total_score, imp.max_tile(main)

if __name__ == "__main__":
  print("Loading game...")

  bitboard.init()

  print("Welcome to 2048!")
  print("Options: ")
  print("w: play manually")
  print("r: use a minimax strategy with random spawning")
  # Right now, the minimax strategy makes the best move assuming the spawning
  # of tiles will be malicious, but the spawning is still random. It could be
  # cool to add modes where either the player plays against a malicious AI
  # or watches two AIs battle it out.
  print("a: use a minimax strategy with antagonistic spawning")
  print("e: use an expectimax strategy")

  c = ''
  while c not in ['w', 'm', 'e', 'r', 'a']:
    c = getch.getch()
    if c == 'w':
      mode, depth = ("manual", 0)
    elif c == 'r':
      mode, depth = ("minimax_random", 7)
    elif c == 'a':
      mode, depth = ("minimax_antagonistic", 7)
    elif c == 'e':
      mode, depth = ("expectimax", 3)

  main, _, total_score, _ = run_iteration(mode, bitboard, depth)

  os.system('clear')
  print("Game over:")
  print(bitboard.string_of_board(main))
  print("Final score: " + str(total_score))
