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
Test if the pair of nodes (node_i, node_j) satisfies the BDD RR.
Returns True if the pair satisfies RR, False otherwise.
"""
def testPairSatisfy(node_i, node_j, RR, xx_vars, yy_vars):
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
    truth_value = RR.restrict(assignment)

    # If truth_value is a constant BDD, check its value
    if isinstance(truth_value, BDDConstant):
        return truth_value.value

    # Otherwise, check if it is not the constant False
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

# Create a long boolean expression for R
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

### RR Tests ###
xx_vars = [xx0, xx1, xx2, xx3, xx4]
yy_vars = [yy0, yy1, yy2, yy3, yy4]

bin_27 = decToBinOfNBits(27)
bin_3 = decToBinOfNBits(3)
bin_16 = decToBinOfNBits(16)
bin_20 = decToBinOfNBits(20)

print(f"RR(27, 3) -- Expected: 1, Actual: {testPairSatisfy(27, 3, RR, xx_vars, yy_vars)}")
print(f"RR(16, 20) -- Expected: 0, Actual: {testPairSatisfy(16, 20, RR, xx_vars, yy_vars)}")
### RR Tests ###