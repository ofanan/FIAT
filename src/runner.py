"""
Run a simulation, looping over all requested values of parameters 
(miss penalty, cache sizes, number of caches etc.).
"""
from datetime import datetime
import os, pickle, sys

import MyConfig
import numpy as np
import pandas as pd
from printf import printf
import python_simulator as sim
from   tictoc import tic, toc

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

def calc_DS_cost (num_of_DSs = 3, use_homo_DS_cost = False):
    """
    Returns a DS_cost matrix - either homo' or hetro', by the user's request  
    """
    num_of_clients      = 1 # we currently consider only a single client, looking for data in several caches.
    if (use_homo_DS_cost):
        return calc_homo_costs(num_of_DSs, num_of_clients)
    else:
        return calc_hetro_costs(num_of_DSs, num_of_clients)

def run_var_missp_sim (trace_file_name, use_homo_DS_cost = False, print_est_mr=True, max_num_of_req=1000000):
    """
    Run a simulation with different miss penalties for the initial table
    """
    num_of_DSs          = 3
    uInterval           = 1000
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req) # Generate a dataframe of requests from the input trace file
    num_of_req          = requests.shape[0]
    DS_cost             = calc_DS_cost (num_of_DSs, use_homo_DS_cost)
    res_file_name       = 'tbl'# open ('../res/tbl_full.res', 'a')
    
    print("now = ", datetime.now(), 'running var_missp sim')
    for missp in [30, 100]: #, 100, 300
        for mode in ['fna']: 
            tic()
            sm = sim.Simulator(res_file_name, trace_file_name.split("/")[0], 
                               mode, requests, DS_cost, 
                               missp        = missp,
                               DS_size      = 10000,  
                               uInterval    = 2000, 
                               calc_mr_by_hist          = True,
                               use_perfect_hist         = False,
                               use_EWMA                 = True,
                               ins_cnt_based_uInterval  = True,
                               hist_based_uInterval     = True,
                               hit_ratio_based_uInterval= False,
                               verbose                  = [MyConfig.VERBOSE_RES, MyConfig.VERBOSE_FULL_RES]
                               )
            sm.run_simulator(interval_between_mid_reports=max_num_of_req/10)
            toc()

def run_uInterval_sim (trace_file_name, use_homo_DS_cost = False):
    """
    Run a simulation where the running parameter is uInterval.
    """
    max_num_of_req      = 1000000 # Shorten the num of requests for debugging / shorter runs
    num_of_DSs          = 3
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req)
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    DS_cost             = calc_DS_cost (num_of_DSs, use_homo_DS_cost)
    res_file_name       = 'uInterval' #open ("../res/" + trace_file_name + "_uInterval.res", "a")
    
    print("now = ", datetime.now(), 'running uInterval sim')
    for mode in ['fna']:  
        calc_mr_by_hist = False
        for uInterval in [8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16]:
            if (mode == 'fna' and not(calc_mr_by_hist) and uInterval < 50): # When uInterval < parameters updates interval, FNO and FNA are identical, so no need to run also FNA
                continue
            tic()
            sm = sim.Simulator(res_file_name, trace_file_name, mode, requests, DS_cost, uInterval = uInterval, calc_mr_by_hist=calc_mr_by_hist)        
            sm.run_simulator()
            toc()

def run_cache_size_sim (trace_file_name, use_homo_DS_cost = False):
    """
    Run a simulation where the running parameter is cache_size.
    """
    max_num_of_req      = 4300000 # Shorten the num of requests for debugging / shorter runs
    num_of_DSs          = 3
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req)
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    DS_cost             = calc_DS_cost (num_of_DSs, use_homo_DS_cost)
    res_file_name       = 'cache_size' #open ("../res/" + trace_file_name + "_cache_size.res", "a")

    if (num_of_req < 4300000):
        print ('Note: you used only {} requests for a cache size sim' .format(num_of_req))
    for DS_size in [1000, 2000, 4000, 8000, 16000, 32000]:
        for uInterval in [1024, 256]:
            for alg_mode in ['f']: 
                print("now = ", datetime.now(), 'running cache_size sim')
                tic()
                sm = sim.Simulator(res_file_name, trace_file_name, alg_mode, requests, DS_cost, uInterval = uInterval, DS_size = DS_size, calc_mr_by_hist=True, use_fresh_hist=False)
                sm.run_simulator()
                toc()
                     
