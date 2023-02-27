import argparse
import copy
import sys
import time

cache = {} # you can use this to implement state caching!

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board):

        self.board = board

        self.width = 8
        self.height = 8
        self.single_jump = False
        self.multi_jump = False
        self.switched = False
        self.eval = 0
        self.parent = None

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

    def is_goal_max(self):
        '''Determine if board is a winner/goal state for r'''
        for i in range(self.height):
            if 'b' in self.board[i] or 'B' in self.board[i]:
                return False
            else:
                continue
        return True
    
    def is_goal_min(self):
        '''Determine if board is a winner/goal state for b'''
        for i in range(self.height):
            if 'r' in self.board[i] or 'R' in self.board[i]:
                return False
            else:
                continue
        return True
    
    def compute_utility(self, player):
        '''Determine player's utility of TERMINAL state'''
        # Return +inf for winner, -inf for loser
        if self.is_goal_max() == True:
            if player == 'r':
                return 100000
            else:
                return -100000
        elif self.is_goal_min() == True:
            if player == 'r':
                return -100000
            else:
                return 100000
        else:
            return 0

    def get_path(self):
        # Given the goal state is reached, backtrack using the parent values to determine solution path
        path = []
        count = 0
        while self.parent != None:
            path += [self.board]
            self = self.parent
            count += 1
        path += [self.board]
        # print(count)
        return path

    def eval_fnc(self, player):
        '''Estimate player's utility of NON TERMINAL state'''
        # Evaluate based on number of pieces player has vs the other player, as well as the 
        # number of player pieces that are more advanced on the board vs the other player and number of safe from capture pieces vs other player
        r = ['r', 'R']
        b = ['b', 'B']

        utility = self.compute_utility(player)
        eval = 0
        if utility == 100000 or utility == -100000:
            self.eval = utility
        else:
            for i in range(self.height):
                for j in range(self.width):
                    if i == 0 or i == 7 or j == 0 or j == 7:
                        # if at any of the safe from capture places (along edges)
                        if self.board[i][j] in r:
                            eval += 1
                            if self.board[i][j] == r[1]:
                                # King piece
                                eval += 2
                            elif self.board[i][j] == r[0]:
                                eval += 1
                        elif self.board[i][j] in b:
                            eval -= 1
                            if self.board[i][j] == b[1]:
                                # King piece
                                eval -= 2
                            elif self.board[i][j] == b[0]:
                                eval -= 1
                        
                        # Red: prefer in top half of board. Black: prefer at bottom half 
                        # if self.board[i][j] in r[0]:
                        #     eval += (7-i)
                        # elif self.board[i][j] in b[0]:
                        #     eval -= i                     

                    else:
                        # Not at edges
                        if self.board[i][j] == r[0]:
                            eval += 1
                        elif self.board[i][j] == r[1]:
                            eval += 2
                        elif self.board[i][j] == b[0]:
                            eval -= 1
                        elif self.board[i][j] == b[1]:
                            eval -= 2

                        # if self.board[i][j] in r[0]:
                        #     eval += (7-i)
                        # elif self.board[i][j] in b[0]:
                        #     eval -= i
            
            self.eval = eval

def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    '''Switch player turns'''
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def simulate_successors(state, turn, dec):
    '''Get successors for current state by generating successors and filtering them based on jumps'''
    
    successors_jump = []
    successors_multi_jumps = []

    successors = generate_successors(state, turn)
    if successors == []:
        return successors
    # Choose from possible successors
    # If we can jump, we must
    for successor in successors:
        if successor.single_jump == True:
            successors_jump.append(successor)
            if successor.multi_jump == True:
                successors_multi_jumps.append(successor)
    
    # If multi jump list is not empty, go with it. Else, if jump list is not empty, go with that list. Otherwise, stick to current successors list
    if successors_multi_jumps != []:
        successors = successors_multi_jumps
    elif successors_jump != []:
        successors = successors_jump
    
    # Node Ordering
    for successor in successors:
        successor.eval_fnc(turn)

    if dec == 'max':
        successors.sort(key=lambda x: x.eval, reverse=True)
    else:
        successors.sort(key=lambda x: x.eval)

    return successors

