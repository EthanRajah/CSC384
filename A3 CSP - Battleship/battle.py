import sys
import argparse

'''****************************************************************************Class Definitions**********************************************************************************************'''

class Variable:
    '''Class for defining CSP variables.

      On initialization the variable object can be given a name and a
      list containing variable's domain of values. You can reset the
      variable's domain if you want to solve a similar problem where
      the domains have changed.

      To support CSP propagation, the class also maintains a current
      domain for the variable. Values pruned from the variable domain
      are removed from the current domain but not from the original
      domain. Values can be also restored.
    '''

    undoDict = dict()             #stores pruned values indexed by a
                                        #(variable,value) reason pair
    def __init__(self, name, domain):
        '''Create a variable object, specifying its name (a
        string) and domain of values.
        '''
        self._name = name                #text name for variable
        self._dom = list(domain)         #Make a copy of passed domain
        self._curdom = list(domain)      #using list
        self._value = None

    def __str__(self):
        return "Variable {}".format(self._name)

    def domain(self):
        '''return copy of variable domain'''
        return(list(self._dom))

    def domainSize(self):
        '''Return the size of the domain'''
        return(len(self.domain()))

    def resetDomain(self, newdomain):
        '''reset the domain of this variable'''
        self._dom = newdomain

    def getValue(self):
        '''return assigned value of variable; if not assigned, return None'''
        return self._value

    def setValue(self, value):
        '''assign value to variable'''
        if value != None and not value in self._dom:
            print("Error: tried to assign value {} to variable {} that is not in {}'s domain".format(value,self._name,self._name))
        else:
            self._value = value    

    def unAssign(self):
        '''remove variable assignment; reset to None'''
        self.setValue(None)

    def isAssigned(self):
        '''return true if variable is assigned to a value'''
        return self.getValue() != None

    def name(self):
        '''get variable name'''
        return self._name

    def curDomain(self):
        '''return copy of variable current domain. But if variable is assigned
           return just its assigned value (this makes implementing hasSupport easier'''
        if self.isAssigned():
            return([self.getValue()])
        return(list(self._curdom))

    def curDomainSize(self):
        '''Return the size of the current domain'''
        if self.isAssigned():
            return(1)
        return(len(self._curdom))

    def inCurDomain(self, value):
        '''check if value is in current domain'''
        if self.isAssigned():
            return(value==self.getValue())
        return(value in self._curdom)

    def pruneValue(self, value, reasonVar, reasonVal):
        '''Remove value from current domain'''
        try:
            self._curdom.remove(value)
        except:
            print("Error: tried to prune value {} from variable {}'s domain, but value not present!".format(value, self._name))
        dkey = (reasonVar, reasonVal)
        if not dkey in Variable.undoDict:
            Variable.undoDict[dkey] = []
        Variable.undoDict[dkey].append((self, value))

    def restoreVal(self, value):
        '''add value back to domain of variable'''
        self._curdom.append(value)

    def restoreCurDomain(self):
        '''reset domain to original '''
        self._curdom = self.domain()

    def reset(self):
        '''reset variable by removing assignment and restoring domain'''
        self.restoreCurDomain()
        self.unAssign()

    def dumpVar(self):
        '''print all variable information'''
        print("Variable\"{}={}\": Dom = {}, CurDom = {}".format(self._name, self._value, self._dom, self._curdom))

    @staticmethod
    def clearUndoDict():
        undoDict = dict()

    @staticmethod
    def restoreValues(reasonVar, reasonVal):
        dkey = (reasonVar, reasonVal)
        if dkey in Variable.undoDict:
            for (var,val) in Variable.undoDict[dkey]:
                var.restoreVal(val)
            del Variable.undoDict[dkey]

#implement various types of constraints
class Constraint:
    '''Base class for defining constraints. Each constraint can check if
       it has been satisfied, so each type of constraint must be a
       different class. For example a constraint of notEquals(V1,V2)
       must be a different class from a constraint of
       greaterThan(V1,V2), as they must implement different checks of
       satisfaction.

       However one can define a class of general table constraints, as
       below, that can capture many different constraints.

       On initialization the constraint's name can be given as well as
       the constraint's scope. IMPORTANT, the scope is ordered! E.g.,
       the constraint greaterThan(V1,V2) is not the same as the
       contraint greaterThan(V2,V1).
    '''
    def __init__(self, name, scope):
        '''create a constraint object, specify the constraint name (a
        string) and its scope (an ORDERED list of variable
        objects).'''
        self._scope = list(scope)
        self._name = "baseClass_" + name  #override in subconstraint types!

    def scope(self):
        '''scope is an ordered list of variables involved in constraint'''
        return list(self._scope)

    def arity(self):
        '''Check how many variables are involved in this constraint object'''
        return len(self._scope)

    def numUnassigned(self):
        '''Check which variables are assigned in constraint scope'''
        i = 0
        for var in self._scope:
            if not var.isAssigned():
                i += 1
        return i

    def unAssignedVars(self):
        '''return list of variables in constraint scope that are not assigned yet'''
        return [var for var in self.scope() if not var.isAssigned()]

    def name(self):
        '''return constraint object name'''
        return self._name

    def __str__(self):
        return "Cnstr_{}({})".format(self.name(), map(lambda var: var.name(), self.scope()))

    def printConstraint(self):
        '''print constraint information'''
        print("Cons: {} Vars = {}".format(
            self.name(), [v.name() for v in self.scope()]))


