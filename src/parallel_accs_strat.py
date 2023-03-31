q       = 0.5 # prob' of failure
missp   = 100
numRsrc = 2

def calcSolCost (sol):
    solCost = sol[-1] + q**sol[-1] * missp
    print (solCost) 
    sol.pop()
    for sol_t in reversed (sol):
        solCost = sol_t + q**sol_t * solCost
        print (solCost) 
        
        
calcSolCost ([1,1,1])