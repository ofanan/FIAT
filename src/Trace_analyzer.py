"""
Analyze traces' stat, e.g.: hit ratio, temporal locality.
"""
import os, sys, itertools, csv, numpy as np, pandas as pd

import mod_pylru, MyConfig
from printf import printf, printar
from tictoc import tic, toc
from MyConfig import getTracesPath, gen_requests, optimal_BF_size_per_DS_size, indexOrNone, error

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
                    
def analyze_trace_locality (
    trace       : str = '',
    max_len     : float = float ('inf'),
    num_uniques : int = None, # num of distinct keys in the trace 
    trace_len   : int = None
    ):
    """
    Analyze the temporal locality of a trace.
    Results include a print of the avg. and of the stdev of the time between subsequent occurrences of the same key. 
    """
    if trace_len==None or num_uniques==None:
        error (f'In Trace_analyzer.analyze_trace_locality(). Sorry, currently num_uniques and numUniques cannot be None')
    
    
    inter_appearance_hist   = np.zeros (trace_len,   dtype='int32')
    last_appearance_of      = np.zeros (num_uniques, dtype='int32')
    input_file = open (getTracesPath() + MyConfig.trace_csv_file_name[trace], 'r')        
    csv_reader = csv.reader (input_file)    
    row_num = 0
    for row in csv_reader:
        row_num += 1
        if row_num==1: # Assume that first row contains the word 'key', rather than a numerical key
            continue        
        if row_num > max_len:
            break
        if row_num>trace_len:
            error (f'in Trace_analyzer.analyze_trace_locality(). row_num={row_num}, key={key} is larger than the given trace_len={trace_len}')            
        key = int(row[0])
        if key>=len(last_appearance_of):
            error (f'in Trace_analyzer.analyze_trace_locality(). row_num={row_num}, key={key} is too larger for the given num_of_uniques={num_uniques}')
        if last_appearance_of[key]>0: # This key has already appeared before #is the first appearance of this key
            inter_appearance_hist[row_num-last_appearance_of[key]] += 1
        last_appearance_of[key] = row_num
        
    outputFile = open (f'{getTracesPath()}traces_stat.txt', 'w')
    printf (outputFile, f'// inter_appearance_hist=\n')
    printar (outputFile, inter_appearance_hist)
    mean_interappearance = sum ([i*inter_appearance_hist[i] for i in range(len(inter_appearance_hist))]) / sum(inter_appearance_hist)
    printf (outputFile, f'// trace={trace} mean inter-appearance={mean_interappearance}, ')
    stdev_contribution_vec = [inter_appearance_hist[i]*(i-mean_interappearance)**2 for i in range(len(inter_appearance_hist))]
    # printf (outputFile, f'// stdev_contribution_vec=\n')
    # printar (outputFile, stdev_contribution_vec)
    printf (outputFile, f'stdev = {np.sqrt (sum (stdev_contribution_vec))}\n')   

for trace in ['Wiki']:
    analyze_trace_locality (trace=trace, trace_len=MyConfig.trace_len[trace], num_uniques=MyConfig.num_uniques_in_trace[trace])
# analyze_trace_locality (trace='Wiki', trace_len=13800000, num_uniques=934000, max_len=2)