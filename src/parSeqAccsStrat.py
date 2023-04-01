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
        optCost = float ('inf')
        optSol  = None
        for numRsrc in range (maxNumRsrc+1):
            for numUsedTimeSlots in range(1, numRsrc+1): # iterate over all possible combinations
                if (numUsedTimeSlots > T):
                    break
                for c in combinations(range(1, numRsrc + numUsedTimeSlots), numUsedTimeSlots - 1):
                    sol = [b - a - 1 for a, b in zip((-1,) + c, c + (numRsrc + numUsedTimeSlots - 1,))]
                    if not (all(x > 0 for x in sol)): # illegal sol --> skip
                        continue
                    solCost = self.calcSolCost(sol)
                    if (solCost < optCost):
                        optSol  = sol.copy ()
                        optCost = solCost 
                        # print ('optSol={}, optCost={}' .format (optSol, optCost))
        print ('real optSol={}, minCost={}' .format (optSol, optCost))

    def updateOptSol (self, sol):
        """
        check a given solution. If its cost < self.optSol, update self.optSol and self.optCost accordingly. 
        """
        solCost    = self.calcSolCost(sol)
        if (solCost < self.optCost):
            self.optCost        = solCost
            self.optSol         = sol.copy ()
            self.updatedOpt     = True
            # self.localOptCost   = sol.copy () # will hold the opt for a concrete sol-size
            # print ('optSol={}, minCost={}' .format (self.optSol, self.optCost))
        
    
    def greedySearchForOptSol (self):
        curSol              = [0]
        self.optSol         = curSol.copy () # default global opt sol 
        self.optCost        = self.calcSolCost(curSol)
        # self.localOptCost   = float ('inf')
        print ('optSol={}, minCost={}' .format (self.optSol, self.optCost))
    
        while (sum (curSol) < maxNumRsrc):
            self.updatedOpt = False
            if (curSol==[0]):
                curSol  = [1]
                solCost = self.calcSolCost(curSol)
                self.updateOptSol (curSol)
                continue
            for slot in range (len(curSol)):
                suggestedSol        = curSol.copy ()
                suggestedSol[slot] += 1
                self.updateOptSol (suggestedSol)
            if (len(curSol) < T):
                suggestedSol = curSol.copy ()
                suggestedSol.append (1)
                self.updateOptSol (suggestedSol)
            curSol = self.optSol.copy ()
            if (not(self.updatedOpt)): # didn't decrease the cost for all options of incrementing the sol size by 1 (trying 1 more rsrc w.r.t. the previous opt sol).
                break
        print ('greedy optSol={}, optCost={}' .format (self.optSol, self.optCost))

q       = 0.1 # prob' of failure
missp   = 200
maxNumRsrc = 5 # num of balls
T = 3  # number of bins

my_parSeqAccsStrat = parSeqAccsStrat () 
my_parSeqAccsStrat.greedySearchForOptSol ()
my_parSeqAccsStrat.exhaustSearchForOptSol ()