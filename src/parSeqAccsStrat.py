import itertools
from itertools import combinations
from numpy import infty
import MyConfig
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
    
    def exhaustSearchForOptSol (self, q, missp, T, numRsrc):
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
                    if not (all(x >= 0 for x in sol)): # illegal sol --> skip
                             continue
                    solCost = self.calcSolCost(sol)
                    if (solCost < optSolCost):
                        optSol     = sol.copy ()
                        optSolCost = solCost 
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
    
    def greedyAlg (self, q, missp, T, numRsrc):
        """
        Finds a solution using a greedy algorithm.
        The alg' begins with the solution [0] (don't accs any rsrc). 
        At each step, the algorithm greedily accesses one additional rsrc, in a way that minimizes the cost.
        The alg' assumes that once it's not beneficial to add a rsrc, we've reached an optimal sol. 
        Returns [greedySol, greedyCost], where greedySol is the solution vector, and greedyCost is its (expected) cost.  
        """
        if T==0: # If the # of time slots is 0, the sol is empty, and its cost is the missp.
            return [[], missp]
        
        curSol             = [0] # access no resources. 
        self.greedySol     = curSol.copy () # default local opt sol 
        self.greedySolCost = self.calcSolCost(curSol)
    
        while (sum (curSol) < maxNumRsrc):
            self.updatedGreedySol = False
            if (curSol==[0]): # handle first the special case of a solution that doesn't accs any resource.
                curSol  = [1]
                solCost = self.calcSolCost(curSol)
                self.updateGreedySol (curSol)
                continue
            for slot in range (len(curSol)): # Try to add 1 to the num of rsrcs accessed in the cur sol, and check whether this reduces the sol's cost
                suggestedSol        = curSol.copy ()
                suggestedSol[slot] += 1
                self.updateGreedySol (suggestedSol)
            if (len(curSol) < T): # If not all slots are used, try to add 1 to the first slot
                suggestedSol = curSol.copy ()
                suggestedSol.append (1) # we add only when all other slots are 1. Hence, we can use "append" instead of adding 1 before the first used slot.
                self.updateGreedySol (suggestedSol)
            curSol = self.greedySol.copy ()
            if (not(self.updatedGreedySol)): # didn't decrease the cost for all options of incrementing the sol size by 1 (trying 1 more rsrc w.r.t. the previous opt sol). Hence, adding even more rsrcs is useless.
                break
        return [self.greedySol, self.greedySolCost]

my_parSeqAccsStrat = parSeqAccsStrat ()
resFile = open ('../res/parSeqAccsHomo.txt', 'w')
<<<<<<< HEAD
# printf (resFile, '// gSol, oSol are the greedy solution, and optimal solution, resp.\n\n')
=======
>>>>>>> a79118e8dce55669064679e47d49f21ccb7f8041
for q in [0.1*i for i in range (1, 10)]:
    for missp in [5, 10, 100, 500]:
        for T in range (1, 11):
            for maxNumRsrc in range (3, 10):
                if T>maxNumRsrc:
                    continue
                printf (resFile, '// R={}, T={}, q={:.01}, missp={}\n' .format (maxNumRsrc, T, q, missp))
<<<<<<< HEAD
                [greedySol, greedySolCost] = my_parSeqAccsStrat.greedyAlg ()
                [optSol,    optSolCost   ] = my_parSeqAccsStrat.exhaustSearchForOptSol ()
                if greedySolCost!=optSolCost:
                    print ('q={}, missp={}, R={}, T={}, greedySol={}, greedyCost={}, optSol={}, optCost={}' .format 
                           (q, missp, maxNumRsrc, T, greedySol, greedySolCost, optSol, optSolCost))
                printf (resFile, '{}\n' .format (optSol))
=======
                [greedySol, greedySolCost] = my_parSeqAccsStrat.greedyAlg               (q=q, missp=missp, T=T, numRsrc=maxNumRsrc)
                [optSol,    optSolCost   ] = my_parSeqAccsStrat.exhaustSearchForOptSol  (q=q, missp=missp, T=T, numRsrc=maxNumRsrc)
                if greedySolCost!=optSolCost:
                    print ('q={}, missp={}, R={}, T={}, greedySol={}, greedyCost={}, optSol={}, optCost={}' .format 
                           (q, missp, maxNumRsrc, T, greedySol, greedySolCost, optSol, optSolCost))
                printf (resFile, '{}\n' .format (optSol))
>>>>>>> a79118e8dce55669064679e47d49f21ccb7f8041
