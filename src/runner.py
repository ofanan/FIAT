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
import mod_pylru

def run_hetro_costs_sim ():
    """
    Run experiments with 3 DSs, varying miss penalties, and heterogeneous DSs costs.
    """
    min_feasible_uInterval = 10
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    for trace in ['Wiki', 'Scarab', 'F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:     
    # for trace in ['F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:     
    # for trace in ['Wiki']:        
    # for trace in ['Scarab']:       
    # for trace in ['F1']: 
    # for trace in ['F2']: 
    # for trace in ['IBM1']: 
    # for trace in ['IBM7']: 
    # for trace in ['Twitter17']:
    #for trace in ['Twitter45']:
        for DS_size in [4000]: #[4000, 16000, 64000]:
            max_num_of_req = MyConfig.calc_num_of_req (trace) # 500000 #$$$$  
            requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
            for mode in ['salsa_dep2']: #'salsa_dep0', 'fnaa'
                for missp in [300]: #[10, 30, 100, 300]:
                    tic()
                    sm = sim.DistCacheSimulator(
                        # bpe                     = 10, #$$$
                        delta_mode_period_param = 5, # length of "sync periods" of the indicator's scaling alg.
                        full_mode_period_param  = 5, # length of "sync periods" of the indicator's scaling alg.
                        res_file_name           = f'{mode}_{MyConfig.getMachineStr()}',
                        EWMA_alpha_mr0          = 0.5, 
                        EWMA_alpha_mr1          = 0.25, 
                        trace_name              = trace,
                        mode                    = mode,
                        req_df                  = requests,
                        client_DS_cost          = DS_cost,
                        missp                   = missp,
                        DS_size                 = DS_size,
                        min_uInterval           = DS_size/10,
                        re_init_after_each_ad   = False,
                        min_feasible_uInterval  = min_feasible_uInterval,
                        uInterval_factor        = 1 if mode.startswith('salsa') else 1,
                        verbose                 = [MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES],
                        # begin_log_mr_at_req_cnt = 74075,
                        ) # MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES, MyConfig.VERBOSE_DETAILED_LOG_MR
                    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10) 
                    toc()


def run_num_of_DSs_sim ():
    """
    Run experiments with varying num of DSs and homogeneous DSs costs..
    """
    min_feasible_uInterval = 10
    mode = 'opt'
    for num_of_DSs in [3,5,7]:
        DS_cost = calc_DS_cost (num_of_DSs=num_of_DSs, use_homo_DS_cost=False)
        for trace in ['Wiki']:        
        # for trace in ['Scarab']:       
        # for trace in ['F1']: 
        # for trace in ['F2']: 
        # for trace in ['IBM1']: 
        # for trace in ['IBM7']: 
        # for trace in ['Twitter17']:
        # for trace in ['Twitter45']:
            max_num_of_req = MyConfig.calc_num_of_req (trace)  
            requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
            tic()
            sm = sim.DistCacheSimulator(
                res_file_name           = f'{mode}_{MyConfig.getMachineStr()}',
                EWMA_alpha_mr0          = 0.85, 
                EWMA_alpha_mr1          = 0.25, 
                trace_name              = trace,
                mode                    = mode,
                req_df                  = requests,
                client_DS_cost          = DS_cost,
                missp                   = 100,
                DS_size                 = 10000,
                min_uInterval           = 1000,
                uInterval_factor        = 32 if mode.startswith('salsa') else 1,
                verbose                 = [MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES])
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

def run_full_ind_oriented_sim ():
    """
    Run a simulation of a conf' that is very likely to encourage SALSA2 to use full indicators. 
    """
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    max_num_of_req = 500000  
    trace = 'Twitter45'
    requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
    tic()
    sm = sim.DistCacheSimulator(
        res_file_name           = f'salsa2__{MyConfig.getMachineStr()}',
        EWMA_alpha_mr0          = 0.85, 
        EWMA_alpha_mr1          = 0.25, 
        trace_name              = trace,
        mode                    = 'salsa2',
        req_df                  = requests,
        client_DS_cost          = DS_cost,
        missp                   = 100,
        DS_size                 = 4000,
        min_uInterval           = 3000,
        uInterval_factor        = 2,
        bpe                     = 10,
        verbose                 = [MyConfig.VERBOSE_DETAILED_LOG_MR]) #MyConfig.VERBOSE_DETAILED_LOG_MR
    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
    toc()


def run_mr_sim ():
    """
    Run an experiment to measure "mr", namely, the exclusion probabilities.
    """
    min_feasible_uInterval = 10
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    for trace in ['Wiki']: #, 'Wiki', 'F1', 'Twitter45']: #  ], 'IBM7', 'Wiki', 'F1', 'Twitter45']:       # for trace in ['F1', 'IBM1', 'Scarab', 'Wiki', 'Twitter17']:       
        max_num_of_req = MyConfig.calc_num_of_req (trace)  
        requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
        for mode in ['measure_mr_by_fnaa']: #, 'measure_mr_fullKnow', 'measure_mr_by_fnaa', 'measure_mr_by_salsa']: 
            for mr_type in range (1, 2): 
                tic()
                sm = sim.DistCacheSimulator(
                    mr_type                 = mr_type,
                    res_file_name           = '',
                    EWMA_alpha_mr0          = 0.85, 
                    EWMA_alpha_mr1          = 0.25, 
                    trace_name              = trace,
                    mode                    = mode,
                    req_df                  = requests,
                    client_DS_cost          = DS_cost,
                    missp                   = 10,
                    DS_size                 = 16000,
                    min_uInterval           = 3200,
                    bpe                     = 12,
                    uInterval_factor        = 32 if mode.startswith('salsa') else 1,
                    verbose                 = [])
                sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
                toc()
    
if __name__ == '__main__':
    try:
        # run_num_of_DSs_sim ()
        # run_full_ind_oriented_sim ()
        # run_mr_sim ()
        run_hetro_costs_sim ()
    except KeyboardInterrupt:
        print('Keyboard interrupt.')

