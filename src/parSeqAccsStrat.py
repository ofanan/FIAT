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

    def updateOptSol (self, sol):
        """
        check a given solution. If its cost < self.optSol, update self.optSol and self.minCost accordingly. 
        """
        solCost    = self.calcSolCost(sol)
        if (solCost < self.minCost):
            self.minCost = solCost
            self.optSol  = sol.copy ()
            print ('optSol={}, minCost={}' .format (self.optSol, self.minCost))
        
    
    def greedySearchForOptSol (self):
        curStepSol      = [0]
        self.optSol     = curStepSol.copy ()
        self.minCost    = self.calcSolCost(curStepSol)
        print ('optSol={}, minCost={}' .format (self.optSol, self.minCost))
    
        while (sum (curStepSol) < numRsrc):
            if (curStepSol==[0]):
                curStepSol = [1]
                solCost    = self.calcSolCost(curStepSol)
                self.updateOptSol (curStepSol)
            for slot in range (len(curStepSol)):
                suggestedSol        = curStepSol.copy ()
                suggestedSol[slot] += 1
                self.updateOptSol (curStepSol)
            if (len(curStepSol) < T):
                suggestedSol = curStepSol.copy ()
                suggestedSol.append (1)
                self.updateOptSol (curStepSol)
            curStepSol = self.optSol.copy ()
            print ('curStepSol={}. sum={}' .format (curStepSol, sum (curStepSol)))


q       = 0.2 # prob' of failure
missp   = 2
numRsrc = 5 # num of balls
T = 3  # number of bins

my_parSeqAccsStrat = parSeqAccsStrat () 
my_parSeqAccsStrat.greedySearchForOptSol ()
# exhaustSearchForOptSol ()