def generate_successors(state, curr_turn):
    '''Determine if particular movement (single move or jump(s)) are possible. If jumps are possible, it must be done.
    After the move check, move the piece and create a new board with the moved piece as a possible successor state'''
    successors = []
    if curr_turn == 'r':
        # Red begins on bottom 3 rows of board
        for i in range(state.height):
            if 'r' in state.board[i] or 'R' in state.board[i]:
                for j in range(state.width):
                    # Find position(s) in row with 'r'
                    if state.board[i][j] == '.':
                        continue
                    elif state.board[i][j] == 'r':
                        successors += move_check(state,j,i,'r')
                    elif state.board[i][j] == 'R':
                        successors += move_check(state,j,i,'R')
            else:
                # No red piece in current row
                continue

    elif curr_turn == 'b':
        # Black begins on top 3 rows of board
        for i in range(state.height):
            if 'b' in state.board[i] or 'B' in state.board[i]:
                for j in range(state.width):
                    # Find position(s) in row with 'r'
                    if state.board[i][j] == '.':
                        continue
                    elif state.board[i][j] == 'b':
                        successors += move_check(state,j,i,'b')
                    elif state.board[i][j] == 'B':
                        successors += move_check(state,j,i,'B')
            else:
                # No black piece in current row
                continue
    
    return successors

def move_check(state, x, y, player):
    '''Given the (x,y) coords of the piece of interest, see what moves are possible. If a jump is possible, use recursion within move function to check for multiple jumps
    and return a list of moves for the piece to make'''
    successors = []

    # initialization
    opps = get_opp_char(player)
    
    if player == 'r':
        # if player is 'r', guarantees that we are not at first row (since it'd be 'R')
        if x != 0:
            # if not at first column, check diagonal left
            if state.board[y-1][x-1] in opps:
                # check for jump left
                pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x-2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state 
            elif state.board[y-1][x-1] == '.':
                # left diagonal must be empty space
                successors += move_piece(state, (y,x), (y-1,x-1))
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y-1][x+1] in opps:
                # check for jump right
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y-1][x+1] == '.':
                # right diagonal must be empty space
                successors += move_piece(state, (y,x), (y-1,x+1))

    elif player == 'R' or player == 'B':
        if x == 0:
            # if R or B is in the first column
            if y == 0:
                # if R is also in the first row -- can only move down and to the right
                if state.board[y+1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y+2,x+2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y+1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x+1))
            elif y == 7:
                # if R is in last row -- can only move up and to the right
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y-2,x+2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y-1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x+1))
            else:
                # can move in two diagonal directions to the RIGHT
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y-2,x+2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y-1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x+1)) 

                if state.board[y+1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y+2,x+2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y+1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x+1))               

        elif x == 7:
            # if R is in the last column
            if y == 0:
                # if R is also in the first row -- can only move down and to the left
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y+2,x-2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y+1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x-1))
            elif y == 7:
                # if R is in last row -- can only move up and to the left
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y-2,x-2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y-1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x-1))
            else:
                # can move in two diagonal directions to the LEFT
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y-2,x-2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y-1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x-1)) 
                
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                    if pos_state != None and pos_state[0].switched == False:
                        multi_jump(pos_state, (y+2,x-2), successors)
                    elif pos_state != None and pos_state[0].switched == True:
                        successors += pos_state
                elif state.board[y+1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x-1))

        elif y == 0:
            # not in first or last column, but in top row -- can only move down in two directions
            if state.board[y+1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x-2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1)) 

            if state.board[y+1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1))

        elif y == 7:
            # not in first or last column, but in last row -- can only move up in two directions
            if state.board[y-1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x-2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1)) 

            if state.board[y-1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1))

        else:
            # at a position where the piece can move in any 4 directions
            # UP_LEFT
            if state.board[y-1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x-2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1)) 
            # UP_RIGHT
            if state.board[y-1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y-2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1))
            # DOWN_LEFT
            if state.board[y+1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x-2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1)) 
            # DOWN_RIGHT
            if state.board[y+1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1))
    
    elif player == 'b':
        # if player is 'b', guarantees that we are not at last row (since it'd be 'B')
        if x != 0:
            # if not at first column, check diagonal left
            if state.board[y+1][x-1] in opps:
                # check for jump left
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x-2), successors) 
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x-1] == '.':
                # left diagonal must be empty space
                successors += move_piece(state, (y,x), (y+1,x-1))
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y+1][x+1] in opps:
                # check for jump right
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None and pos_state[0].switched == False:
                    multi_jump(pos_state, (y+2,x+2), successors)
                elif pos_state != None and pos_state[0].switched == True:
                    successors += pos_state
            elif state.board[y+1][x+1] == '.':
                # right diagonal must be empty space
                successors += move_piece(state, (y,x), (y+1,x+1))

    return successors

