"""
Analyze traces' stat, e.g.: hit ratio, temporal locality.
"""
import os, sys, itertools, csv, numpy as np, pandas as pd

import mod_pylru, MyConfig
from   printf import printf
from   tictoc import tic, toc
from MyConfig import getTracesPath, gen_requests, optimal_BF_size_per_DS_size

def analyze_trace_locality (
    traces = [],
    max_len : float = float ('inf'),
    ):
    """
    Analyze the temporal locality of a trace.
    Results include a print of the avg. and of the stdev of the time between subsequent occurrences of the same key. 
    """
    for trace in traces:
        input_file = open (getTracesPath() + MyConfig.trace_csv_file_name[trace], 'r')
        
        csv_reader = csv.reader (input_file)
        
        row_num = 0
        for row in csv_reader:
            row_num += 1
            print (row)
            if row_num > max_len:
                break

def hit_rate_of_trace (trace_file_name):
    """
    Checks the hit rate in a given cache trace.
    """
    traces_path         = getTracesPath()
    max_num_of_req = 50000
    
    size = 100
    num_of_DSs = 3
    k_loc = 1
    requests            = gen_requests (traces_path + trace_file_name, max_num_of_req, num_of_DSs)
    DS = [mod_pylru.lrucache (size) for i in range (num_of_DSs)]# LRU cache. for documentation, see: https://pypi.org/project/pylru/
    hit_cnt = 0
    miss_cnt = 0
    for req_id in range(requests.shape[0]): # for each request in the trace...
        cur_req = requests.iloc[req_id] 
        key = cur_req.key
        hits_list = np.array ([DS_id for DS_id in range(num_of_DSs) if key in DS[DS_id] ])   
        if (hits_list.size == 0): #miss
            miss_cnt = miss_cnt + 1
            for k in range (k_loc): #Insert key to all the (randomly chosen) k_loc locations
                DS[cur_req['%d'%k]][key] = key
        else: # hit
            hit_cnt = hit_cnt + 1
            DS[hits_list[0]][key] # Touch the key, to indicate that it was accessed
    print ('hit cnt = {}, miss cnt = {}\n' .format (hit_cnt, miss_cnt))
    print ('hit rate = {:.2}\n' .format (hit_cnt / (hit_cnt + miss_cnt)))
                    

analyze_trace_locality (max_len=2, traces=['Wiki'])