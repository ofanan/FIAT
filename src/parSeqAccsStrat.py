import itertools
from itertools import combinations
from numpy import infty

class parSeqAccsStrat (object):

    def __init__ (self):
        return
    
    def calcSolCost (self, sol):
        sol = sol.copy() # as sol is modified by this func, we copy it to a local var
        solCost = sol[-1] + q**sol[-1] * missp
        sol.pop()
        for sol_t in reversed (sol):
            solCost = sol_t + q**sol_t * solCost
        return solCost 
    
    def exhaustSearchForOptSol (self):
        for numUsedTimeSlots in range(1, numRsrc+1): # iterate over all possible combinations
            if (numUsedTimeSlots > T):
                break
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
    
    def greedySearchForOptSol (self):
        curStepSol      = [0]
        optSol     = curStepSol.copy ()
        minCost    = self.calcSolCost(curStepSol)
        print ('suggestedSol={}, cost={}' .format (optSol, minCost))
    
        while (sum (curStepSol) < numRsrc):
            if (curStepSol==[0]):
                curStepSol = [1]
                solCost    = self.calcSolCost(curStepSol)
                if (solCost < minCost):
                    minCost = solCost
                    optSol  = curStepSol.copy ()
                    print ('suggestedSol={}, cost={}' .format (optSol, solCost))
                    continue
                else:
                    MyConfig.error ('cheapest sol is [0]') 
            for slot in range (len(curStepSol)):
                suggestedSol        = curStepSol.copy ()
                suggestedSol[slot] += 1
                solCost             = self.calcSolCost(suggestedSol)
                print ('suggestedSol={}, cost={}' .format (suggestedSol, solCost))
                if (solCost < minCost):
                    minCost = solCost
                    optSol  = suggestedSol.copy()
                    print ('optSol={}' .format (optSol))
            if (len(curStepSol) < T):
                suggestedSol = curStepSol.copy ()
                suggestedSol.append (1)
                solCost      = self.calcSolCost(suggestedSol)
                print ('suggestedSol={}, cost={}' .format (suggestedSol, solCost))
            if (solCost < minCost):
                minCost = solCost
                optSol  = suggestedSol.copy()
                print ('optSol={}' .format (optSol))
            curStepSol = optSol.copy ()
            print ('curStepSol={}. sum={}' .format (curStepSol, sum (curStepSol)))


q       = 0.2 # prob' of failure
missp   = 10
numRsrc = 5 # num of balls
T = 3  # number of bins

my_parSeqAccsStrat = parSeqAccsStrat () 
my_parSeqAccsStrat.greedySearchForOptSol ()
# exhaustSearchForOptSol ()