def first_jump(state, piece_loc, move_loc, dir):
    '''Check if first jump can be made, if it can then complete the first jump'''
    # since diagonal piece is opponent, lets check if we can do another move in the same direction diagonally to complete jump
    switch = 0
    if dir == 'up_right':
        if move_loc[0] != 0 and move_loc[1] != 7:
            if state.board[move_loc[0]-1][move_loc[1]+1] == '.':
                # jump can be made 
                successor_board = copy.deepcopy(state.board)
                piece = successor_board[piece_loc[0]][piece_loc[1]]
                successor_board[piece_loc[0]][piece_loc[1]] = '.'
                # Opposing piece gets jumped
                successor_board[move_loc[0]][move_loc[1]] = '.'
                # Set new location
                if (move_loc[0]-1) == 0 and piece == 'r':
                    successor_board[move_loc[0]-1][move_loc[1]+1] = 'R'
                    switch = 1
                else:
                    successor_board[move_loc[0]-1][move_loc[1]+1] = piece
                new_state = State(successor_board)
                new_state.single_jump = True
                if switch == 1:
                    new_state.switched = True
                return [new_state]
            else:
                return None
    elif dir == 'up_left':
        if move_loc[0] != 0 and move_loc[1] != 0:
            if state.board[move_loc[0]-1][move_loc[1]-1] == '.':
                # jump can be made 
                successor_board = copy.deepcopy(state.board)
                piece = successor_board[piece_loc[0]][piece_loc[1]]
                successor_board[piece_loc[0]][piece_loc[1]] = '.'
                # Opposing piece gets jumped
                successor_board[move_loc[0]][move_loc[1]] = '.'
                # Set new location
                if (move_loc[0]-1) == 0 and piece == 'r':
                    successor_board[move_loc[0]-1][move_loc[1]-1] = 'R'
                    switch = 1
                else:
                    successor_board[move_loc[0]-1][move_loc[1]-1] = piece
                new_state = State(successor_board)
                new_state.single_jump = True
                if switch == 1:
                    new_state.switched = True
                return [new_state]
            else:
                return None

    elif dir == 'down_right':
        if move_loc[0] != 7 and move_loc[1] != 7:
            if state.board[move_loc[0]+1][move_loc[1]+1] == '.':
                # jump can be made 
                successor_board = copy.deepcopy(state.board)
                piece = successor_board[piece_loc[0]][piece_loc[1]]
                successor_board[piece_loc[0]][piece_loc[1]] = '.'
                # Opposing piece gets jumped
                successor_board[move_loc[0]][move_loc[1]] = '.'
                # Set new location
                if (move_loc[0]+1) == 7 and piece == 'b':
                    successor_board[move_loc[0]+1][move_loc[1]+1] = 'B'
                    switch = 1
                else:
                    successor_board[move_loc[0]+1][move_loc[1]+1] = piece
                new_state = State(successor_board)
                new_state.single_jump = True
                if switch == 1:
                    new_state.switched = True
                return [new_state]
            else:
                return None
    elif dir == 'down_left':
        if move_loc[0] != 7 and move_loc[1] != 0:
            if state.board[move_loc[0]+1][move_loc[1]-1] == '.':
                # jump can be made 
                successor_board = copy.deepcopy(state.board)
                piece = successor_board[piece_loc[0]][piece_loc[1]]
                successor_board[piece_loc[0]][piece_loc[1]] = '.'
                # Opposing piece gets jumped
                successor_board[move_loc[0]][move_loc[1]] = '.'
                # Set new location
                if (move_loc[0]+1) == 7 and piece == 'b':
                    successor_board[move_loc[0]+1][move_loc[1]-1] = 'B'
                    switch = 1
                else:
                    successor_board[move_loc[0]+1][move_loc[1]-1] = piece
                new_state = State(successor_board)
                new_state.single_jump = True
                if switch == 1:
                    new_state.switched = True
                return [new_state]
            else:
                return None

