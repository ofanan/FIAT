"""
Run a simulation, looping over all requested values of parameters 
(miss penalty, cache sizes, number of caches etc.).
"""
from datetime import datetime
import os, pickle, sys

import MyConfig
import numpy as np
from printf import printf
import python_simulator as sim
from   tictoc import tic, toc

def main ():
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    for trace in ['Wiki', 'F1', 'Scarab', 'P3']:
        for DS_size in [4000, 16000, 64000]:
            max_num_of_req = MyConfig.calc_num_of_req (trace, DS_size)
            requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req) 
            for mode in ['fnaa']:
                for missp in [10] if mode=='opt' else [10, 30, 100, 300]:
                    tic()
                    sm = sim.Simulator(
                        res_file_name = mode,
                        trace_name       = trace,
                        mode             = mode,
                        req_df           = requests,
                        client_DS_cost   = DS_cost,
                        missp            = missp,
                        DS_size          = DS_size,
                        min_uInterval    = DS_size/10,
                        uInterval_factor = 4 if mode.startswith('salsa') else 1,
                        verbose          = [MyConfig.VERBOSE_RES])
                    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
                    toc()

def calc_homo_costs (num_of_DSs, num_of_clients):
    """
    Returns a DS_cost matrix, representing an homogeneous access cost of 2 from each client to each DS. 
    """
    DS_cost = np.empty (shape=(num_of_clients,num_of_DSs))
    DS_cost.fill(2)
    return DS_cost

def calc_hetro_costs (num_of_DSs, num_of_clients):
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
        return calc_homo_costs(num_of_DSs, num_of_clients)
    else:
        return calc_hetro_costs(num_of_DSs, num_of_clients)


def calc_opt_service_cost (accs_cost, comp_miss_cnt, missp, num_of_req):
    """
    Opt's behavior is not depended upon parameters such as the indicaror's size, and miss penalty.
    Hence, it suffices to run Opt only once per trace and network, and then calculate its service cost for other 
    parameters' values. Below is the relevant auxiliary code. 
    tot_access_cost= 1805450.0
    comp_miss_cnt = 104710
    num_of_req = 1000000
    for missp in [50, 500]:
    print ("Opt's service cost is ", MyConfig.calc_service_cost_of_opt (tot_access_cost, comp_miss_cnt, missp, num_of_req))
    """
    print ('Opt service cost is ', (accs_cost + comp_miss_cnt * missp) / num_of_req)


    # def 
        # if max_num_of_req==None: # the caller hasn't assign a requested number of requests
        #     if DS_size <= 4000:
        #         max_num_of_req = 400000
        #     elif DS_size <= 16000:
        #         max_num_of_req = 1000000
        #     else:
        #         max_num_of_req = int (float('inf'))
        # else:

# for trace_file_name in [scarab_trace_file_name, P3_trace_file_name, wiki_trace_file_name]:
#     DS_size         = 16000
#     num_of_DSs      = 3
#     max_num_of_req  = 3000000
#     sm = sim.Simulator(res_file_name    = '', 
#                        trace_name       = MyConfig.get_trace_name (trace_file_name),
#                        mode             = 'measure_mr0',
#                        req_df           = MyConfig.gen_requests (trace_file_name, max_num_of_req=max_num_of_req), 
#                        client_DS_cost   = calc_DS_cost (num_of_DSs, use_homo_DS_cost=False),
#                        missp            = 10,
#                        DS_size          = DS_size,
#                        min_uInterval    = DS_size/10,
#                        verbose          = [])
#     sm.run_simulator(interval_between_mid_reports=max_num_of_req)


def run_var_missp_sim (trace, 
                       use_homo_DS_cost = False, 
                       print_est_mr     = True, 
                       max_num_of_req   = None, 
                       missp_vals       = [], 
                       modes            = [], 
                       verbose          = [],
                       DS_size          = 10000
                       ):
    """
    Run a simulation with different miss penalties for the initial table
    """
    if max_num_of_req==None: # the caller hasn't assign a requested number of requests
        max_num_of_req = MyConfig.calc_num_of_req (trace, DS_size)
    else:
        max_num_of_req = max_num_of_req
         
    num_of_DSs  = 3
    requests    = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req) # Generate a dataframe of requests from the input trace file
    num_of_req  = requests.shape[0]
    DS_cost     = calc_DS_cost (num_of_DSs, use_homo_DS_cost)
    
    print("now = ", datetime.now(), 'running var_missp sim')
    for mode in modes:
        for missp in missp_vals: 
            tic()
            sm = sim.Simulator(res_file_name    = mode, 
                               trace_name       = MyConfig.get_trace_name (trace_file_name), 
                               mode             = mode, 
                               req_df           = requests, 
                               client_DS_cost   = DS_cost, 
                               missp            = missp,
                               DS_size          = DS_size,   
                               min_uInterval    = DS_size/10, 
                               uInterval_factor = 4 if mode.startswith('salsa') else 1,
                               verbose          = verbose,
                               )
            sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
            toc()



if __name__ == '__main__':
    main ()