import itertools
from itertools import combinations
from numpy import infty

q       = 0.5 # prob' of failure
missp   = 100
numRsrc = 5
numUsedTimeSlots = 5  # number of balls

def exhaustSearchForOptSol ():
    for numUsedTimeSlots in range(1, numRsrc+1): # iterate over all possible combinations
        minCost = float ('inf')
        optSol  = None
        for c in combinations(range(1, numRsrc + numUsedTimeSlots), numUsedTimeSlots - 1):
            sol = [b - a - 1 for a, b in zip((-1,) + c, c + (numRsrc + numUsedTimeSlots - 1,))]
            if not (all(x > 0 for x in sol)): # illegal sol --> skip
                continue
            solCost = calcSolCost(sol)
            if (solCost < minCost):
                optSol  = sol
                minCost = solCost 
    print ('optSol={}, minCost={}' .format (optSol, minCost))

def calcSolCost (sol):
    solCost = sol[-1] + q**sol[-1] * missp
    sol.pop()
    for sol_t in reversed (sol):
        solCost = sol_t + q**sol_t * solCost
    return solCost 

# def exhaustSearchForOptSol (solSize = 2):
#     if (solSize> numRsrc):
#         MyConfig.error ('solSize should be <= num o frsrcs, which is {}' .format (numRsrc))


exhaustSearchForOptSol ()