def run_bpe_sim (trace_file_name, use_homo_DS_cost = False):
    """
    Run a simulation where the running parameter is bpe.
    If the input parameter "homo" is true, the access costs are uniform 1, and the miss penalty is 300/7. 
    Else, the access costs are 1, 2, 4, and the miss penalty is 100.
    """
    max_num_of_req      = 1000000 # Shorten the num of requests for debugging / shorter runs
    num_of_DSs          = 3
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req)
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    DS_cost             = calc_DS_cost (num_of_DSs, use_homo_DS_cost)
    res_file_name       = 'bpe' #open ("../res/" + trace_file_name + "_bpe.res", "a")
                       
    print("now = ", datetime.now(), 'running bpe sim')
    for bpe in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
        for uInterval in [1024, 256]:
            for alg_mode in ['fno']:              
                tic()
                sm = sim.Simulator(res_file_name, trace_file_name, alg_mode, requests, DS_cost, bpe = bpe, uInterval = uInterval, calc_mr_by_hist=True, use_fresh_hist=False) 
                sm.run_simulator()
                toc()


def run_num_of_caches_sim (trace_file_name, use_homo_DS_cost = True):
    """
    Run a simulation where the running parameter is the num of caches, and access costs are all 1.
    If the input parameter "homo" is true, the access costs are uniform 1, and the miss penalty is 300/7. 
    Else, the access costs are 1, 2, 4, and the miss penalty is 100.
    """
    DS_size             = 10000
    max_num_of_req      = 4300000 # Shorten the num of requests for debugging / shorter runs
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req)
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    res_file_name       = 'num_of_caches' #open ("../res/" + trace_file_name + "_num_of_caches.res", "a")
    
    if (num_of_req < 4300000):
        print ('Note: you used only {} requests for a num of caches sim' .format(num_of_req))

    for num_of_DSs in [1, 2, 3, 4, 5, 6, 7, 8]: 
        for uInterval in [1024]:
            DS_cost = calc_DS_cost (num_of_DSs, use_homo_DS_cost)            
            missp    = 50 * np.average (DS_cost)
     
            for alg_mode in ['fno']: 
                        
                print("now = ", datetime.now(), 'running num of caches sim')
                tic()
                sm = sim.Simulator(res_file_name, trace_file_name, alg_mode, requests, DS_cost, uInterval = uInterval, calc_mr_by_hist=True, use_fresh_hist=False)
                sm.run_simulator()
                toc()


def run_k_loc_sim (trace_file_name, use_homo_DS_cost = True):
    """
    Run a simulation where the running parameter is the num of caches, and access costs are all 1.
    If the input parameter "homo" is true, the access costs are uniform 1, and the miss penalty is 300/7. 
    Else, the access costs are 1, 2, 4, and the miss penalty is 100.
    """
    max_num_of_req      = 4300000 # Shorten the num of requests for debugging / shorter runs
    k_loc               = 1
    num_of_DSs          = 8
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req, k_loc) # In this sim', each item's location will be calculated as a hash of the key. Hence we actually don't use the k_loc pre-computed entries. 
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    res_file_name       = 'k_loc' #open ("../res/" + trace_file_name + "_k_loc.res", "a")
    
    if (num_of_req < 4300000):
        print ('Note: you used only {} requests for a num of caches sim' .format(num_of_req))

    for k_loc in [3]:
        for uInterval in [256]:
    
            DS_cost = calc_DS_cost (num_of_DSs, use_homo_DS_cost)            
            missp    = 50 * np.average (DS_cost)
     
            for alg_mode in ['opt']: 
                        
                print("now = ", datetime.now(), 'running k_loc sim')
                tic()
                sm = sim.Simulator(res_file_name, trace_file_name, alg_mode, requests, DS_cost, uInterval = uInterval, k_loc = k_loc, calc_mr_by_hist=True, use_fresh_hist=False)
                sm.run_simulator()
                toc()

