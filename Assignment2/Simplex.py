from fractions import Fraction
from warnings import warn

#define Simplex class to implement Simplex algorithm using Tabular method
class Simplex(object):
    def __init__(self, no_of_var, constraints, obj_fun):
        self.no_of_var = no_of_var #defining no of variables
        self.constraints = constraints #defining constraints
        self.objective = obj_fun[0] #getting type of objecting function
        self.obj_fun = obj_fun[1] #getting value of objecting function
        self.coef_Matrix, self.r_Rows, self.no_Of_SVariables, self.no_Of_RVariables = self.createMatrixFromConstraints()
        del self.constraints
        self.basic_Var = [0 for i in range(len(self.coef_Matrix))] #setting the basic variables to zero
        self.phase1() 
        r_Index = self.no_Of_RVariables + self.no_Of_SVariables

        for i in self.basic_Var: #Iterating each basic variable
            if i > r_Index:
                raise ValueError("Infeasible Solution") #solution is not feasible

        self.del_RVariables() #deleting additional variables

        if 'min' in self.objective.lower(): #if the objective function is of minimization
            self.solution = self.objectiveMinimize() #calling the minimize function

        else:
            self.solution = self.Obj_Max() #calling the maximize function
        self.optVal = self.coef_Matrix[0][-1] #storing optimal value

    def createMatrixFromConstraints(self):
        no_Of_SVariables = 0  #number of slack and surplus variables
        no_Of_RVariables = 0  #number of additional variables to balance equality and less than equal to
        for expression in self.constraints: # for each constraint
            if '>=' in expression:
                no_Of_SVariables += 1 #incrementing slack variables

            elif '<=' in expression:
                no_Of_SVariables += 1 #incrementing slack variables
                no_Of_RVariables += 1 #incrementing additional variables

            elif '=' in expression:
                no_Of_RVariables += 1 #incrementing additional variables values
        totalVariables = self.no_of_var + no_Of_SVariables + no_Of_RVariables # total number of variables

        coef_Matrix = [[Fraction("0/1") for i in range(totalVariables+1)] for j in range(len(self.constraints)+1)]
        s_Index = self.no_of_var
        r_Index = self.no_of_var + no_Of_SVariables
        r_Rows = [] # stores the non zero index of r
        for i in range(1, len(self.constraints)+1):
            constraint = self.constraints[i-1].split(' ') # split constraints by space

            for j in range(len(constraint)): # for each constraint

                if '_' in constraint[j]: # if there is an underscore
                    coeff, index = constraint[j].split('_') # get the coefficient and index
                    if constraint[j-1] == '-': # if sign is negative
                        coef_Matrix[i][int(index)-1] = Fraction("-" + coeff[:-1] + "/1")
                    else:
                        coef_Matrix[i][int(index)-1] = Fraction(coeff[:-1] + "/1")

                elif constraint[j] == '<=': # if less than equal to
                    coef_Matrix[i][s_Index] = Fraction("1/1")  # add surplus variable
                    s_Index += 1

                elif constraint[j] == '>=': # if greater than equal to
                    coef_Matrix[i][s_Index] = Fraction("-1/1")  # slack variable
                    coef_Matrix[i][r_Index] = Fraction("1/1")   # r variable
                    s_Index += 1
                    r_Index += 1
                    r_Rows.append(i)

                elif constraint[j] == '=': # if equal to
                    coef_Matrix[i][r_Index] = Fraction("1/1")  # r variable
                    r_Index += 1
                    r_Rows.append(i)

            coef_Matrix[i][-1] = Fraction(constraint[-1] + "/1")

        return coef_Matrix, r_Rows, no_Of_SVariables, no_Of_RVariables

    def phase1(self): #define phase 1 
        r_Index = self.no_of_var + self.no_Of_SVariables #add number of surplus variables
        for i in range(r_Index, len(self.coef_Matrix[0])-1): #iterating for each coefficient
            self.coef_Matrix[0][i] = Fraction("-1/1") #set fraction
        coeff0 = 0
        for i in self.r_Rows: # iterating for each non zero row
            self.coef_Matrix[0] = add_Row(self.coef_Matrix[0], self.coef_Matrix[i]) #add the row
            self.basic_Var[i] = r_Index #store the values of basic variables
            r_Index += 1
        s_Index = self.no_of_var
        for i in range(1, len(self.basic_Var)): #iterating for each basic variable
            if self.basic_Var[i] == 0:
                self.basic_Var[i] = s_Index #store its s_Index
                s_Index += 1

        # run simplex iterations
        key_Col = Max_index(self.coef_Matrix[0]) #getting the maximum index
        condition = self.coef_Matrix[0][key_Col] > 0

        while condition is True:

            keyRow = self.findKeyRow(key_Col = key_Col)
            self.basic_Var[keyRow] = key_Col
            pivot = self.coef_Matrix[keyRow][key_Col]
            self.Normalize_Pivot(keyRow, pivot)
            self.makeKeyColZero(key_Col, keyRow)

            key_Col = Max_index(self.coef_Matrix[0])
            condition = self.coef_Matrix[0][key_Col] > 0

    def findKeyRow(self, key_Col):
        Min_Val = float("inf")
        minI = 0
        for i in range(1, len(self.coef_Matrix)): # for each coefficient
            if self.coef_Matrix[i][key_Col] > 0: # if greater than zero
                val = self.coef_Matrix[i][-1] / self.coef_Matrix[i][key_Col] # divide the maximum column
                if val <  Min_Val: # update the minimum value
                    Min_Val = val
                    minI = i
        if Min_Val == float("inf"):
            raise ValueError("Unbounded Solution") #solution is unbounded
        if Min_Val == 0:
            warn("Dengeneracy") #condition of degeneracy
        return minI

    def Normalize_Pivot(self, keyRow, pivot):
        for i in range(len(self.coef_Matrix[0])): # for each coefficient
            self.coef_Matrix[keyRow][i] /= pivot # divide the pivot

    def makeKeyColZero(self, key_Col, keyRow):
        num_columns = len(self.coef_Matrix[0])
        for i in range(len(self.coef_Matrix)): # for each coefficient
            if i != keyRow:
                factor = self.coef_Matrix[i][key_Col] # get the factor
                for j in range(num_columns): # for each column
                    self.coef_Matrix[i][j] -= self.coef_Matrix[keyRow][j] * factor # multiply the factor

    def del_RVariables(self):
        for i in range(len(self.coef_Matrix)): # for each coefficient
            nonRLength = self.no_of_var + self.no_Of_SVariables + 1 # add the number of variables and surplus variables
            length = len(self.coef_Matrix[i]) # get the length
            while length != nonRLength: # till the length gets equal
                del self.coef_Matrix[i][nonRLength-1] # delete the coefficient
                length -= 1 # reduce the length by 1

    def update_Obj_Fun(self):
        obj_funCoeffs = self.obj_fun.split()
        for i in range(len(obj_funCoeffs)): # for each variable in objective function
            if '_' in obj_funCoeffs[i]: # if there is an underscore
                coeff, index = obj_funCoeffs[i].split('_') # split from underscore
                if obj_funCoeffs[i-1] == '-': # if sign is negative
                    self.coef_Matrix[0][int(index)-1] = Fraction(coeff[:-1] + "/1")
                else:
                    self.coef_Matrix[0][int(index)-1] = Fraction("-" + coeff[:-1] + "/1")

    #checking if alternate solution exists or not
    def CheckAlterSol(self):
        for i in range(len(self.coef_Matrix[0])):
            if self.coef_Matrix[0][i] and i not in self.basic_Var[1:]:
                # warn("Alternative Solution Exists")
                break

    #defining minimizae objective function
    def objectiveMinimize(self):
        self.update_Obj_Fun()

        for row, column in enumerate(self.basic_Var[1:]): #iterating for each basic variables
            if self.coef_Matrix[0][column] != 0:
                self.coef_Matrix[0] = add_Row(self.coef_Matrix[0], multiplyConstRow(-self.coef_Matrix[0][column], self.coef_Matrix[row+1])) # add row

        # run simplex iterations
        key_Col = Max_index(self.coef_Matrix[0]) # get the maximum index
        condition = self.coef_Matrix[0][key_Col] > 0

        while condition is True:

            keyRow = self.findKeyRow(key_Col = key_Col)
            self.basic_Var[keyRow] = key_Col
            pivot = self.coef_Matrix[keyRow][key_Col]
            self.Normalize_Pivot(keyRow, pivot)
            self.makeKeyColZero(key_Col, keyRow)

            key_Col = Max_index(self.coef_Matrix[0])
            condition = self.coef_Matrix[0][key_Col] > 0

        solution = {}
        for i, var in enumerate(self.basic_Var[1:]):
            if var < self.no_of_var:
                solution['x_'+str(var+1)] = self.coef_Matrix[i+1][-1]

        for i in range(0, self.no_of_var):
            if i not in self.basic_Var[1:]:
                solution['x_'+str(i+1)] = Fraction("0/1")
        self.CheckAlterSol()
        return solution

    #defining maximize objective function
    def Obj_Max(self):
        self.update_Obj_Fun()

        for row, column in enumerate(self.basic_Var[1:]): # for each basic variable
            if self.coef_Matrix[0][column] != 0: # if non zero coefficient
                self.coef_Matrix[0] = add_Row(self.coef_Matrix[0], multiplyConstRow(-self.coef_Matrix[0][column], self.coef_Matrix[row+1]))

        # run simplex iterations
        key_Col = Min_index(self.coef_Matrix[0]) # get the maximum index
        condition = self.coef_Matrix[0][key_Col] < 0

        while condition is True: #checking untill condition is true

            keyRow = self.findKeyRow(key_Col = key_Col)
            self.basic_Var[keyRow] = key_Col
            pivot = self.coef_Matrix[keyRow][key_Col]
            self.Normalize_Pivot(keyRow, pivot)
            self.makeKeyColZero(key_Col, keyRow)

            key_Col = Min_index(self.coef_Matrix[0])
            condition = self.coef_Matrix[0][key_Col] < 0

        solution = {}
        for i, var in enumerate(self.basic_Var[1:]):
            if var < self.no_of_var:
                solution['x_'+str(var+1)] = self.coef_Matrix[i+1][-1]

        for i in range(0, self.no_of_var):
            if i not in self.basic_Var[1:]:
                solution['x_'+str(i+1)] = Fraction("0/1")

        self.CheckAlterSol() #check for alternate solutions

        return solution

#adding rows of x and y
def add_Row(x, y):
    row_sum = [0 for i in range(len(x))]
    for i in range(len(x)):
        row_sum[i] = x[i] + y[i]
    return row_sum

#getting the maximum index
def Max_index(x):
    max_i = 0
    for i in range(0, len(x)-1):
        if x[i] > x[max_i]:
            max_i = i

    return max_i

#multiplying each element with constant value
def multiplyConstRow(const, x):
    mul_row = []
    for i in x:
        mul_row.append(const*i)
    return mul_row

#getting the minimum index
def Min_index(x):
    minI = 0
    for i in range(0, len(x)):
        if x[minI] > x[i]:
            minI = i

    return minI

