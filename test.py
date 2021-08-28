import board
main = board.new_board()
main = board.spawn_tile_2(main, 0, 0)
main = board.spawn_tile_2(main, 0, 1)
main,_ = board.move(main, 'L')
print(board.string_of_board(main))
