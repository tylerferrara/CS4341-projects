import random
import game
import agent
import alpha_beta_agent as aba
import trap_alpha_beta_agent as taba

# Set random seed for reproducibility
random.seed(1)

#
# Random vs. Random
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.RandomAgent("random1"),       # player 1
#               agent.RandomAgent("random2"))       # player 2

#
# Human vs. Random
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human"),    # player 1
#               agent.RandomAgent("random"))        # player 2

#
# Random vs. AlphaBeta
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.RandomAgent("random"),        # player 1
#               aba.AlphaBetaAgent("alphabeta", 4)) # player 2

#
# Human vs. AlphaBeta
#
depth = 7
to_win = 4
g = game.Game(7, # width
              6, # height
              to_win, # tokens in a row to win
              agent.InteractiveAgent("human"),    # player 1
              taba.TrapAlphaBetaAgent("trap_5", depth, 6, 10, 1, 800, 0.85, 0))
#
# Human vs. Human
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human1"),   # player 1
#               agent.InteractiveAgent("human2"))   # player 2

# Execute the game
outcome = g.go()
