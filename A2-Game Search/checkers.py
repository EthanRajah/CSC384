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

def simulate(state):
    '''Beginning with the initial board state, simulate the checkers game'''
    # Red always starts first
    curr_turn = 'r'
    while state.is_goal() == False:
        # while the are still black pieces on the board, keep playing
        successors = generate_successors(state, curr_turn)
        # Choose from possible successors
        

def generate_successors(state, curr_turn):
    '''Determine if particular movement (single move or jump(s)) are possible. If jumps are possible, it must be done.
    After the move check, move the piece and create a new board with the moved piece as a possible successor state'''
    if curr_turn == 'r':
        # Red begins on bottom 3 rows of board
        for i in range(state.height):
            if 'r' in state.board[i] or 'R' in state.board[i]:
                for j in range(state.width):
                    # Find position(s) in row with 'r'
                    if state.board[i][j] == '.':
                        continue
                    elif state.board[i][j] == 'r':
                        move_check(state,j,i,'r')
                    elif state.board[i][j] == 'R':
                        move_check(state,j,i,'R')
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
                        move_check(state,j,i,'b')
                    elif state.board[i][j] == 'B':
                        move_check(state,j,i,'B')
            else:
                # No black piece in current row
                continue

def move_check(state, x, y, player):
    '''Given the (x,y) coords of the piece of interest, see what moves are possible. If a jump is possible, use recursion within move function to check for multiple jumps
    and return a list of moves for the piece to make'''
    successors = []

    # initialization
    if player in ['r', 'R']:
        opps = ['b', 'B']
    else:
        opps = ['r', 'R']

    if player == 'r':
        # if player is 'r', guarantees that we are not at first row (since it'd be 'R')
        if x != 0:
            # if not at first column, check diagonal left
            if state.board[y-1][x-1] in opps:
                # check for jump left
                '''JUMP FUNCTION FOR FIRST JUMP -- TRY TO DO FIRST JUMP, IF IT CAN'T RETURN NONE, OTHERWISE RETURN NEW BOARD STATE AND CALL MOVE_PIECE'''
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=True, dir='up_left')
            elif state.board[y-1][x-1] == '.':
                # left diagonal must be empty space
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=False, dir='up_left')
        
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y-1][x+1] in opps:
                # check for jump right
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=True, dir='up_right')
            elif state.board[y-1][x+1] == '.':
                # right diagonal must be empty space
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=False, dir='up_right')

    elif player == 'R':
        if x == 0:
            # if R is in the first column
            if y == 0:
                # if R is also in the first row -- can only move down and to the right
                if state.board[y+1][x+1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=True, dir='down_right')
                elif state.board[y+1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=False, dir='down_right')
            elif y == 7:
                # if R is in last row -- can only move up and to the right
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=True, dir='up_right')
                elif state.board[y-1][x+1] == '.':
                    # right diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=False, dir='up_right')
            else:
                # can move in two diagonal directions to the RIGHT
                if state.board[y-1][x+1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=True, dir='up_right')
                elif state.board[y-1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=False, dir='up_right') 

                if state.board[y+1][x+1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=True, dir='down_right')
                elif state.board[y+1][x+1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=False, dir='down_right')               

        elif x == 7:
            # if R is in the last column
            if y == 0:
                # if R is also in the first row -- can only move down and to the left
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=True, dir='down_left')
                elif state.board[y+1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=False, dir='down_left')
            elif y == 7:
                # if R is in last row -- can only move up and to the left
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=True, dir='up_left')
                elif state.board[y-1][x-1] == '.':
                    # left diagonal must be empty space
                    successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=False, dir='up_left')
            else:
                # can move in two diagonal directions to the LEFT
                if state.board[y-1][x-1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=True, dir='up_left')
                elif state.board[y-1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=False, dir='up_left') 
                
                if state.board[y+1][x-1] in opps:
                    # check for jump
                    successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=True, dir='down_left')
                elif state.board[y+1][x-1] == '.':
                    successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=False, dir='down_left')

        elif y == 0:
            # not in first or last column, but in top row -- can only move down in two directions
            if state.board[y+1][x-1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=True, dir='down_left')
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=False, dir='down_left') 

            if state.board[y+1][x+1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=True, dir='down_right')
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=False, dir='down_right')

        elif y == 7:
            # not in first or last column, but in last row -- can only move up in two directions
            if state.board[y-1][x-1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=True, dir='up_left')
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=False, dir='up_left') 

            if state.board[y-1][x+1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=True, dir='up_right')
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=False, dir='up_right')

        else:
            # at a position where the piece can move in any 4 directions
            # UP_LEFT
            if state.board[y-1][x-1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=True, dir='up_left')
            elif state.board[y-1][x-1] == '.':
                successors += move_piece(state, (y,x), (y-1,x-1), jump_cond=False, dir='up_left') 
            # UP_RIGHT
            if state.board[y-1][x+1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=True, dir='up_right')
            elif state.board[y-1][x+1] == '.':
                successors += move_piece(state, (y,x), (y-1,x+1), jump_cond=False, dir='up_right')
            # DOWN_LEFT
            if state.board[y+1][x-1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=True, dir='down_left')
            elif state.board[y+1][x-1] == '.':
                successors += move_piece(state, (y,x), (y+1,x-1), jump_cond=False, dir='down_left') 
            # DOWN_RIGHT
            if state.board[y+1][x+1] in opps:
                # check for jump
                successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=True, dir='down_right')
            elif state.board[y+1][x+1] == '.':
                successors += move_piece(state, (y,x), (y+1,x+1), jump_cond=False, dir='down_right')                       

    elif player == 'b':
        pass

def first_jump(state, piece_loc, move_loc, jump_cond, dir):
    '''Check if first jump can be made, if it can then complete the first jump'''
    pass

def move_piece(state, piece_loc, move_loc, jump_cond, dir):
    '''Using move tuple, move piece to location. Then, if a jump occured, check if multiple jumps can occur and execute using recursion'''
    
    successor_board = copy.deepcopy(state.board)
    piece = successor_board[piece_loc[0]][piece_loc[1]]

    if jump_cond == True:
        # an opponent piece is to the diagonal of this piece; check if jump can be made again and if it can, enter recursion
        if dir == 'up_right':
            if move_loc[0] != 0 or move_loc[1] != 7:
                if successor_board[move_loc[0]-1][move_loc[1]+1] == '.':
                    # jump can be made again
                    pass
                else:
                    return state
        elif dir == 'up_left':
            pass
        elif dir == 'down_right':
            pass
        elif dir == 'down_left':
            pass
    else:
        # moving to an empty space
        # change piece initial position to '.'
        # then, make the change using move_loc and store the piece in that slot
        successor_board[piece_loc[0]][piece_loc[1]] = '.'
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
    print(init_state.board)
    turn = 'r'
    ctr = 0

    sys.stdout = open(args.outputfile, 'w')

    sys.stdout = sys.__stdout__

