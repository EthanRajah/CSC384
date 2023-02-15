from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

char_goal = '1'
char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        # returns attributes of piece
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)
    
    def move(self, dir):
        # based on the fact that the motion is possible, move a piece (based on top left corner of piece)
        if dir == 'right':
            self.coord_x += 1
        elif dir == 'left':
            self.coord_x -= 1
        elif dir == 'up':
            self.coord_y -= 1
        elif dir == 'down':
            self.coord_y += 1

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        Symbols are set in certain places on board, depending on where the piece is located (checking coords)

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                # King piece setup (4 spaces)
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                # Single piece setup (1 space)
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                # 1x2 piece setup (2 spaces)
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
    
    def find_empty(self):
        # find the two empty slots on the board
        empty = []
        for i in range(5):
            for j in range(4):
                if self.grid[i][j] == '.':
                    point = (j,i)
                    empty += [point]
        # print('Empty spaces:', empty)
        return empty

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree. This is the g value for the heuristic function
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.

    def goal_state(self):
        # Check if the current state is a goal state
        # Goal state if the King piece coordinates are: coord_x = 1, coord_y = 3 (location of top left piece)
        if self.board.grid[3][1] == '1' and self.board.grid[3][2] == '1' and self.board.grid[4][1] == '1' \
        and self.board.grid[4][2] == '1':
            return True
        else:
            return False

    def heuristic(self, state):
        # Compute heuristic function from state (n) to goal state
        # Initial state to state n costs g (depth of state) 
        # Goal: king top left part should be located at (1,3)
        goal = (1,3)
        if state.goal_state():
            # h = 0
            state.f = state.depth
        else:
            for piece in state.board.pieces:
                if piece.is_goal:
                    h = abs(piece.coord_x - goal[0]) + abs(piece.coord_y - goal[1])
                    state.f = h + state.depth

    def generate_successors(self):
        # Based on state, return a list of the possible successor states

        """
        Logic:

        1. Find empty space locations
        2. Check what pieces are to the left, right, up, down from the empty spaces (board.pieces)
        3. Decide if moving an adjacent piece is possible (also depends on if empty spaces are next to one another)
        4. If motion is possible, move piece, load new board and add resulting state to list
        """

        spaces = self.board.find_empty()
        empty1, empty2 = spaces[0], spaces[1]
        
        # Get coords of pieces around empty spots if not at edges
        if empty1[0] != 0:
            left1 = self.piece_left(empty1)
            # print(left1)
        else:
            left1 = None
            # print(left1)
        if empty2[0] != 0:
            left2 = self.piece_left(empty2)
            # print(left2)
        else:
            left2 = None
            # print(left2)           
        if empty1[0] != 3:
            right1 = self.piece_right(empty1)
            # print(right1)
        else:
            right1 = None
            # print(right1)
        if empty2[0] != 3:
            right2 = self.piece_right(empty2)
            # print(right2)
        else:
            right2 = None
            # print(right2)
        if empty1[1] != 0:
            above1 = self.piece_above(empty1)
            # print(above1)
        else:
            above1 = None
            # print(above1)
        if empty2[1] != 0:
            above2 = self.piece_above(empty2)
            # print(above2)
        else:
            above2 = None
            # print(above2)
        if empty1[1] != 4:
            below1 = self.piece_below(empty1)
            # print(below1)
        else:
            below1 = None
            # print(below1)
        if empty2[1] != 4:
            below2 = self.piece_below(empty2)
            # print(below2)
        else:
            below2 = None
            # print(below2)
        
        # Using surrounding piece coordinates, classify the pieces and generate states for each empty slot
        successor_states1 = self.piece_classification(left1, right1, above1, below1, empty1)
        successor_states2 = self.piece_classification(left2, right2, above2, below2, empty2)

        # Combine state lists to 1 successor state list
        successors_dup = successor_states1 + successor_states2
        successors_boards = []
        successors = []
        
        # Get rid of duplicate states from the two empty spots. Then calculate heuristic for each remaining state
        for i in range (len(successors_dup)):
            if successors_dup[i].board.grid not in successors_boards:
                successors_boards += [successors_dup[i].board.grid]

        for i in range (len(successors_dup)):
            for j in range (len(successors_boards)):
                if successors_dup[i].board.grid == successors_boards[j]:
                    successors.append(successors_dup[i])
                    successors_boards.remove(successors_boards[j])
                    self.heuristic(successors_dup[i])
                    break

        return successors

    def piece_left(self, empty_spot):
        # Determine what piece is to the left of the empty spot
        piece = self.board.grid[empty_spot[1]][empty_spot[0]-1]
        if piece == '1':
            # part of King
            # Get coords of king piece
            if empty_spot[1] != 0:
                if self.board.grid[empty_spot[1]-1][empty_spot[0]-1] == '1':
                    # Top right of piece
                    king = (empty_spot[0]-2, empty_spot[1]-1)
                    return king
                else:
                    king = (empty_spot[0]-2, empty_spot[1])
                    return king
            else:
                # Guaranteed top right of piece
                king = (empty_spot[0]-2, empty_spot[1])
                return king                
        elif piece == '2':
            # single piece
            single = (empty_spot[0]-1, empty_spot[1])
            return single
        elif piece == 'v':
            # bottom of vertical piece
            vert = (empty_spot[0]-1, empty_spot[1]-1)
            return vert
        elif piece == '^':
            # top of vertical piece
            vert = (empty_spot[0]-1, empty_spot[1])
            return vert
        elif piece == '>':
            # right side of horizontal piece
            horiz = (empty_spot[0]-2, empty_spot[1])
            return horiz
        # Cannot have < on left side of empty slot
        else:
            # also empty space
            # if empty space next to it, return same coords
            return (empty_spot[0], empty_spot[1])

    def piece_right(self,empty_spot):
        # Determine what piece is to the right of the empty spot
        piece = self.board.grid[empty_spot[1]][empty_spot[0]+1]
        if piece == '1':
            # part of King
            # Get coords of king piece
            if empty_spot[1] != 0:
                if self.board.grid[empty_spot[1]-1][empty_spot[0]+1] == '1':
                    # Top left of piece
                    king = (empty_spot[0]+1, empty_spot[1]-1)
                    return king
                else:
                    king = (empty_spot[0]+1, empty_spot[1])
                    return king
            else:
                # Guaranteed top left of piece
                king = (empty_spot[0]+1, empty_spot[1])
                return king                
        elif piece == '2':
            # single piece
            single = (empty_spot[0]+1, empty_spot[1])
            return single
        elif piece == 'v':
            # bottom of vertical piece
            vert = (empty_spot[0]+1, empty_spot[1]-1)
            return vert
        elif piece == '^':
            # top of vertical piece
            vert = (empty_spot[0]+1, empty_spot[1])
            return vert
        elif piece == '<':
            # left side of horizontal piece
            horiz = (empty_spot[0]+1, empty_spot[1])
            return horiz
        # Cannot have > on right side of empty slot
        else:
            # also empty space
            # if empty space next to it, return same coords
            return (empty_spot[0], empty_spot[1])
    
    def piece_above(self, empty_spot):
        # Determine what piece is above the empty spot
        piece = self.board.grid[empty_spot[1]-1][empty_spot[0]]
        if piece == '1':
            # part of King
            # Get coords of king piece
            if empty_spot[0] != 0:
                if self.board.grid[empty_spot[1]-2][empty_spot[0]-1] == '1':
                    # Top left of piece
                    king = (empty_spot[0]-1, empty_spot[1]-2)
                    return king
                else:
                    king = (empty_spot[0], empty_spot[1]-2)
                    return king
            else:
                king = (empty_spot[0], empty_spot[1]-2)
                return king
        elif piece == '2':
            # single piece
            single = (empty_spot[0], empty_spot[1]-1)
            return single
        elif piece == 'v':
            # bottom of vertical piece
            vert = (empty_spot[0], empty_spot[1]-2)
            return vert
        elif piece == '^':
            # top of vertical piece
            vert = (empty_spot[0], empty_spot[1]-1)
            return vert
        elif piece == '<':
            # left side of horizontal piece
            horiz = (empty_spot[0], empty_spot[1]-1)
            return horiz
        elif piece == '>':
            # right side of horizontal piece
            horiz = (empty_spot[0]-1, empty_spot[1]-1)
            return horiz
        else:
            # also empty space
            # if empty space next to it, return same coords
            return (empty_spot[0], empty_spot[1])

    def piece_below(self, empty_spot):
        # Determine what piece is below the empty spot
        piece = self.board.grid[empty_spot[1]+1][empty_spot[0]]
        if piece == '1':
            # part of King
            # Get coords of king piece
            if empty_spot[0] != 0:
                if self.board.grid[empty_spot[1]+1][empty_spot[0]-1] == '1':
                    # Top left of piece
                    king = (empty_spot[0]-1, empty_spot[1]+1)
                    return king
                else:
                    king = (empty_spot[0], empty_spot[1]+1)
                    return king
            else:
                king = (empty_spot[0], empty_spot[1]+1)
                return king
        elif piece == '2':
            # single piece
            single = (empty_spot[0], empty_spot[1]+1)
            return single
        elif piece == '^':
            # top of vertical piece
            vert = (empty_spot[0], empty_spot[1]+1)
            return vert
        elif piece == '<':
            # left side of horizontal piece
            horiz = (empty_spot[0], empty_spot[1]+1)
            return horiz
        elif piece == '>':
            # right side of horizontal piece
            horiz = (empty_spot[0]-1, empty_spot[1]+1)
            return horiz
        else:
            # also empty space
            # if empty space next to it, return same coords
            return (empty_spot[0], empty_spot[1])     

    def piece_classification(self, left1, right1, above1, below1, empty1):
        # Match the coordinates of the surrounding pieces with the pieces on the board and try to move
        states = []
        for piece in self.board.pieces:
            ### LEFT PIECE 
            if left1 is not None and (piece.coord_x, piece.coord_y) == left1:
                # piece found from pieces list
                # make copy of board
                cp_board = deepcopy(self.board)
                # find piece in copied state
                for piece_cp in cp_board.pieces:
                    if (piece_cp.coord_x, piece_cp.coord_y) == (piece.coord_x, piece.coord_y):
                        # found copied piece to move so break out of search loop
                        break
                if piece.is_goal:
                    # King piece (4 spaces)
                    if left1 == (empty1[0]-2, empty1[1]):
                            # top left 1 begins to left of empty, on same row
                            if below1 == empty1:
                                # Can move king 2x2 if second empty spot is below or above first empty
                                # Else: Can't move king piece as we only have one empty space available and need 2 adjacent
                                piece_cp.move('right')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                    else:
                        # top left 1 begins one row above
                        if above1 == empty1:
                            # Can move king 2x2 if second empty spot is below or above first empty
                            piece_cp.move('right')
                            states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                elif piece.is_single:
                    # Single piece (1 space)
                    piece_cp.move('right')
                    states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                else:
                    # 1x2 piece (2 spaces)
                    if piece.orientation == 'h':
                        piece_cp.move('right')
                        states.append(State(Board(cp_board.pieces),0,self.depth+1,self))                
                    elif piece.orientation == 'v':
                        if left1 == (empty1[0]-1, empty1[1]):
                            # '^' begins to left of empty
                            if below1 == empty1:
                                # Can move vertical 1x2 if second empty spot is below or above first empty
                                # Else: Can't move vertical piece as we only have one empty space available and need 2 adjacent
                                piece_cp.move('right')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                        else:
                            # '^' begins one row above
                            if above1 == empty1:
                                # Can move vertical 1x2 if second empty spot is below or above first empty
                                piece_cp.move('right')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                                            
            ### RIGHT PIECE
            elif right1 is not None and (piece.coord_x, piece.coord_y) == right1:
                # piece found from pieces list
                # make copy of board
                cp_board = deepcopy(self.board)
                # find piece in copied state
                for piece_cp in cp_board.pieces:
                    if (piece_cp.coord_x, piece_cp.coord_y) == (piece.coord_x, piece.coord_y):
                        # found copied piece to move so break out of search loop
                        break
                if piece.is_goal:
                    # King piece (4 spaces)
                    if right1 == (empty1[0]+1, empty1[1]):
                        if below1 == empty1:
                            # Can move king 2x2 if second empty spot is below or above first empty
                            # Else: Can't move king piece as we only have one empty space available and need 2 adjacent
                            piece_cp.move('left')
                            states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                    else:
                        # top left 1 begins one row above
                        if above1 == empty1:
                            # Can move king 2x2 if second empty spot is below or above first empty
                            piece_cp.move('left')
                            states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                elif piece.is_single:
                    # Single piece (1 space)
                    piece_cp.move('left')
                    states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                else:
                    # 1x2 piece (2 spaces)
                    if piece.orientation == 'h':
                        piece_cp.move('left')
                        states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                    elif piece.orientation == 'v':
                        if right1 == (empty1[0]+1, empty1[1]):
                            # '^' begins to right of empty
                            if below1 == empty1:
                                # Can move vertical 1x2 if second empty spot is below or above first empty
                                # Else: Can't move vertical piece as we only have one empty space available and need 2 adjacent
                                piece_cp.move('left')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                        else:
                            # '^' begins one row above
                            if above1 == empty1:
                                # Can move vertical 1x2 if second empty spot is below or above first empty
                                piece_cp.move('left')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
        
            ### ABOVE PIECE
            elif above1 is not None and (piece.coord_x, piece.coord_y) == above1:
                # piece found from pieces list
                # make copy of board
                cp_board = deepcopy(self.board)
                # find piece in copied state
                for piece_cp in cp_board.pieces:
                    if (piece_cp.coord_x, piece_cp.coord_y) == (piece.coord_x, piece.coord_y):
                        # found copied piece to move so break out of search loop
                        break
                if piece.is_goal:
                    # King piece (4 spaces)
                    if above1 == (empty1[0], empty1[1]-2):
                        # king top left 1 is directly above empty
                            if right1 == empty1:
                                # Else: Can't move king piece as we only have one empty space available and need 2 adjacent
                                piece_cp.move('down')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                    else: 
                        if left1 == empty1:
                            piece_cp.move('down')
                            states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                elif piece.is_single:
                    # Single piece (1 space)
                    piece_cp.move('down')
                    states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                else:
                    # 1x2 piece (2 spaces)
                    if piece.orientation == 'h':
                        if above1 == (empty1[0], empty1[1]-1):
                            # '<' begins above of empty
                            if right1 == empty1:
                                piece_cp.move('down')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                        else:
                            # '<' begins one row above and one to the left
                            if left1 == empty1:
                                piece_cp.move('down')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))                                              
                    elif piece.orientation == 'v':
                        piece_cp.move('down')
                        states.append(State(Board(cp_board.pieces),0,self.depth+1,self))

            ### BELOW PIECE
            elif below1 is not None and (piece.coord_x, piece.coord_y) == below1:
                # piece found from pieces list
                # make copy of board
                cp_board = deepcopy(self.board)
                # find piece in copied state
                for piece_cp in cp_board.pieces:
                    if (piece_cp.coord_x, piece_cp.coord_y) == (piece.coord_x, piece.coord_y):
                        # found copied piece to move so break out of search loop
                        break
                if piece.is_goal:
                    # King piece (4 spaces)
                    if below1 == (empty1[0], empty1[1]+1):
                        # king top left 1 is directly below empty
                            if right1 == empty1:
                                # Else: Can't move king piece as we only have one empty space available and need 2 adjacent
                                piece_cp.move('up')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                    else: 
                        if left1 == empty1:
                            piece_cp.move('up')
                            states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                elif piece.is_single:
                    # Single piece (1 space)
                    piece_cp.move('up')
                    states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                else:
                    # 1x2 piece (2 spaces)
                    if piece.orientation == 'h':
                        if below1 == (empty1[0], empty1[1]+1):
                            # '<' begins below empty
                            if right1 == empty1:
                                piece_cp.move('up')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
                        else:
                            # '<' begins one row below and one to the left
                            if left1 == empty1:
                                piece_cp.move('up')
                                states.append(State(Board(cp_board.pieces),0,self.depth+1,self))                                             
                    elif piece.orientation == 'v':
                        piece_cp.move('up')
                        states.append(State(Board(cp_board.pieces),0,self.depth+1,self))
        
        return states        

    def get_path(self):
        # Given the goal state is reached, backtrack using the parent values to determine solution path
        path = []
        count = 0
        while self.parent != None:
            path += [self.board.grid]
            self = self.parent
            count += 1
        # print(count)
        path += [self.board.grid]
        print(count)
        return path

