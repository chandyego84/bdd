from pyeda.inter import *
from pyeda.boolalg.bdd import BDDConstant

### CONSTANTS , GLOBAL VARS
NUM_NODES = 32

###
# Let G be a graph over 32 nodes (node 0, ..., node 31)
# For all nodes i,j there is a node i to node j iff:
    # (i + 3) % 32 == j % 32 OR (i + 8) % 32 = j % 32.

# We define even and prime nodes:
    # Node i is even if i is an even number: {0, 2, 4, ..., 30}
    # Node i is prime if i is a prime number: {3, 5, 7, 11, 13, 17, 19, 23, 29, 31}

# We use R to denote the set of all edges in G.
###

'''
Returns true if edge condition between two nodes is met
'''
def edgeConditionOne(i, j):
    return (i + 3) % NUM_NODES == j % NUM_NODES

'''
Returns true if edge condition between two nodes is met
'''
def edgeConditionTwo(i, j):
    return (i + 8) % NUM_NODES == j % NUM_NODES

'''
Converts decimal num to its binary expression of length n bits
'''
def decToBinOfNBits(num, n = 5):
    return bin(num)[2:].zfill(n)

"""
Test if the pair of nodes (node_i, node_j) satisfies the BDD.
Returns True if the pair satisfies RR, False otherwise.
"""
def testPairSatisfy(node_i, node_j, BDD, xx_vars, yy_vars):
    # Convert node_i and node_j to binary strings
    bin_node_i = decToBinOfNBits(node_i)
    bin_node_j = decToBinOfNBits(node_j)

    # Create a Boolean assignment for RR's variables
    assignment = {}
    for i, bit in enumerate(bin_node_i):
        assignment[xx_vars[i]] = bool(int(bit))
    for i, bit in enumerate(bin_node_j):
        assignment[yy_vars[i]] = bool(int(bit))

    # Evaluate RR with the assignment
    truth_value = BDD.restrict(assignment)

    # If truth_value is a constant BDD, check its value
    if isinstance(truth_value, BDDConstant):
        return truth_value.value

    # Otherwise, check if it is not the constant False
    return not truth_value.is_const_false()

"""
Test if a number satisfies the BDD.
Returns True if the number satisfies the BDD, False otherwise.
"""
def testNumberSatisfy(num, BDD, vars):
    # Convert the number to a binary string
    bin_num = decToBinOfNBits(num)

    # Create a boolean assignment for BDD's variables
    assignment = {}
    for i, bit in enumerate(bin_num):
        assignment[vars[i]] = bool(int(bit))
    
    # Evalute BDD with assignment
    truth_value = BDD.restrict(assignment)

    # If truth_value is a constant BDD, check value
    if isinstance(truth_value, BDDConstant):
        return truth_value.value
    
    return not truth_value.is_const_false()


# set of node pairs satisfying the edge relation
R = []
for i in range(NUM_NODES):
    for j in range(NUM_NODES):
        if (edgeConditionOne(i, j) or edgeConditionTwo(i, j)):
            # create pair (binary rep) for nodes that make an edge
            node_i = decToBinOfNBits(i)
            node_j = decToBinOfNBits(j)
            R.append((node_i, node_j))

###
# Every finite set can be coded as a BDD.
# Decide whethere the following is true:
    # (StatementA) for each node u in [PRIME], there is a node v in [EVEN] such that
    # u can reach v in a positive even number of steps.
###

### Obtain BDDs RR, EVEN, PRIME, for finite sets R, [even], [prime] ###

### BDD VARS ###
xx0 = bddvar('xx0')
xx1 = bddvar('xx1')
xx2 = bddvar('xx2')
xx3 = bddvar('xx3')
xx4 = bddvar('xx4')

yy0 = bddvar('yy0')
yy1 = bddvar('yy1')
yy2 = bddvar('yy2')
yy3 = bddvar('yy3')
yy4 = bddvar('yy4')

zz0 = bddvar('zz0')
zz1 = bddvar('zz1')
zz2 = bddvar('zz2')
zz3 = bddvar('zz3')
zz4 = bddvar('zz4')
### BDD VARS ###

#------------ Create a long boolean expression for R ------------#
booleanExpr = ""
for index, node_pair in enumerate(R):
    node_i = node_pair[0]
    node_j = node_pair[1]
    exp_ij = ""

    # Construct expression for node_i
    for n in range(len(node_i)):
        if not int(node_i[n]):  # indicates binary 0
            exp_ij += '~'
        exp_ij += f"xx{n} & "  

    # Construct expression for node_j
    for p in range(len(node_j)):
        if not int(node_j[p]):  # indicates binary 0
            exp_ij += ' ~'

        exp_ij += f"yy{p}"  

        if p < (len(node_j) - 1):  # only add & if not at last digit of node_j
            exp_ij += " & "

    # Combine expressions for node_i and node_j
    booleanExpr += f"{exp_ij}"

    if index < len(R) - 1:  # if not the last node pair
        booleanExpr += " | "  # OR

# Create BDD RR
exp = expr(booleanExpr)
RR = expr2bdd(exp)

#------------ Create a long boolean expression for EVEN numbers (over yy vars) ------------#
EVEN = [decToBinOfNBits(num) for num in range(0, NUM_NODES, 2)] # get even numbers from 0 - 31

