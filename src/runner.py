"""
Run a simulation, looping over all requested values of parameters 
(miss penalty, cache sizes, number of caches etc.).
The cache-selection and content-advertisement alg' is defined by the mode.
The main modes are:
- opt.
- fnaa: the HecSFna alg', defined in [1].
- salsa_dep4: SALSA2 alg', defined in [2].
- Earlier, degenerated versions of SALSA2 (e.g., salsa2, salsa_dep2).
[1] I. Cohen, Gil Einziger, and G. Scalosub, [False Negative Awareness in Indicator-based Caching Systems, IEEE Transactions on Networking, 2022, pp. 46-56.
[2] I. Cohen, Bandwidth Efficient Cache Selection and Content Advertisement, pre-print, 2024.
"""
import os, pickle, sys, time
import numpy as np, pandas as pd
from datetime import datetime
from pathlib  import Path

import MyConfig
from printf import printf
import mod_pylru
import DistCacheSimulator as sim
from ttictoc import tic,toc
from MyConfig import * 

def run_hetro_costs_sim ():
    """
    Run experiments with several DSs, varying miss penalties, and heterogeneous DSs costs.
    """
    min_feasible_uInterval = 10
    DS_sizes    = [4]
    missps      = [300]
    DS_cost     = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    verbose     = [VERBOSE_CNT_SCALING] # MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES, MyConfig.VERBOSE_LOG_MR
    # start_time = time.time() 
    print ('running hetro_costs_sim')
    # for trace in ['Scarab', 'F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:     
    # for trace in ['Wiki', 'Scarab', 'F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:     
    for trace in ['F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:     
    # for trace in ['Wiki']:        
    # for trace in ['Scarab']:       
    # for trace in ['F1']: 
    # for trace in ['F2']: 
    # for trace in ['IBM1']: 
    # for trace in ['IBM7']: 
    # for trace in ['Twitter17']:
    # for trace in ['Twitter45']:
        for DS_size in [1000*item for item in DS_sizes]:
            max_num_of_req = 5000 #$$$ MyConfig.calc_num_of_req (trace) #    
            requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
            for mode in ['salsa_dep4']: #'salsa_dep0', 'fnaa', 'salsa_dep2'
                for missp in missps: 
                    res_file_name           = f'{mode}_{MyConfig.getMachineStr()}'
                    if VERBOSE_CNT_SCALING in verbose:
                        res_file_name += '_cntScale'
                    tic()
                    sm = sim.DistCacheSimulator(
                        delta_mode_period_param = 10, # length of "sync periods" of the indicator's scaling alg.
                        full_mode_period_param  = 10, # length of "sync periods" of the indicator's scaling alg.
                        res_file_name           = res_file_name,
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
                        uInterval_factor        = 2 if mode.startswith('salsa') else 1,
                        verbose                 = verbose
                        ) 
                    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10) 
                    print (f'Finished an iteration of run_hetro_costs_sim. mode={mode},missp={missp},DS_size={DS_size} {genElapsedTimeStr (toc())}')
                    exit ()
        
    # run_times_log_file_name = 'run_times.log'
    # if Path(run_times_log_file_name).is_file() and MyConfig.VERBOSE_RES in verbose: # does this res file already exist?
    #     run_times_log_file = open (run_times_log_file_name,  'a')
    # else:
    #     run_times_log_file = open (run_times_log_file_name,  'w')
    # printf (run_times_log_file, f'// finished running DS_size={DS_sizes}, missp={missps} after {time.time() - start_time}\n')