#object for holding a constraint problem
class CSP:
    '''CSP class groups together a set of variables and a set of
       constraints to form a CSP problem. Provides a usesful place
       to put some other functions that depend on which variables
       and constraints are active'''

    def __init__(self, name, variables, constraints):
        '''create a CSP problem object passing it a name, a list of
           variable objects, and a list of constraint objects'''
        self._name = name
        self._variables = variables
        self._constraints = constraints

        #some sanity checks
        varsInCnst = set()
        for c in constraints:
            varsInCnst = varsInCnst.union(c.scope())
        for v in variables:
            if v not in varsInCnst:
                print("Warning: variable {} is not in any constraint of the CSP {}".format(v.name(), self.name()))
        for v in varsInCnst:
            if v not in variables:
                print("Error: variable {} appears in constraint but specified as one of the variables of the CSP {}".format(v.name(), self.name()))

        self.constraints_of = [[] for i in range(len(variables))]
        for c in constraints:
            for v in c.scope():
                # v is a variable involved in constraint (str)
                i = variables.index(v) # get index of variable occurance in variable object list (match)
                self.constraints_of[i].append(c)
                # constraints_of is a matrix of constraint objects, where the index of each row (i) corresponds to the index of the variable 
                # in the 'variables' object list that the constraint is involved in 

    def name(self):
        '''return name of CSP'''
        return self._name

    def variables(self):
        '''return list of variables that are involved in problem'''
        return list(self._variables)

    def constraints(self):
        '''return list of constraints that are involved in problem'''
        return list(self._constraints)

    def constraintsOf(self, var):
        '''return constraints with var in their scope'''
        try:
            i = self.variables().index(var)
            return list(self.constraints_of[i])
        except:
            print("Error: tried to find constraint of variable {} that isn't in this CSP {}".format(var, self.name()))

    def unAssignAllVars(self):
        '''unassign all variables'''
        for v in self.variables():
            v.unAssign()

    def check(self, solutions):
        '''each solution is a list of (var, value) pairs. Check to see
           if these satisfy all the constraints. Return list of
           erroneous solutions'''

        #save values to restore later
        current_values = [(var, var.getValue()) for var in self.variables()]
        errs = []

        for s in solutions:
            s_vars = [var for (var, val) in s]

            if len(s_vars) != len(self.variables()):
                errs.append([s, "Solution has incorrect number of variables in it"])
                continue

            if len(set(s_vars)) != len(self.variables()):
                errs.append([s, "Solution has duplicate variable assignments"])
                continue

            if set(s_vars) != set(self.variables()):
                errs.append([s, "Solution has incorrect variable in it"])
                continue

            for (var, val) in s:
                var.setValue(val)

            for c in self.constraints():
                if not c.check():
                    errs.append([s, "Solution does not satisfy constraint {}".format(c.name())])
                    break

        for (var, val) in current_values:
            var.setValue(val)

        return errs
    
    def __str__(self):
        return "CSP {}".format(self.name())

