"""
Run a simulation, looping over all requested values of parameters 
(miss penalty, cache sizes, number of caches etc.).
"""
from datetime import datetime
import os, pickle, sys

import MyConfig
import numpy as np
from printf import printf
import DistCacheSimulator as sim
from   tictoc import tic, toc

def main ():
    re_init_after_each_ad = False
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    for trace in ['Wiki', 'Scarab', 'Twitter', 'IBM', 'F2']:   
        for DS_size in [64000]: #[4000, 16000, 64000]:
            max_num_of_req = MyConfig.calc_num_of_req (trace, DS_size)
            requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req) 
            for mode in ['salsa2']:
                for missp in [30, 100, 300]: #[10, 30, 100, 300]:
                    tic()
                    sm = sim.DistCacheSimulator(
                        res_file_name    = mode + ('_re_init_after_each_ad' if re_init_after_each_ad else ''), 
                        trace_name       = trace,
                        mode             = mode,
                        req_df           = requests,
                        client_DS_cost   = DS_cost,
                        missp            = missp,
                        DS_size          = DS_size,
                        min_uInterval    = DS_size/10,
                        re_init_after_each_ad = re_init_after_each_ad,
                        uInterval_factor = 8 if mode.startswith('salsa') else 1,
                        verbose          = [MyConfig.VERBOSE_RES]) #[MyConfig.VERBOSE_DETAILED_LOG_MR])
                    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
                    toc()

def calc_DS_homo_costs (num_of_DSs, num_of_clients):
    """
    Returns a DS_cost matrix, representing an homogeneous access cost of 2 from each client to each DS. 
    """
    DS_cost = np.empty (shape=(num_of_clients,num_of_DSs))
    DS_cost.fill(2)
    return DS_cost

def calc_DS_hetro_costs (num_of_DSs, num_of_clients):
    """
    Returns a DS_cost matrix, where the access cost from client i to DS j is j-i+1  
    """
    DS_cost = np.empty (shape=(num_of_clients,num_of_DSs))
    for i in range (num_of_clients):
        for j in range (i, i + num_of_DSs):
            DS_cost[i][j % num_of_DSs] = j - i + 1
    return DS_cost

def calc_DS_cost (num_of_DSs=3, use_homo_DS_cost = False):
    """
    Returns a DS_cost matrix - either homo' or hetro', by the user's request  
    """
    num_of_clients      = 1 # we currently consider only a single client, looking for data in several caches.
    if (use_homo_DS_cost):
        return calc_DS_homo_costs(num_of_DSs, num_of_clients)
    else:
        return calc_DS_hetro_costs(num_of_DSs, num_of_clients)


def calc_opt_service_cost (accs_cost, comp_miss_cnt, missp, num_of_req):
    """
    Opt's behavior is not depended upon parameters such as the indicaror's size, and miss penalty.
    Hence, it suffices to run Opt only once per trace and network, and then calculate its service cost for other 
    """
    print ('{:.2f}' .format((accs_cost + comp_miss_cnt * missp) / num_of_req))

def calc_opt_service_cost_in_loop ():
    """
    Opt's behavior is not depended upon parameters such as the indicaror's size, and miss penalty.
    Hence, it suffices to run Opt only once per trace and network, and then calculate its service cost for other 
    parameters' values. 
    This function calculates and prints Opt's. 
    """
    for trace in ['F2']:
        for missp in [30, 100, 300]:
            calc_opt_service_cost (accs_cost=65151, comp_miss_cnt=367426, missp=missp, num_of_req=400000)

if __name__ == '__main__':
    # calc_opt_service_cost_in_loop ()
    main ()