def run_FN_by_staleness_sim (): 
    max_num_of_req      = 1000000 # Shorten the num of requests for debugging / shorter runs
    DS_cost             = calc_DS_cost ()            
    res_file_name       = 'FN_by_staleness' #open ("../res/FN_by_staleness.res", "a")
    print("now = ", datetime.now(), 'running FN_by_staleness sim')

    for trace_file_name in ['scarab/scarab.recs.trace.20160808T073231Z.15M_req_1000K_3DSs.csv', 'umass/storage/F2.3M_req_1000K_3DSs.csv']:
        requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req)  
        trace_file_name     = trace_file_name.split("/")[0]
        num_of_req          = requests.shape[0]
        #printf (output_file, '\n\ntrace = {}\n///////////////////\n' .format (trace_file_name))
    
        for bpe in [2, 4, 8, 16]:
            tic()
            sm = sim.Simulator(res_file_name, trace_file_name, 'fno', requests, DS_cost, bpe = bpe,    
                               verbose = [MyConfig.VERBOSE_CNT_FN_BY_STALENESS, MyConfig.VERBOSE_RES], uInterval = 8192, calc_mr_by_hist=True, use_fresh_hist=False) 
            sm.run_simulator()
            toc()


def run_FN_by_uInterval_sim (trace_file_name): 
    max_num_of_req      = 1000000 # Shorten the num of requests for debugging / shorter runs
    requests            = MyConfig.gen_requests (trace_file_name, max_num_of_req) # In this sim', each item's location will be calculated as a hash of the key. Hence we actually don't use the k_loc pre-computed entries. 
    DS_cost             = calc_DS_cost(num_of_DSs=1)            
    trace_file_name     = trace_file_name.split("/")[0]
    num_of_req          = requests.shape[0]
    
    print("now = ", datetime.now(), 'running FN_by_uInterval_sim sim')
    for bpe in [4, 8, 16]:
        res_file_name = "_FN_by_uInterval_bpe" + str(bpe) #open ("../res/" + trace_file_name + "_FN_by_uInterval_bpe" + str(bpe) +".res", "a")

        for uInterval in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]:
            tic()
            sm = sim.Simulator(res_file_name, trace_file_name, 'measure fp fn', requests, DS_cost,    
                               bpe = bpe, uInterval = uInterval)
            sm.run_simulator()
            toc()


def calc_opt_service_cost (accs_cost, comp_miss08_cnt, missp, num_of_req):
    print ('Opt service cost is ', (accs_cost + comp_miss_cnt * missp) / num_of_req)


wiki_trace_file_name   = 'wiki/wiki1.1190448987.txt'
gradle_trace_file_name = 'gradle/gradle.build-cache.xz.txt'
scarab_trace_file_name = 'scarab/scarab.recs.trace.20160808T073231Z.xz.txt'
F2_trace_file_name     = 'umass/storage/F2.spc.bz2.txt'
# print (MyConfig.gen_requests ('wiki/wiki2.1191403252.gz.txt', max_num_of_req=5))

# run_FN_by_uInterval_sim (trace_file_name)

# run_FN_by_staleness_sim ()
# run_bpe_sim              (trace_file_name)
# run_uInterval_sim(trace_file_name)

# run_cache_size_sim(trace_file_name)
# run_num_of_caches_sim  (trace_file_name, use_homo_DS_cost = True)
# run_k_loc_sim (trace_file_name)


# # Opt's behavior is not depended upon parameters such as the indicaror's size, and miss penalty.
# # Hence, it suffices to run Opt only once per trace and network, and then calculate its service cost for other 
# # parameters' values. Below is the relevant auxiliary code. 
# tot_access_cost= 1805450.0
# comp_miss_cnt = 104710
# num_of_req = 1000000
# for missp in [50, 500]:
#     print ("Opt's service cost is ", MyConfig.calc_service_cost_of_opt (tot_access_cost, comp_miss_cnt, missp, num_of_req))
run_var_missp_sim(trace_file_name=gradle_trace_file_name, max_num_of_req=1000000) 
