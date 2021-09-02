# 2048 AI

We built an implementation of 2048 and used expectimax and minimax to try to maximize the game score. An in-depth description of our approach and results can be found in details.pdf.

Created by [Henry Middleton](github.com/henrynine) and [CJ Schmidt](github.com/conzwrath).


## Installation

To run the game, first install the required libraries:

`pip install -r requirements.txt`

## Usage

To play a game or watch the AI work, run `client.py`. For manual play, use WASD to move.
The speed of different game strategies and implementations can be compared with `timing.py`:

`python3 timing.py [mode] [run_count] [implementation] [depth]`

The available modes are:

* minimax_random
* minimax_antagonistic
* expectimax
* random

And the available implementations are:

* board
* bitboard