def multi_jump(state, piece_loc, successors):
    '''Take a state that has just done one jump and recursively do more if possible'''
    state = state[0]
    piece = state.board[piece_loc[0]][piece_loc[1]]
    x = piece_loc[1]
    y = piece_loc[0]
    opps = get_opp_char(piece)
    failed = 0

    if piece == 'r':
        # UP_LEFT
        if (x-2) >= 0 and (y-2) >= 0:
            if state.board[y-1][x-1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if new_state != None:
                    # multi jump successful
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y-2,x-2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # UP_RIGHT
        if (x+2) <= 7 and (y-2) >= 0:
            if state.board[y-1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y-2,x+2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1

        if failed == 2:
            successors += [state]
            return [state]
        else:
            return [state]
   
    elif piece == 'R' or piece == 'B':
        # UP_LEFT
        if (x-2) >= 0 and (y-2) >= 0:
            if state.board[y-1][x-1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y-2,x-2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # UP_RIGHT
        if (x+2) <= 7 and (y-2) >= 0:
            if state.board[y-1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y-2,x+2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_LEFT
        if (x-2) >= 0 and (y+2) <= 7:
            if state.board[y+1][x-1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y+2,x-2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_RIGHT
        if (x+2) <= 7 and (y+2) <= 7:
            if state.board[y+1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y+2,x+2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1

        if failed == 4:
            successors += [state]
            return [state]
        else:
            return [state]
        
    elif piece == 'b':
        # DOWN_LEFT
        if (x-2) >= 0 and (y+2) <= 7:
            if state.board[y+1][x-1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y+2,x-2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_RIGHT
        if (x+2) <= 7 and (y+2) <= 7:
            if state.board[y+1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if new_state != None:
                    if new_state[0].switched == True:
                        successors += new_state
                        new_state[0].multi_jump = True
                    elif state.board != new_state[0].board:
                        new_state[0].multi_jump = True
                        multi_jump(new_state, (y+2,x+2), successors)
                else:
                    failed += 1
            else:
                failed += 1
        else:
            failed += 1

        if failed == 2:
            successors += [state]
            return [state]
        else:
            return [state]

def move_piece(state, piece_loc, move_loc):
    '''Using move tuple, move piece to location.'''
    # moving to an empty space
    # change piece initial position to '.'
    # then, make the change using move_loc and store the piece in that slot
    successor_board = copy.deepcopy(state.board)
    piece = successor_board[piece_loc[0]][piece_loc[1]]
    successor_board[piece_loc[0]][piece_loc[1]] = '.'
    if move_loc[0] == 0 and piece == 'r':
        successor_board[move_loc[0]][move_loc[1]] = 'R'
    elif move_loc[0] == 7 and piece =='b':
        successor_board[move_loc[0]][move_loc[1]] = 'B'
    else:
        successor_board[move_loc[0]][move_loc[1]] = piece
    successor = State(successor_board)
    return [successor]

def alpha_beta_search_max(state, turn, cache):
    v, best_move = max_value(state, -100000, 100000, 0, turn, cache)
    # Return the action with the value v
    return best_move

def alpha_beta_search_min(state, turn, cache):
    v, best_move = min_value(state, -100000, 100000, 0, turn, cache)
    # Return the action with the value v
    return best_move

def max_value(state, alpha, beta, depth, turn, cache):
    if depth == 10 or state.is_goal_min == True or state.is_goal_max == True:
        # At depth limit or terminal state
        # State caching
        if str(state) not in cache.keys():
            state.eval_fnc(turn)
            cache[str(state)] = state.eval
        return cache[str(state)], state
    v = -100000
    best_move = None
    actions = simulate_successors(state, turn, dec='max')
    for action in actions:
        curr_v = min_value(action, alpha, beta, depth+1, get_next_turn(turn), cache)[0]
        if curr_v >= v:
            v = curr_v
            best_move = action
        if v >= beta:
            return v, best_move
        alpha = max(alpha, v)
    return v, best_move

def min_value(state, alpha, beta, depth, turn, cache):
    if depth == 6 or state.is_goal_min == True or state.is_goal_max == True:
        # At depth limit or terminal state
        # State caching
        if str(state) not in cache.keys():
            state.eval_fnc(turn)
            cache[str(state)] = state.eval
        return cache[str(state)], state
    v = 100000
    best_move = None
    actions = simulate_successors(state, turn, dec='min')
    for action in actions:
        curr_v = max_value(action, alpha, beta, depth+1, get_next_turn(turn), cache)[0]
        if curr_v <= v:
            v = curr_v
            best_move = action
        if v <= alpha:
            return v, best_move
        beta = min(beta, v)
    return v, best_move

def game_time(state, cache):
    # red always goes first
    turn = 'r'
    while state.eval != 100000 and state.eval != -100000:
        if turn == 'r':
            # alpha beta pruning for red
            red_move = alpha_beta_search_max(state, 'r', cache)
            red_move.parent = state
            state = red_move
        elif turn == 'b':
            # alpha beta pruning for black
            black_move = alpha_beta_search_min(red_move, 'b', cache)
            black_move.parent = state
            state = black_move

        turn = get_next_turn(turn)

    return state

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board

def output_file(filename, soln):
    # Create output file
    sys.stdout = open(filename, 'w')

    # Get list of paths for each solution type and convert to string format
    path = soln.get_path()

    # Load file
    for state in reversed(path):
        for row in state:
            sys.stdout.writelines(row)
            sys.stdout.write("\n")
        sys.stdout.write("\n")

    # Close file
    sys.stdout.close()
    sys.stdout = sys.__stdout__

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    initial_board = read_from_file(args.inputfile)
    init_state = State(initial_board)
    turn = 'r'
    ctr = 0

    # Run game
    cache = dict()
    final_state = game_time(init_state, cache)
    output_file(args.outputfile, final_state)