booleanExpr = ""
for index, num in enumerate(EVEN):
    for n in range(len(num)):
        if not int(num[n]): # indicates binary 0
            booleanExpr += " ~"
        
        booleanExpr += f"yy{n}"

        if n < (len(num) - 1): # only add & if not at last digit of the binary num
            booleanExpr += " & "
    
    if index < (len(EVEN) - 1): # if not the last binary number
        booleanExpr += " | "

# Create BDD EVEN_BDD
exp = expr(booleanExpr)
EVEN_BDD = expr2bdd(exp)

#------------ Create a long boolean expression for PRIME numbers ------------#
PRIME = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31] # explicit list of prime numbers
PRIME = [decToBinOfNBits(num) for num in PRIME]

booleanExpr = ""
for index, num in enumerate(PRIME):
    for n in range(len(num)):
        if not int(num[n]): # indicates binary 0
            booleanExpr += " ~"
        
        booleanExpr += f"xx{n}"

        if n < (len(num) - 1): # only add & if not at last digit of binary num
            booleanExpr += " & "
        
    
    if index < (len(PRIME) - 1):
        booleanExpr += " | "

# Create BDD for PRIME numbers
exp = expr(booleanExpr)
PRIME_BDD = expr2bdd(exp)

#------------ Compute BDD RR2 for the set RoR, from BDD RR ------------#
###
# RR2 encodes the set of node pairs such that one can reach the other in two steps.
###

### There exists a zz1-zz5 such that RR(xx1-xx5; zz1-zz5) and RR(zz1-zz5; yy1-yy5) is true ###
# replace yy1-yy5 with zz1-zz5
BDD1 = RR.compose({yy0: zz0, yy1: zz1, yy2: zz2, yy3: zz3, yy4: zz4})
# replace xx1-xx5 with zz1-zz5
BDD2 = RR.compose({xx0: zz0, xx1: zz1, xx2: zz2, xx3: zz3, xx4: zz4})

# same as existential quntification operator: there exists {zz1, ..., zz4} in f
RR2 = (BDD1 & BDD2).smoothing((zz0, zz1, zz2, zz3, zz4))

#------------ Compute BDD transitive closure RR2star of RR2. RR2star encodes set of all node pairs 
#------------ such that one can reach the other in a positive even number of steps. ------------#
H = RR2
while True:
    H_prime = H
    n1 = H_prime.compose({yy0: zz0, yy1: zz1, yy2: zz2, yy3: zz3, yy4: zz4})
    n2 = RR2.compose({xx0: zz0, xx1: zz1, xx2: zz2, xx3: zz3, xx4: zz4})
    nxtFormula = (n1 & n2).smoothing((zz0, zz1, zz2, zz3, zz4))
    
    H = H_prime | nxtFormula

    if (H.equivalent(H_prime)):
        # Must be true eventually:
        # For all nodes u, v in graph: 
        # u can reach v in 1 or more steps iff u can reach v within n steps
        break

RR2_STAR = H

#------------ StatementA: For all u, (PRIME(u) -> There exists v, EVEN(v) & RRstar(u, v))
### Check if this statement is true or not. ###

CONCLUSION = EVEN_BDD & RR2_STAR # BDD for conclusion of statement

# Statement A = X -> Y == ~X or Y
STATEMENT = ~PRIME_BDD | CONCLUSION.smoothing((yy0, yy1, yy2, yy3, yy4)) # BDD for Statement A

### BDD Tests -- Checks whether or not certain nodes satisfy created BDDs. ###
xx_vars = [xx0, xx1, xx2, xx3, xx4]
yy_vars = [yy0, yy1, yy2, yy3, yy4]

print(f"RR(27, 3) -- Expected: 1, Actual: {testPairSatisfy(27, 3, RR, xx_vars, yy_vars)}")
print(f"RR(16, 20) -- Expected: 0, Actual: {testPairSatisfy(16, 20, RR, xx_vars, yy_vars)}")
print(f"EVEN_BDD(14) -- Expected: 1, Actual: {testNumberSatisfy(14, EVEN_BDD, yy_vars)}")
print(f"EVEN_BDD(13) -- Expected: 0, Actual: {testNumberSatisfy(13, EVEN_BDD, yy_vars)}")
print(f"PRIME_BDD(7) -- Expected: 1, Actual: {testNumberSatisfy(7, PRIME_BDD, xx_vars)}")
print(f"PRIME_BDD(2) -- Expected: 0, Actual: {testNumberSatisfy(2, PRIME_BDD, xx_vars)}")
print(f"RR2(27, 6) -- Expected: 1, Actual: {testPairSatisfy(27, 6, RR2, xx_vars, yy_vars)}")
print(f"RR2(27, 9) -- Expected: 0, Actual: {testPairSatisfy(27, 9, RR2, xx_vars, yy_vars)}")
print(f"Number of satisfying inputs on RR2_STAR: {RR2_STAR.satisfy_count()}")
print("---------------------------------------------")
print(f"Statement A: For all u, (PRIME(u) -> There exists v, EVEN(v) & RRstar(u, v))")
print(f"Statement A: {STATEMENT.equivalent(True)}")

assertion = ""
if (str(STATEMENT.satisfy_one()) == "{}"):
    assertion = "tautology"
else:
    assertion = "contradiction"

print(f"Based on the BDD for Statement A, Statement A is a {assertion}")
### BDD Tests ###