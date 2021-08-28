import numpy, board, getch, os, math, copy, numpy, expectimax, minimax, \
       heuristics, bitboard
from geneticalgorithm import geneticalgorithm as ga
# from functools import lru_cache

# @lru_cache(maxsize=1000000)
def f(X):
    main = bitboard.new_board()
    total_score = 0
    for n in range(2): main = bitboard.spawn_tile(main)

    bitboard.init(weights=X)

    while not bitboard.game_over(main):
        _, move = expectimax.expectimax(main, 1, bitboard)

        img,score_inc = bitboard.move(main, move)

        # print(board.string_of_board(main))
        # print("Score: " + str(total_score))

        # if no change happened, don't update the score or try to spawn a tile
        if bitboard.equal(img, main): continue

        main = img

        total_score += score_inc
        main = bitboard.spawn_tile(main)

    print(total_score)
    return -total_score

algorithm_param = {'max_num_iteration': 2,\
                   'population_size':3,\
                   'mutation_probability':0.1,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.5,\
                   'parents_portion': 0.3,\
                   'crossover_type':'uniform',\
                   'max_iteration_without_improv':None}

varbound = numpy.array([[0,10],[0,100],[0,100],[0,100],[0,1000],[0,1000],[0,500000]])
model=ga(function=f,dimension=7,variable_type='real',variable_boundaries=varbound,function_timeout=600,algorithm_parameters=algorithm_param)
model.run()

convergence=model.report
solution=model.output_dict
print(solution)
