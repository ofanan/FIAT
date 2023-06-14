"""
Parses a twitter trace, 
Output: a csv file, where:
        - the first col. is the keys,
        - (optional): a 2nd col. detailing the (u.a.r. picked) id of the clients associated with this req,
        - (optional): the rest of the cols. are the locations ("k_loc") to which a central controller would enter this req. upon a miss. 
"""

import numpy as np, pandas as pd
from numpy import infty
import mmh3, sys, hashlib
import MyConfig

def parse_IBN_trace (trace_file_name, 
                     max_num_of_req       = MyConfig.INF_INT, # maximum number of requests to be parsed, starting from the beginning of the trace
                     num_of_clients       = 1 # when larger than 1, the output will contain also the client u.a.r.-associated with each req. 
                     ):

    traces_path                 = MyConfig.getTracesPath()
    input_file_name             = 'snia/twitter/' + trace_file_name
    full_path_input_file_name   = traces_path + 'snia/twitter/' +  trace_file_name
     
    # input_file = open (full_path_input_file_name,  "r")
    # lines               = (line.rstrip() for line in input_file) # "lines" contains all lines in input file
    # lines               = (line for line in lines if line)       # Discard blank lines
        
    keys    = []
    req_cnt = 0
    
    with open (full_path_input_file_name,  "r") as input_file:
        for line in open (full_path_input_file_name,  "r"): 
            splitted_line = line.split (',')
            if not (splitted_line[5].startswith('get')):
                continue
            keys.append(splitted_line[1])
            req_cnt += 1
            if req_cnt > max_num_of_req:
                break
    
    uniq_keys       = np.unique(keys)
    keys_lut_dict   = dict(zip(uniq_keys , range(uniq_keys.size))) # dictionary serving as a LUT associating each unique_url with a unique integer
    keys            = np.array([keys_lut_dict[key] for key in keys]).astype('uint32')
    
    num_of_req = len(keys)     
    if (num_of_clients > 1):    # generate client assignments for each request
        client_assignment = np.random.RandomState(seed=42).randint(0 , num_of_clients , df.shape[0]).astype('uint8')
    
        unique_permutations_array   = np.array ([np.random.RandomState(seed=i).permutation(range(num_of_clients)) for i in range(uniq_keys.size)]).astype('uint8') # generate permutation for each unique key in the trace
        unique_permutations_array   = unique_permutations_array [:, range (kloc)] # Select only the first kloc columns for each row (unique key) in the random permutation matrix    
        permutation_lut_dict        = dict(zip(uniq_keys , unique_permutations_array)) # generate dictionary to serve as a LUT of unique_key -> permutation
        permutations_array          = np.array([permutation_lut_dict[url] for url in df[0]]).astype('uint8') # generate full permutations array for all requests. identical keys will get identical permutations
        permutations_df             = pd.DataFrame(permutations_array)
        trace_df                    = pd.DataFrame(np.transpose([keys, client_assignment]))
        trace_df.columns            = ['key', 'client_id']
        full_trace_df               = pd.concat([trace_df, permutations_df], axis=1)
    
    else:
        full_trace_df         = pd.DataFrame(np.transpose([keys]))
        full_trace_df.columns = ['key']
    
    print ('trace_file_name={}, {:.0f}K req, {:.0f}K uniques' .format (trace_file_name, num_of_req/1000, len(uniq_keys)/1000))    
    full_trace_df.to_csv (full_path_input_file_name + '.csv', index=False, header=True)
    
parse_IBN_trace ('cluster45.txt', max_num_of_req=1000) 