def run_num_of_DSs_sim ():
    """
    Run experiments with varying num of DSs and homogeneous DSs costs..
    """
    min_feasible_uInterval = 10
    DS_cost     = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    DS_size     = 16000
    verbose     = [MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES] # MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES, MyConfig.VERBOSE_LOG_MR
    print ('running num_of_DSs_sim')
    for num_of_DSs in [9]:
        DS_cost = calc_DS_cost (num_of_DSs=num_of_DSs, use_homo_DS_cost=True)
        for trace in ['Wiki', 'Scarab']:     
        # for trace in ['Wiki', 'Scarab', 'F1', 'F2', 'IBM1', 'IBM7', 'Twitter17', 'Twitter45']:
            missp = 30     
            for mode in ['salsa_dep4']:
                max_num_of_req = MyConfig.calc_num_of_req (trace)  
                requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
                tic()
                sm = sim.DistCacheSimulator(
                    delta_mode_period_param = 10, # length of "sync periods" of the indicator's scaling alg.
                    full_mode_period_param  = 10, # length of "sync periods" of the indicator's scaling alg.
                    res_file_name           = f'homo_{mode}_{MyConfig.getMachineStr()}',
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
                    min_feasible_uInterval  = 10,
                    k_loc                   = int(num_of_DSs/3),
                    uInterval_factor        = 2 if mode.startswith('salsa') else 1,
                    verbose                 = verbose
                ) 
                sm.run_simulator(interval_between_mid_reports=max_num_of_req/10) 
                print (f'Finished an iteration of run_num_of_DSs_sim. mode={mode},missp={missp},DS_size={DS_size}. {genElapsedTimeStr (toc())}')
    

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
    Returns a DS_cost matrix - either homo' or hetro', by the caller's request
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
    missp = 100
    DS_size = 4000
    sm = sim.DistCacheSimulator(
        res_file_name           = f'salsa2__{MyConfig.getMachineStr()}',
        EWMA_alpha_mr0          = 0.5, 
        EWMA_alpha_mr1          = 0.25, 
        trace_name              = trace,
        mode                    = 'salsa2',
        req_df                  = requests,
        client_DS_cost          = DS_cost,
        missp                   = missp,
        DS_size                 = DS_size,
        min_uInterval           = 3000,
        uInterval_factor        = 2,
        bpe                     = 10,
        verbose                 = [MyConfig.VERBOSE_LOG_MR]) #MyConfig.VERBOSE_DETAILED_LOG_MR
    sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
    print (f'Finished an iteration of run_full_ind_oriented_sim. mode={mode},missp={missp},DS_size={DS_size}. {genElapsedTimeStr (toc())}')


def run_mr_sim ():
    """
    Run an experiment to measure "mr", namely, the exclusion probabilities.
    """
    min_feasible_uInterval = 10
    DS_cost = calc_DS_cost (num_of_DSs=3, use_homo_DS_cost=False)
    for trace in ['Twitter45']: #, 'Scarab', 'Wiki', 'F1', 'Twitter45']: #  ], 'IBM7', 'Wiki', 'F1', 'Twitter45']:       # for trace in ['F1', 'IBM1', 'Scarab', 'Wiki', 'Twitter17']:       
        max_num_of_req = MyConfig.calc_num_of_req (trace)  
        requests = MyConfig.gen_requests (MyConfig.trace_csv_file_name[trace], max_num_of_req=max_num_of_req)  
        for mode in ['measure_mr_by_fullKnow_dep4', 'measure_mr_by_fnaa', 'measure_mr_by_salsa_dep4']: #, 'measure_mr_by_fnaa', 'measure_mr_by_salsa_dep4']: #'measure_mr_by_fnaa', 'measure_mr_by_salsa_dep4', 'measure_mr_by_fullKnow_dep']: 
            for mr_type in range (2): 
                tic()
                missp = 12
                DS_size = 16000
                sm = sim.DistCacheSimulator(
                    mr_type                 = mr_type,
                    res_file_name           = '',
                    EWMA_alpha_mr0          = 0.5, 
                    EWMA_alpha_mr1          = 0.25, 
                    trace_name              = trace,
                    mode                    = mode,
                    req_df                  = requests,
                    client_DS_cost          = DS_cost,
                    missp                   = missp,
                    DS_size                 = DS_size,
                    min_uInterval           = 3200,
                    bpe                     = 12,
                    uInterval_factor        = 32 if mode.startswith('salsa') else 1,
                    verbose                 = [])
                sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
                print (f'Finished an iteration of run_mr_sim. mode={mode},missp={missp},DS_size={DS_size}. {genElapsedTimeStr (toc())}')

   
if __name__ == '__main__':
    try:
        # run_num_of_DSs_sim ()
        # run_mr_sim ()
        # run_full_ind_oriented_sim ()
        run_hetro_costs_sim ()
    except KeyboardInterrupt:
        print('Keyboard interrupt.')
