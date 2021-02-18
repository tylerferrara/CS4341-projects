import math
import agent

###########################
# Alpha-Beta Search Agent #
###########################

# OPTOMIZED means we tuned the values to be the best we could

class AlphaBetaAgent(agent.Agent):
    """Agent that uses alpha-beta search"""

    # Class constructor.
    #
    # PARAM [string] name:      the name of this player
    # PARAM [int] max_depth: the maximum search depth
    # PARAM [int] to_win: number of pieces in a row to win
    # PARAM [bool] isPlayer1: true if the AI is player 1
    def __init__(self, name, max_depth, to_win):
        super().__init__(name)
        # Max search depth
        self.max_depth = max_depth
        # Num of pieces in a row to win
        self.to_win = to_win
        self.player = 0

        # UN-TUNED VALUES
        # ====================================
        self.TRAP_BONUS = 900
        self.N_IN_A_ROW_SCALAR = 1
        self.WINNING_BONUS = 1000
        self.DEFENSE_RATIO = 1 # 0.5 - very defensive, 1 - weight wins the same

        # TUNED VALUES
        # ====================================
        self.MID_SCALAR = 25


    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        """Search for the best move (choice of column for the token)"""

        # find opponent token
        if self.player == 0:
            self.player = self.find_player(brd)

        return self.find_best_column(brd)

    # Get the successors of the given board.
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [list of (board.Board, int)]: a list of the successor boards,
    #                                      along with the column where the last
    #                                      token was added in it
    def get_successors(self, brd):
        """Returns the reachable boards from the given board brd. The return value is a tuple (new board state, column number where last token was added)."""
        # Get possible actions
        freecols = brd.free_cols()
        # Are there legal actions left?
        if not freecols:
            return []
        # Make a list of the new boards along with the corresponding actions
        succ = []
        for col in freecols:
            # Clone the original board
            nb = brd.copy()
            # Add a token to the new board
            # (This internally changes nb.player, check the method definition!)
            nb.add_token(col)
            # Add board to list of successors
            succ.append((nb,col))
        return succ

    # use the minimax algorithm to choose the best column to add to
    #
    # PARAM  [board.Board] brd: the current board state
    # RETURN [int]: index of the column to add a the next move
    #
    def find_best_column(self, brd):
        val = float('-inf')
        move = -1
        for child in self.get_successors(brd):
            next_brd = child[0]
            next_move = child[1]
            found_val = self.minimax(next_brd, self.max_depth, False, next_move)
            # PRIORITIZE THE MIDDLE OF THE BOARD
            #
            #   NOTE: This may not belong here...
            #   It may be better to:
            #       - count 1-in-a-row and multiply them by this scalar
            #
            #
            found_val = found_val + self.col_midpoint_scalar(next_move, brd.w-1)
            if found_val > val:
                val = found_val
                move = next_move
        return move

    # minimax algorithm to be called by go
    #
    # PARAM  [board.Board] brd: the board state
    # PARAM  [int] depth: the max depth of recursive calls
    # PARAM  [bool] max_node: determins if max or min node
    # PARAM  [int] col: column chosen to place last piece
    # RETURN [float]: value of given decision tree
    #
    def minimax(self, brd, depth, max_node, col):
        # is the game over?
        if depth == 0 or len(brd.free_cols()) == 0 or brd.get_outcome() != 0:
            e = self.evaluate(brd, col)
            # brd.print_it()
            # print(e)
            res = e
            return res
        # max
        if max_node:
            v = float('-inf')
            for child in self.get_successors(brd):
                res = self.minimax(child[0], depth-1, False, child[1])
                v = max(v, res)
            return v
        # min
        v = float('inf')
        for child in self.get_successors(brd):
            res = self.minimax(child[0], depth-1, True, child[1])
            v = min(v, res)
        return v

    # scores a given board counting n_in_a_row, wins, and traps
    #
    # PARAM  [board.Board] brd: the game board
    # PARAM  [int] col: column of last move 
    # RETURN [float]: score of the board (in respect to the AI's positon)
    #
    def evaluate(self, brd, col):
        # NOTE: TRAP_SCALAR is used within num_in_a_row.
        #       it will be combined with the win_bonus. This may not be helpful
        #       if an opponent set a trap but the AI can win the game
        #
        #
        score = self.num_in_a_row(brd)

        if brd.get_outcome != 0:
            score = score + self.win_bonus(brd)
            # LOOK FOR TRAPS
            for y in reversed(range(brd.h)):
                if brd.board[y][col] != 0:
                    win_coord = [col, y]
                    if self.is_trap(brd, win_coord):
                        score = score + self.TRAP_BONUS
                    break

        return score
    
    # add a win bonus, prioritizing the opponent, in order to play deffensively
    #
    # PARAM  [board.Board] brd: the game board
    # RETURN [int]: bonus value for winning the game
    #
    def win_bonus(self, brd):
        outcome = brd.get_outcome()
        if self.player == outcome:
            return self.WINNING_BONUS * self.DEFENSE_RATIO
        elif outcome != 0:
            return -1 * self.WINNING_BONUS
        else:
            return 0

    # score the number of n_in_a_row with parabolic scalar
    # 
    # PARAM  [board.Board] brd: the game board
    # RETURN [float] score of board peices (self - opponent)
    #  
    def num_in_a_row(self, brd):
        # each points[i] is number of occurances with i+1 in a row
        my_points = [0 for _ in range(self.to_win)]
        op_points = [0 for _ in range(self.to_win)]
        
        # horizontal
        h_found = self.count_horizontal(brd, self.player, self.to_win)
        # vertical
        v_found = self.count_vertical(brd, self.player, self.to_win)
        # diagnal
        x_found = self.count_diagnal(brd, self.player, self.to_win)

        for p_idx, _ in enumerate(h_found[0]):
            my_points[p_idx] = my_points[p_idx] + h_found[0][p_idx] + v_found[0][p_idx] + x_found[0][p_idx] 
            op_points[p_idx] = op_points[p_idx] + h_found[1][p_idx] + v_found[1][p_idx] + x_found[1][p_idx]

        # count points
        result = 0
        for i, v in enumerate(my_points):
            result = result + (v * self.quad_scalar(i+1))
            result = result - (op_points[i] * self.quad_scalar(i+1))
        return result
    
    # find the number of n horizontal pieces for player1 and player2
    #
    # PARAM [board.Board] brd: game board
    # PARAM [int] piece: number to find in a row within the board
    # PARAM [int] to_win: number of pieces in a row to win the game
    # RETURN [list of [list of int]]: value at each index is number of n=(index+1) in a row
    #                                first array is my pieces, second array is opponent's pieces
    def count_horizontal(self, brd, piece, to_win):
        # create array only as large as num_to_win
        # rational: we don't care about counting 4 in a rows
        # if it only takes 2 in a row to win
        #
        # NOTE: tokens in a row > num_to_win will cound as num_to_win
        #
        my_res = [0 for _ in range(to_win)]
        op_res = [0 for _ in range(to_win)]
        empty = True
        for y, row in enumerate(brd.board):
            me = 0
            op = 0
            for x, token in enumerate(row):
                if token == piece:
                    empty = False
                    me = me + 1
                    self.add_to_points_list(op_res, op, [x, y], brd)
                    op = 0
                elif token != 0:
                    empty = False
                    op = op + 1
                    self.add_to_points_list(my_res, me, [x, y], brd)
                    me = 0
                else:
                    self.add_to_points_list(op_res, op, [x, y], brd)
                    self.add_to_points_list(my_res, me, [x, y], brd)
                    op = 0
                    me = 0
            if empty:
                break
            else:
                empty = True
                self.add_to_points_list(op_res, op, [x, y], brd)
                self.add_to_points_list(my_res, me, [x, y], brd)
        
        return [my_res, op_res]
    
    # find the number of n vertical pieces for player1 and player2
    #
    # PARAM [board.Board] brd: game board
    # PARAM [int] piece: number to find in a row within the board
    # PARAM [int] to_win: number of pieces in a row to win the game
    # RETURN [list of [list of int]]: value at each index is number of n=(index+1) in a row
    #       
    def count_vertical(self, brd, piece, to_win):
        my_res = [0 for _ in range(to_win)]
        op_res = [0 for _ in range(to_win)]
        col_idx = 0
        while col_idx < brd.w:
            x = col_idx
            me = 0
            op = 0
            for row_idx in range(brd.h):
                y = row_idx
                token = brd.board[row_idx][col_idx]
                if token == piece:
                    me = me + 1
                    self.add_to_points_list(op_res, op, [x, y], brd)
                    op = 0
                elif token != 0:
                    op = op + 1
                    self.add_to_points_list(my_res, me, [x, y], brd)
                    me = 0
                else:
                    self.add_to_points_list(op_res, op, [x, y], brd)
                    self.add_to_points_list(my_res, me, [x, y], brd)
                    me = 0
                    op = 0
                    break

            self.add_to_points_list(op_res, op, [x, y], brd)
            self.add_to_points_list(my_res, me, [x, y], brd)
            col_idx = col_idx + 1

        return [my_res, op_res]

    # find the number of n diagnal pieces for player1 and player2
    #
    # PARAM [board.Board] brd: game board
    # PARAM [int] piece: number to find in a row within the board
    # PARAM [int] to_win: number of pieces in a row to win the game
    # RETURN [list of [list of int]]: value at each index is number of n=(index+1) in a row
    #     
    def count_diagnal(self, brd, piece, to_win):
        # top left to bottom right
        my_res = [0 for _ in range(to_win)]
        op_res = [0 for _ in range(to_win)]
        for top_left_x in range((-1*brd.h)-1, brd.w):
            top_left_y = 0

            x = top_left_x
            y = top_left_y
            me = 0
            op = 0
            while y < brd.h:
                if x >= 0 and x < brd.w:
                    token = brd.board[y][x]
                    if token == piece:
                        me = me + 1
                        self.add_to_points_list(op_res, op, [x, y], brd)
                        op = 0
                    elif token != 0:
                        op = op + 1
                        self.add_to_points_list(my_res, me, [x, y], brd)
                        me = 0
                    else:
                        self.add_to_points_list(op_res, op, [x, y], brd)
                        self.add_to_points_list(my_res, me, [x, y], brd)
                        me = 0
                        op = 0
                # iterate
                x = x + 1
                y = y + 1
            # add last row
            self.add_to_points_list(op_res, op, [x-1, y-1], brd)
            self.add_to_points_list(my_res, me, [x-1, y-1], brd)
        # top right to bottom left
        for top_left_x in range(0, brd.w + brd.h - 1):
            top_left_y = 0

            x = top_left_x
            y = top_left_y
            me = 0
            op = 0
            while y < brd.h:
                if x >= 0 and x < brd.w:
                    token = brd.board[y][x]
                    if token == piece:
                        me = me + 1
                        self.add_to_points_list(op_res, op, [x, y], brd)
                        op = 0
                    elif token != 0:
                        op = op + 1
                        self.add_to_points_list(my_res, me, [x, y], brd)
                        me = 0
                    else:
                        self.add_to_points_list(op_res, op, [x, y], brd)
                        self.add_to_points_list(my_res, me, [x, y], brd)
                        me = 0
                        op = 0
                # iterate
                x = x - 1
                y = y + 1
            # add last row
            self.add_to_points_list(op_res, op, [x+1, y-1], brd)
            self.add_to_points_list(my_res, me, [x+1, y-1], brd)
        
        return [my_res, op_res]

    # helper function to num_in_a_row which adds 1 to the value at the index of point-1
    # NOTE: This will neglect point values of 1
    #
    # PARAM  [list of int] lst: number of n in a row at index = n-1
    # PARAM  [int] point: longest re-occurance of peices found in a arow
    # PARAM  [[x int, y int]] coords: coordinates of point
    # PARAM  [board.Board] brd: the game board
    #
    def add_to_points_list(self, lst, point, coords, brd):
        if point > 1 and len(lst) != 0:
            t_scalar = 1
            if point >= len(lst):
                point = len(lst)

            lst[point-1] = (lst[point-1] + 1) * t_scalar
            
    # returns True if a trap is found
    #
    # PARAM  [board.Board] brd: the game board
    # PARAM  [x int, y int] coords: x and y coordnates of a winning line
    # RETURN [bool]: True if a trap is found
    #
    def is_trap(self, brd, coords):
        piece = brd.board[coords[1]][coords[0]]
        seen = {str(coords[0]) + "," + str(coords[1]): True}           # dictionary of coords seen
        stack = [coords]    # stack for new coords to visit

        while len(stack) > 0:
            coord = stack.pop()
            x, y = coord[0], coord[1]
            key = str(x) + "," + str(y)
            seen[key] = True
            # look for a trap
            #
            #   checking above and below for a near win
            #
            return ((y + 1 < brd.h and self.missing_one_from_win(brd, [x,y+1], piece)) or
                    (y - 1 >= 0 and self.missing_one_from_win(brd, [x,y-1], piece)))

    # finds if a horizontal or diagnal line exists where n_in_row + 1 >= to_win
    # NOTE: This niglects counting the coord given
    #
    # PARAM  [board.Board] brd: the game board
    # PARAM  [[x int, y int]] coord: x and y coordinate to look for line
    # PARAM  [int] piece: piece to count for line
    # RETURN [bool]: True if n_in_row + 1 >= to_win with given piece
    #
    def missing_one_from_win(self, brd, coord, piece):
        x, y = coord[0], coord[1]
        
        # horizontal
        seen = 0
        right = 0

        for n_x in range(x+1, brd.w):
            if n_x < brd.w and brd.board[y][n_x] == piece:
                right = right + 1
            else:
                break
        seen = seen + right
        left = 0
        for n_x in reversed(range(0, x)):
            if n_x >= 0 and brd.board[y][n_x] == piece:
                left = left + 1
            else:
                break
        seen = seen + left

        if seen + 1 >= self.to_win:
            return True
        
        # diaginal
        seen = 0
        # top left to bottom right
        # left
        left = 0
        n_x, n_y = x-1, y-1
        while n_x >= 0 and n_y >= 0:
            if brd.board[n_y][n_x] == piece:
                left = left+1
            else:
                break
            n_x, n_y = n_x-1, n_y-1
        seen = seen + left
        right = 0
        n_x, n_y = x+1, y+1
        while n_x < brd.w and n_y < brd.h:
            if brd.board[n_y][n_x] == piece:
                right = right+1
            else:
                break
            n_x, n_y = n_x+1, n_y+1
        seen = seen + right

        if seen + 1 >= self.to_win:
            return True
        
        # top right to bottom left
        left = 0
        n_x, n_y = x-1, y+1
        while n_x >= 0 and n_y < brd.h:
            if brd.board[n_y][n_x] == piece:
                left = left+1
            else:
                break
            n_x, n_y = n_x-1, n_y+1
        seen = seen + left
        right = 0
        n_x, n_y = x+1, y-1
        while n_x < brd.w and n_y >= 0:
            if brd.board[n_y][n_x] == piece:
                right = right+1
            else:
                break
            n_x, n_y = n_x+1, n_y-1
        seen = seen + right

        # last try to find win
        return seen + 1 >= self.to_win

    # ********** CURRENTLY NOT BEING USED **********
    # 
    # returns all coordinates of neighbors surrounding the given coordinate
    #
    # PARAM  [board.Board] brd: the game board
    # PARAM  [[x int, y int]] coords: x and y coordinate to find the neighbors of
    # RETURN [list of [x int, y int]]: list of neighbor coordinates
    #
    def get_neighbor_coords(self, brd, coords):
        x = coords[0]
        y = coords[1]
        n = [
            [x-1,y-1],  # top left
            [x,y-1],    # top
            [x+1,y-1],  # top right
            [x+1,y],    # right
            [x+1,y+1],  # bot right
            [x,y+1],    # bot
            [x-1,y+1],  # bot left
            [x-1,y],    # left
        ]
        res = []
        for c in n:
            if c[0] >= 0 and c[0] < brd.w and c[1] >= 0 and c[1] < brd.h:
                res.append(c)
        return res

    # equation used to value larger n_in_a_row occurances exponentially greater
    #
    # PARAM  [int] x: n_in_a_row
    # RETURN [float]: scalar value used to weigh number of occurances of n_in_a_row
    #
    def quad_scalar(self, x):
        return self.N_IN_A_ROW_SCALAR * x*x*x/self.to_win
    
    # OPTIMIZED
    # equation to prioritize the middle of the board
    # 
    # PARAM  [int] col: the column of the next move
    # PARAM  [int] last_col: the last column available to move to
    # RETURN [float]: scalar value prioritizing the middle of the board
    #
    def col_midpoint_scalar(self, col, last_col):
        return self.MID_SCALAR * ((-1 * col * col) + (last_col * col))
        
    # run once at the first move of the agent, finding which piece to place
    # [PARAM] brd: board from game
    # [int]: which player the AI is playing as
    #
    def find_player(self, brd):
        for row in brd.board:
            for col in row:
                if col != 0:
                    return 2
        return 1