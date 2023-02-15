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
    if player == 'r':
        # if player is 'r', guarantees that we are not at first row (since it'd be 'R')
        if x != 0:
            # if not at first column, check diagonal left
            if state.board[y-1][x-1] == 'b' or state.board[y-1][x-1] == 'B':
                # check for jump left
                '''CHECK FINAL JUMP LOCATION'''
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=True)
            elif state.board[y-1][x-1] == '.':
                # left diagonal must be empty space
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=False)
        
        if x != 7:
            # if not at last column, check diagonal right
            if state.board[y-1][x+1] == 'b' or state.board[y-1][x+1] == 'B':
                # check for jump right
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=True)
            elif state.board[y-1][x+1] == '.':
                # right diagonal must be empty space
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=False)

    elif player == 'R':
        if x == 0:
            # if R is in the first column
            if y == 0:
                # if R is also in the first row -- can only move down and to the right
                if state.board[y+1][x+1] == 'b' or state.board[y+1][x+1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=True)
                elif state.board[y+1][x+1] == 'b':
                    # right diagonal must be empty space
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=False)
            elif y == 7:
                # if R is in last row -- can only move up and to the right
                if state.board[y-1][x+1] == 'b' or state.board[y-1][x+1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=True)
                elif state.board[y-1][x+1] == '.':
                    # right diagonal must be empty space
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=False)
            else:
                # can move in two diagonal directions to the RIGHT
                if state.board[y-1][x+1] == 'b' or state.board[y-1][x+1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=True)
                elif state.board[y-1][x+1] == '.':
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=False) 

                if state.board[y+1][x+1] == 'b' or state.board[y+1][x+1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=True)
                elif state.board[y+1][x+1] == '.':
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=False)               

        elif x == 7:
            # if R is in the last column
            if y == 0:
                # if R is also in the first row -- can only move down and to the left
                if state.board[y+1][x-1] == 'b' or state.board[y+1][x-1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=True)
                elif state.board[y+1][x-1] == '.':
                    # left diagonal must be empty space
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=False)
            elif y == 7:
                # if R is in last row -- can only move up and to the left
                if state.board[y-1][x-1] == 'b' or state.board[y-1][x-1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=True)
                elif state.board[y-1][x-1] == '.':
                    # left diagonal must be empty space
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=False)
            else:
                # can move in two diagonal directions to the LEFT
                if state.board[y-1][x-1] == 'b' or state.board[y-1][x-1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=True)
                elif state.board[y-1][x-1] == '.':
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=False) 
                
                if state.board[y+1][x-1] == 'b' or state.board[y+1][x-1] == 'B':
                    # check for jump
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=True)
                elif state.board[y+1][x-1] == '.':
                    successor_board = copy.deepcopy(state.board)
                    successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=False)

        elif y == 0:
            # not in first or last column, but in top row -- can only move down in two directions
            if state.board[y+1][x-1] == 'b' or state.board[y+1][x-1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=True)
            elif state.board[y+1][x-1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=False) 

            if state.board[y+1][x+1] == 'b' or state.board[y+1][x+1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=True)
            elif state.board[y+1][x+1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=False)

        elif y == 7:
            # not in first or last column, but in last row -- can only move up in two directions
            if state.board[y-1][x-1] == 'b' or state.board[y-1][x-1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=True)
            elif state.board[y-1][x-1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=False) 

            if state.board[y-1][x+1] == 'b' or state.board[y-1][x+1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=True)
            elif state.board[y-1][x+1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=False)

        else:
            # at a position where the piece can move in any 4 directions
            # UP_LEFT
            if state.board[y-1][x-1] == 'b' or state.board[y-1][x-1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=True)
            elif state.board[y-1][x-1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x-1), jump_cond=False) 
            # UP_RIGHT
            if state.board[y-1][x+1] == 'b' or state.board[y-1][x+1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=True)
            elif state.board[y-1][x+1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y-1,x+1), jump_cond=False)
            # DOWN_LEFT
            if state.board[y+1][x-1] == 'b' or state.board[y+1][x-1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=True)
            elif state.board[y+1][x-1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x-1), jump_cond=False) 
            # DOWN_RIGHT
            if state.board[y+1][x+1] == 'b' or state.board[y+1][x+1] == 'B':
                # check for jump
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=True)
            elif state.board[y+1][x+1] == '.':
                successor_board = copy.deepcopy(state.board)
                successors += move_piece(successor_board, (y,x), (y+1,x+1), jump_cond=False)                       

    elif player == 'b':
        pass
    elif player == 'B':
        pass

def move_piece(successor_board, piece_loc, move_loc, jump_cond):
    '''Using move tuple, move piece to location. Then, if a jump occured, check if multiple jumps can occur and execute using recursion'''
    
    piece = successor_board[piece_loc[0]][piece_loc[1]]

    if jump_cond == True:
        # a jump can be made; perform recursion if possible
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