def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        # Reading file to find each piece and setting their initial positions

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    # Initialize board with pieces and state of current board to be updated when the board changes
    board = Board(pieces)
    state = State(board, 0, 0, None) 
    
    return board, state

def output_file(filename, soln):
    # Create output file
    output = open(filename, "w")

    # Get list of paths for each solution type and convert to string format
    path = soln.get_path()

    # Load file
    for state in reversed(path):
        for row in state:
            output.writelines(row)
            output.write("\n")
        output.write("\n")

    # Close file
    output.close()

def dfs(state0):
    # initialize frontier list and explored set
    frontier = [state0]
    explored = set()

    while frontier:
        # while frontier is not empty
        # remove based on LIFO
        state = frontier.pop()
        if str(state.board.grid) not in explored:
            explored.add(str(state.board.grid))
            if state.goal_state():
                # If state is goal state, get goal path and return it
                return state
            else:
                # Add successors of state to frontier
                successors = state.generate_successors()
                frontier = frontier + successors
    return None
        
def astar(state0):
    # initialize frontier heap and explored set
    frontier = []
    heappush(frontier, (state0.f, state0.id, state0))
    explored = set()

    while frontier:
        # while frontier is not empty
        # remove based on smallest f value. If tie, remove based on id
        state_tup = heappop(frontier)
        state = state_tup[2]

        if str(state.board.grid) not in explored:
            explored.add(str(state.board.grid))
            if state.goal_state():
                # If state is goal state, get goal path and return it
                return state
            else:
                # Add successors of state to frontier
                successors = state.generate_successors()
                for successor in successors:
                    heappush(frontier, (successor.f, successor.id, successor))
    return None

if __name__ == "__main__":

    # Interpretting lines from terminal

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file and intiialize classes
    board, state0 = read_from_file(args.inputfile)

    if args.algo == 'dfs':
        soln = dfs(state0)
    elif args.algo == 'astar':
        soln = astar(state0)

    # Create output file
    output_file(args.outputfile, soln)
    


    




