from battle import *
# from backtracking import bt_search
import sys

class AllDiffConstraint(Constraint):
    '''All diff constraint between a set of variables'''
    def __init__(self, name, scope):
        Constraint.__init__(self,name, scope)
        self._name = "AllDiff_" + name

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return len(set(assignments)) == len(assignments)

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
        other variable in the constraint that satisfies the constraint'''
        if var not in self.scope():
            return True  #var=val has support on any constraint it does not participate in

    #since the contraint has many variables use the helper function 'findvals'
    #for that we need two test functions
    #1. for testing complete assignments to the constraint's scope
    #   return True if and only if the complete assignment satisfies the constraint
    #2. for testing partial assignments to see if they could possibly work.
    #   return False if the partial assignment cannot be extended to a satisfying complete
    #   assignment
    #
    #Function #2 is only needed for efficiency (sometimes don't have one)
    #  if it isn't supplied findvals will use a function that never returns False
    #
    #For alldiff, we do have both functions! And they are the same!
    #We just check if the assignments are all to different values. If not return False
        def valsNotEqual(l):
            '''tests a list of assignments which are pairs (var,val)
                to see if they can satisfy the all diff'''
            vals = [val for (var, val) in l]
            return len(set(vals)) == len(vals)
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsNotEqual, valsNotEqual)
        return x

def print_solution(s, size):
    s_ = {}
    for (var, val) in s:
        s_[int(var.name())] = val
    for i in range(0, size):
        for j in range(0, size):
            print (s_[i*size+j]),
        print ('')

board = [[0,0,0,2,6,0,7,0,1],
[6,8,0,0,7,0,0,9,0],
[1,9,0,0,0,4,5,0,0],
[8,2,0,1,0,0,0,4,0],
[0,0,4,6,0,2,9,0,0],
[0,5,0,0,0,3,0,2,8],
[0,0,9,3,0,0,0,7,4],
[0,4,0,0,5,0,0,3,6],
[7,0,3,0,1,8,0,0,0]]

varlist = []
varn = {}
conslist = []

#define variables
'''CELL BASED APPROACH - EACH SQUARE IS A VARIABLE'''
for i in range(0,9):
    for j in range(0,9):
        v = None
        if board[i][j] > 0:
            '''If already assigned, make domain its value'''
            v = Variable(str((i*9+j)), [board[i][j]])
        else:
            '''Otherwise, set domain from 1-9 for new variable'''
            v = Variable(str((i*9+j)), [1,2,3,4,5,6,7,8,9]) 
            # For battleship, add ships as the domain, and add checks so that we can limit the domain depending on if we're at the
            # end of the board etc
    
        '''Create dictionary of variables created'''
        varlist.append(v)
        varn[str((i*9+j))] = v

#define row and column constraints
for i in range(9):
    rowi = []
    coli = []
    for j in range(9):
        '''Create row and column lists, and add the variables for row i and column j to the lists'''
        rowi.append(varn[str(i*9+j)])
        coli.append(varn[str(i+j*9)])
    
    '''Create two constraint objects for each row (i) and col(i), one that uses rowi as scope, other uses coli'''
    conslist.append(AllDiffConstraint('row'+str(i),rowi))
    conslist.append(AllDiffConstraint('col'+str(i),coli)) 

#define same square constraints
'''Define second constraint relevant for sudoku'''
for i in (0, 3, 6):
    for j in (0, 3, 6):
        scope = []
        for k in range(2):
            for l in range(2):
                scope.append(varn[str((i+k)*9+j+l)])
                conslist.append(AllDiffConstraint("sq"+str(i)+str(j), scope))

#add all constraints, variables to csp and solve
csp = CSP('sudoku', varlist, conslist)
# solutions, num_nodes = bt_search('GAC', csp, 'mrv', True, False)
# print_solution(solutions[0], 9)
'''Look through solutions and check for ship constraints'''