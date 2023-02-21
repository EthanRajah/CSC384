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

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")
    
    def compute_utility(self):
        '''Determine player's utility of TERMINAL state'''
        pass

    def eval_fnc(self):
        '''Estimate player's utility of NON TERMINAL state'''
        pass

    def is_goal(self):
        '''Determine if board is a winner/goal state for MAX'''
        for i in range(len(self.board)):
            if 'b' in self.board[i]:
                return False
            else:
                continue
        return True

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

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board

def simulate(state, first_turn):
    '''Beginning with the initial board state, simulate the checkers game'''
    # Red always starts first
    curr_turn = first_turn
    while state.is_goal() == False:
        # while the are still black pieces on the board, keep playing
        successors = generate_successors(state, curr_turn)
        # Choose from possible successors
        break
    print(successors[7].board)

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
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x-2), successors) 
            elif state.board[y-1][x-1] == '.':
                # left diagonal must be empty space
                successors += move_piece(state, (y,x), (y-1,x-1))
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y-1][x+1] in opps:
                # check for jump right
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x+2), successors)
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
                    if pos_state != None:
                        multi_jump(pos_state, (y+2,x+2), successors)
                elif state.board[y+1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x+1))
            elif y == 7:
                # if R is in last row -- can only move up and to the right
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                    if pos_state != None:
                        multi_jump(pos_state, (y-2,x+2), successors)
                elif state.board[y-1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x+1))
            else:
                # can move in two diagonal directions to the RIGHT
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                    if pos_state != None:
                        multi_jump(pos_state, (y-2,x+2), successors)
                elif state.board[y-1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x+1)) 

                if state.board[y+1][x+1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                    if pos_state != None:
                        multi_jump(pos_state, (y+2,x+2), successors)
                elif state.board[y+1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x+1))               

        elif x == 7:
            # if R is in the last column
            if y == 0:
                # if R is also in the first row -- can only move down and to the left
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                    if pos_state != None:
                        multi_jump(pos_state, (y+2,x-2), successors)
                elif state.board[y+1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x-1))
            elif y == 7:
                # if R is in last row -- can only move up and to the left
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                    if pos_state != None:
                        multi_jump(pos_state, (y-2,x-2), successors)
                elif state.board[y-1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x-1))
            else:
                # can move in two diagonal directions to the LEFT
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                    if pos_state != None:
                        multi_jump(pos_state, (y-2,x-2), successors)
                elif state.board[y-1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x-1)) 
                
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                    if pos_state != None:
                        multi_jump(pos_state, (y+2,x-2), successors)
                elif state.board[y+1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x-1))

        elif y == 0:
            # not in first or last column, but in top row -- can only move down in two directions
            if state.board[y+1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x-2), successors)
                    return successors
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1)) 

            if state.board[y+1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x+2), successors)
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1))

        elif y == 7:
            # not in first or last column, but in last row -- can only move up in two directions
            if state.board[y-1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x-2), successors)
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1)) 

            if state.board[y-1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x+2), successors)
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1))

        else:
            # at a position where the piece can move in any 4 directions
            # UP_LEFT
            if state.board[y-1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x-1), dir='up_left')
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x-2), successors)
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1)) 
            # UP_RIGHT
            if state.board[y-1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                if pos_state != None:
                    multi_jump(pos_state, (y-2,x+2), successors)
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1))
            # DOWN_LEFT
            if state.board[y+1][x-1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x-2), successors)
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1)) 
            # DOWN_RIGHT
            if state.board[y+1][x+1] in opps:
                # check for jump
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x+2), successors)
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1))
    
    elif player == 'b':
        # if player is 'b', guarantees that we are not at last row (since it'd be 'B')
        if x != 0:
            # if not at first column, check diagonal left
            if state.board[y+1][x-1] in opps:
                # check for jump left
                pos_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x-2), successors) 
            elif state.board[y+1][x-1] == '.':
                # left diagonal must be empty space
                successors += move_piece(state, (y,x), (y+1,x-1))
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y+1][x+1] in opps:
                # check for jump right
                pos_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                if pos_state != None:
                    multi_jump(pos_state, (y+2,x+2), successors)
            elif state.board[y-1][x+1] == '.':
                # right diagonal must be empty space
                successors += move_piece(state, (y,x), (y+1,x+1))

    return successors

def first_jump(state, piece_loc, move_loc, dir):
    '''Check if first jump can be made, if it can then complete the first jump'''
    # since diagonal piece is opponent, lets check if we can do another move in the same direction diagonally to complete jump
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
                else:
                    successor_board[move_loc[0]-1][move_loc[1]+1] = piece
                new_state = State(successor_board)
                return [new_state]
            else:
                return [None]
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
                else:
                    successor_board[move_loc[0]-1][move_loc[1]-1] = piece
                new_state = State(successor_board)
                return [new_state]
            else:
                return [None]

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
                else:
                    successor_board[move_loc[0]+1][move_loc[1]+1] = piece
                new_state = State(successor_board)
                return [new_state]
            else:
                return [None]
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
                else:
                    successor_board[move_loc[0]+1][move_loc[1]-1] = piece
                new_state = State(successor_board)
                return [new_state]
            else:
                return [None]

def multi_jump(state, piece_loc, successors):
    '''Take a state that has just done one jump and recursively do more if possible'''
    print(1)
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
                multi_jump(new_state, (y-2,x-2), successors)
            else:
                failed += 1
        else:
            failed += 1
        
        # UP_RIGHT
        if (x+2) <= 7 and (y-2) >= 0:
            if state.board[y-1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                multi_jump(new_state, (y-2,x+2), successors)
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
                multi_jump(new_state, (y-2,x-2), successors)
            else:
                failed += 1
        else:
            failed += 1
        
        # UP_RIGHT
        if (x+2) <= 7 and (y-2) >= 0:
            if state.board[y-1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y-1,x+1), dir='up_right')
                multi_jump(new_state, (y-2,x+2), successors)
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_LEFT
        if (x-2) >= 0 and (y+2) <= 7:
            if state.board[y+1][x-1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x-1), dir='down_left')
                multi_jump(new_state, (y+2,x-2), successors)
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_RIGHT
        if (x+2) <= 7 and (y+2) <= 7:
            if state.board[y+1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x+1), dir='down_right')
                multi_jump(new_state, (y+2,x+2), successors)
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
                multi_jump(new_state, (y+2,x-2), successors)
            else:
                failed += 1
        else:
            failed += 1
        
        # DOWN_RIGHT
        if (x+2) <= 7 and (y+2) <= 7:
            if state.board[y+1][x+1] in opps:
                new_state = first_jump(state, (y,x), (y+1,x+1), dir='down_left')
                multi_jump(new_state, (y+2,x+2), successors)
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
    turn = 'b'
    ctr = 0
    simulate(init_state, turn)

    sys.stdout = open(args.outputfile, 'w')

    sys.stdout = sys.__stdout__