class TableConstraint(Constraint):
    '''General type of constraint that can be use to implement any type of
       constraint. But might require a lot of space to do so.

       A table constraint explicitly stores the set of satisfying
       tuples of assignments.'''

    def __init__(self, name, scope, satisfyingAssignments):
        '''Init by specifying a name and a set variables the constraint is over.
           Along with a list of satisfying assignments.
           Each satisfying assignment is itself a list, of length equal to
           the number of variables in the constraints scope.
           If sa is a single satisfying assignment, e.g, sa=satisfyingAssignments[0]
           then sa[i] is the value that will be assigned to the variable scope[i].


           Example, say you want to specify a constraint alldiff(A,B,C,D) for
           three variables A, B, C each with domain [1,2,3,4]
           Then you would create this constraint using the call
           c = TableConstraint('example', [A,B,C,D],
                               [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4],
                                [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                                [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4],
                                [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                                [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                                [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                                [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3],
                                [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]])
          as these are the only assignments to A,B,C respectively that
          satisfy alldiff(A,B,C,D)
        '''

        Constraint.__init__(self,name, scope)
        self._name = "TableCnstr_" + name
        self.satAssignments = satisfyingAssignments

    def check(self):
        '''check if current variable assignments are in the satisfying set'''
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return assignments in self.satAssignments

    def hasSupport(self, var,val):
        '''check if var=val has an extension to an assignment of all variables in
           constraint's scope that satisfies the constraint. Important only to
           examine values in the variable's current domain as possible extensions'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        vindex = self.scope().index(var)
        found = False
        for assignment in self.satAssignments:
            if assignment[vindex] != val:
                continue   #this assignment can't work it doesn't make var=val
            found = True   #Otherwise it has potential. Assume found until shown otherwise
            for i, v in enumerate(self.scope()):
                if i != vindex and not v.inCurDomain(assignment[i]):
                    found = False  #Bummer...this assignment didn't work it assigns
                    break          #a value to v that is not in v's curDomain
                                   #note we skip checking if val in in var's curDomain
            if found:     #if found still true the assigment worked. We can stop
                break
        return found     #either way found has the right truth value

class NValuesConstraint(Constraint):
    '''NValues constraint over a set of variables.  Among the variables in
       the constraint's scope the number that have been assigned
       values in the set 'required_values' is in the range
       [lower_bound, upper_bound] (lower_bound <= #of variables
       assigned 'required_value' <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [1,4], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 1 or 4, and at most 3
       of them have been assigned the value 1 or 4.

    '''

    def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._required = required_values
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        rv_count = 0

        #print "Checking {} with assignments = {}".format(self.name(), assignments)

        for v in assignments:
            if v in self._required:
                rv_count += 1

        #print "rv_count = {} test = {}".format(rv_count, self._lb <= rv_count and self._ub >= rv_count)

        return self._lb <= rv_count and self._ub >= rv_count

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in

        #define the test functions for findvals
        def valsOK(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy this sum constraint'''
            rv_count = 0
            vals = [val for (var, val) in l]
            for v in vals:
                if v in self._required:
                    rv_count += 1
            least = rv_count + self.arity() - len(vals)
            most =  rv_count
            return self._lb <= least and self._ub >= most
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsOK, valsOK)
        return x

class IfAllThenOneConstraint(Constraint):
    '''if each variable in left_side equals each value in left_values 
    then one of the variables in right side has to equal one of the values in right_values. 
    hasSupport tested only, check() untested.'''
    '''left_side + right_side sum to the scope of the constraint'''

    def __init__(self, name, left_side, right_side, left_values, right_values):
        Constraint.__init__(self,name, left_side+right_side)
        self._name = "IfAllThenOne_" + name
        self._ls = left_side
        self._rs = right_side
        self._lv = left_values
        self._rv = right_values

'''****************************************************************************Program Functions**********************************************************************************************'''

def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporing tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    # print "==>findvars([",
    # for v in remainingVars: print v.name(), " ",
    # print "], [",
    # for x,y in assignment: print "({}={}) ".format(x.name(),y),
    # print ""

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False

def board_creation(filename):

    f = open(filename)
    lines = f.readlines()
    count = 0
    board = []
    for l in lines:
        if count == 0:
            row_const = [int(x) for x in l.rstrip()]
            count += 1
        elif count == 1:
            col_const = [int(x) for x in l.rstrip()]
            count += 1
        elif count == 2:
            ship_const = [int(x) for x in l.rstrip()]
            count += 1
        else:
            board += [[str(x) for x in l.rstrip()]]
            count += 1
    f.close()

    return board, row_const, col_const, ship_const

def variable_creation(board):
    '''Using the cell based approach, create variable objects for each square of the board, specifying its domain'''
    N = len(board[0])
    varlist = []
    var_dict = {}
    # i = row, j = column
    for i in range(0, N):
        for j in range(0, N):
            if board[i][j] != '0':
                # board piece already assigned (given as hint)
                v = Variable(str(i*N+j), [board[i][j]])
            else:
                # board square is 0 -- no hint given
                v = Variable(str(i*N+j), ['S', '.', '<', '>', '^', 'v', 'M'])

            # Create variable object list, as well as dictionary of variable objects, addressable by its name
            varlist.append(v)
            var_dict[str(i*N+j)] = v
    
    return varlist, var_dict

def constraint_creation(board, row_const, col_const, var_dict):
    '''Using the variable objects, create constraint objects based on row constraints, column constraints and water constraint'''
    N = len(board[0])
    constraints = []

    # Define row and column constraints
    for i in range(0, N):
        row_i = []
        col_i = []
        ships = ['S', '.', '<', '>', '^', 'v', 'M']
        for j in range(0, N):
            #Create row and column lists, and add the variable objects for row i and column j to the lists
            row_i.append(var_dict[str(i*N+j)])
            col_i.append(var_dict[str(i+j*N)])

        # Create row and column constraints for ships using lists as scope
        constraints.append(NValuesConstraint('row_'+str(i), row_i, ships, 0, row_const[i]))
        constraints.append(NValuesConstraint('col_'+str(i), col_i, ships, 0, col_const[i]))

        '''Need to add water constraint and implement checks for edge cases and proper ship formation'''

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
    (board, row_const, col_const, ship_const) = board_creation(args.inputfile)
    print(row_const)
    print(col_const)
    
    