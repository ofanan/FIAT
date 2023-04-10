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
        """
        Finds an optimal solution using an exhaustive search over all feasible solutions.
        A feasible solution is a vector where all entries are strictly positive integers.
        Returns [greedySol, greedySolCost], where greedySol is the solution vector, and greedySolCost is its (expected) cost.  
        """
        greedySolCost = float ('inf')
        greedySol  = None
        for numRsrc in range (maxNumRsrc+1):
            for numUsedTimeSlots in range(1, numRsrc+1): # iterate over all possible combinations
                if (numUsedTimeSlots > T):
                    break
                for c in combinations(range(1, numRsrc + numUsedTimeSlots), numUsedTimeSlots - 1):
                    sol = [b - a - 1 for a, b in zip((-1,) + c, c + (numRsrc + numUsedTimeSlots - 1,))]
                    if not (all(x > 0 for x in sol)): # illegal sol --> skip
                        continue
                    solCost = self.calcSolCost(sol)
                    if (solCost < greedySolCost):
                        greedySol  = sol.copy ()
                        greedySolCost = solCost 
                        # print ('greedySol={}, greedySolCost={}' .format (greedySol, greedySolCost))
        # print ('greedySol={}, greedySolCost={}' .format (greedySol, greedySolCost))
        return [greedySol, greedySolCost]

    def updateGreedySol (self, sol):
        """
        check a given solution. If its cost < self.greedySol, update self.greedySol and self.greedySolCost accordingly. 
        """
        solCost    = self.calcSolCost(sol)
        if (solCost < self.greedySolCost):
            self.greedySolCost  = solCost
            self.greedySol         = sol.copy ()
            self.updatedGreedySol     = True
            # self.localOptCost   = sol.copy () # will hold the opt for a concrete sol-size
            # print ('greedySol={}, minCost={}' .format (self.greedySol, self.greedySolCost))
        
    
    def greedyAlg (self):
        """
        Finds a solution using a greedy algorithm.
        The alg' begins with the solution [0] (don't accs any rsrc). 
        At each step, the algorithm greedily accesses one additional rsrc, in a way that minimizes the cost.
        The alg' assumes that once it's not beneficial to add a rsrc, we've reached an optimal sol. 
        Returns [greedySol, greedyCost], where greedySol is the solution vector, and greedyCost is its (expected) cost.  
        """
        curSol              = [0]
        self.greedySol     = curSol.copy () # default local opt sol 
        self.greedySolCost = self.calcSolCost(curSol)
    
        while (sum (curSol) < maxNumRsrc):
            self.updatedGreedySol = False
            if (curSol==[0]):
                curSol  = [1]
                solCost = self.calcSolCost(curSol)
                self.updateGreedySol (curSol)
                continue
            for slot in range (len(curSol)):
                suggestedSol        = curSol.copy ()
                suggestedSol[slot] += 1
                self.updateGreedySol (suggestedSol)
            if (len(curSol) < T):
                suggestedSol = curSol.copy ()
                suggestedSol.append (1)
                self.updateGreedySol (suggestedSol)
            curSol = self.greedySol.copy ()
            if (not(self.updatedGreedySol)): # didn't decrease the cost for all options of incrementing the sol size by 1 (trying 1 more rsrc w.r.t. the previous opt sol).
                break
        # print ('greedySol={}, greedyCost={}' .format (self.greedySol, self.greedyCost))
        return [self.greedySol, self.greedySolCost]

q       = 0.1 # prob' of failure
missp   = 2000
maxNumRsrc = 10 # num of balls
T = 4  # number of bins

my_parSeqAccsStrat = parSeqAccsStrat () 
[greedySol, greedySolCost] = my_parSeqAccsStrat.greedyAlg ()
[optSol,    optSolCost   ] = my_parSeqAccsStrat.exhaustSearchForOptSol ()
if greedySolCost!=optSolCost:
    print ('greedySol={}, greedyCost={}, optSol={}, optCost={}' .format 
           (greedySol, greedySolCost, optSol, optSolCost))
