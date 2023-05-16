import itertools
from itertools import combinations
from numpy import infty
from printf import printf

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
        Returns [optSol, optSolCost], where optSol is the solution vector, and optSolCost is its (expected) cost.  
        """
        if T==0:
            return [[], missp]
        optSolCost = float ('inf')
        optSol     = None
        for numRsrc in range (maxNumRsrc+1):
            for numUsedTimeSlots in range(1, numRsrc+1): # iterate over all possible combinations
                if (numUsedTimeSlots > T):
                    break
                for c in combinations(range(1, numRsrc + numUsedTimeSlots), numUsedTimeSlots - 1):
                    sol = [b - a - 1 for a, b in zip((-1,) + c, c + (numRsrc + numUsedTimeSlots - 1,))]
                    if not (all(x > 0 for x in sol)): # illegal sol --> skip
                        continue
                    solCost = self.calcSolCost(sol)
                    if (solCost < optSolCost):
                        optSol     = sol.copy ()
                        optSolCost = solCost 
                        # print ('optSol={}, optSolCost={}' .format (optSol, optSolCost))
        # print ('greedySol={}, greedySolCost={}' .format (optSol, optSolCost))
        # Consider the special case of accessing none rsrc
        accsNoneCost = self.calcSolCost ([0])
        if accsNoneCost < optSolCost:
            return [[0], accsNoneCost]
        return [optSol, optSolCost]

    def updateGreedySol (self, sol):
        """
        check a given solution. If its cost < self.greedySol, update self.greedySol and self.greedySolCost accordingly. 
        """
        solCost    = self.calcSolCost(sol)
        if (solCost < self.greedySolCost):
            self.greedySolCost  = solCost
            self.greedySol         = sol.copy ()
            self.updatedGreedySol     = True
    
    def greedyAlg (self):
        """
        Finds a solution using a greedy algorithm.
        The alg' begins with the solution [0] (don't accs any rsrc). 
        At each step, the algorithm greedily accesses one additional rsrc, in a way that minimizes the cost.
        The alg' assumes that once it's not beneficial to add a rsrc, we've reached an optimal sol. 
        Returns [greedySol, greedyCost], where greedySol is the solution vector, and greedyCost is its (expected) cost.  
        """
        if T==0:
            return [[], missp]
        
        curSol             = [0]
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

# p1 = 1/2
# q1 = 1 - p1
# c1 = 4
# p2 = 0.2
# q2 = 1 - p2
# c2 = 1
#
# missp  = 1000
# reward = 1000
#
# sol0 = [0]
# sol1 = [c1]
# sol2 = [c2]
# sol1reward = reward*(1-q1) - c1
# print ('sol1Cost={}, sol1reward={}' .format (sol1Cost, sol1reward))  
# exit ()

# q       = 0.5 # prob' of failure
# missp   = 100
# sol = [1,2] 
# print ('cost of {}={}' .format (sol, my_parSeqAccsStrat.calcSolCost (sol)))
# sol = [2,1] 
# print ('cost of {}={}' .format (sol, my_parSeqAccsStrat.calcSolCost (sol)))
# exit ()


my_parSeqAccsStrat = parSeqAccsStrat ()
resFile = open ('../res/parSeqAccsHomo.txt', 'w')
printf (resFile, '// gSol, oSol are the greedy solution, and optimal solution, resp.\n\n')
for q in [0.1*i for i in range (11)]:
    for missp in [5, 10, 100, 500]:
        for maxNumRsrc in range (1, 10):
          for T in range (1, maxNumRsrc+1):
            [greedySol, greedySolCost] = my_parSeqAccsStrat.greedyAlg ()
            [optSol,    optSolCost   ] = my_parSeqAccsStrat.exhaustSearchForOptSol ()
            if greedySolCost!=optSolCost:
                print ('q={}, missp={}, R={}, T={}, greedySol={}, greedyCost={}, optSol={}, optCost={}' .format 
                       (q, missp, maxNumRsrc, T, greedySol, greedySolCost, optSol, optSolCost))
            printf (resFile, '{}\n' .format (optSol))
