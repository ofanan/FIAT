"""
This file contains several accessory functions, used throughout the project. In particular:
- Parse a trace, and associate each request with a concrete client and/or concrete DSs, to which the item is inserted, in case of a miss.
- Generate from the parsed trace a dataframe, to be used as an input to the simulator.
- Calculate the service cost of an optimal alg'.
- Calculate the BW used by the advertisement mechanism. 
- Generate the settings string, which is used to convey all the parameters (# of caches, cache size, indicator size etc.) of a concrete run.
- Calculate the inherent fpr of an optimally-configured Bloom filter, given its number of bits-per-element.
"""
import os
import numpy as np
import pandas as pd

INF_INT = 999999999

# levels of verbose
VERBOSE_RES                     = 1 # write to output files
VERBOSE_FULL_RES                = 2 
VERBOSE_LOG                     = 3 # write to log files
VERBOSE_DETAILED_LOG            = 4 
VERBOSE_LOG_MR                  = 5 # Write a log file detailing the mr upon every advertisement
VERBOSE_DETAILED_LOG_MR         = 6 # Write a log file detailing the mr upon every advertisement
VERBOSE_LOG_Q                   = 7 # Write a log file detailing the q (prob' of pos ind')
VERBOSE_DEBUG                   = 9
VERBOSE_CNT_FN_BY_STALENESS     = 10 
VERBOSE_CNT_MR0_BY_STALENESS    = 11
VERBOSE_SHORT_LOG               = 12  # Write to a log file only major events.

num_of_req = {'Wiki'      : {4000 : 390000, 10000 : 700000, 16000 : 1100000, 64000 :  6000000},
              'Scarab'    : {4000 : 250000, 10000 : 500000, 16000 : 700000,  64000 :  4000000},
              'F1'        : {4000 : 250000, 10000 : 400000, 16000 : 500000,  64000 :  2500000},
              'F2'        : {4000 : 150000, 10000 : 350000, 16000 : 500000,  64000 : 10000000},
              'P3'        : {4000 : 250000, 10000 : 300000, 16000 : 400000,  64000 :  2500000},
              'Twitter17' : {4000 : 250000, 10000 : 600000, 16000 : 1200000, 64000 : 14000000},
              'Twitter45' : {4000 : 200000, 10000 : 200000, 16000 : 300000,  64000 :  2000000},
              'IBM1'      : {4000 : 200000, 10000 : 300000, 16000 : 300000,  64000 :  948000},
              'IBM7'      : {4000 : 250000, 10000 : 650000, 16000 : 800000,  64000 :  4006000}
             }

# relative paths of the traces, under the directory 'traces' 
trace_txt_file_name = {'Wiki'   : 'wiki/wiki1.1190448987.txt',
                       'Gradle' : 'gradle/gradle.build-cache.txt',
                       'Scarab' : 'scarab/scarab.recs.trace.20160808T073231Z.xz.txt'}

trace_csv_file_name = {'Wiki'       : 'wiki/wiki1.1190448987_6000Kreq.csv',
                       'Gradle'     : 'gradle/gradle.build-cache.xz_2091Kreq.csv',
                       'Scarab'     : 'scarab/scarab.recs.trace.20160808T073231Z.xz_8159Kreq.csv',
                       'F1'         : 'umass/storage/F1.spc.bz2_5643Kreq.csv',
                       'F2'         : 'umass/storage/F2.spc.bz2_13883Kreq.csv',
                       'WS1'        : 'umass/storage/WS1.spc.bz2_31967Kreq.csv',
                       'P3'         : 'arc/P3.3912Kreq.csv',
                       'Twitter17'  : 'snia/twitter/Twitter17.cluster17_14MReq_464Kuniqes.csv',
                       'Twitter45'  : 'snia/twitter/Twitter45.cluster45.txt.csv',
                       'IBM1'       : 'snia/IBM/IBM1.ObjectStoreTrace001Part0.txt.csv',
                       'IBM7'       : 'snia/IBM/IBM7.ObjectStoreTrace007Part0.txt.csv'
                       }


def print_list (list):
    for item in list:
        print (f'{item}')

def check_if_input_file_exists (relative_path_to_input_file):
    """
    Check whether an input file, given by its relative path, exists.
    If the file doesn't exist - exit with a proper error msg.
    """
    if not (os.path.isfile (relative_path_to_input_file)):
        error (f'the input file {relative_path_to_input_file} does not exist')

def calc_num_of_req (trace, DS_size=64000):
    """
    Given a trace and caches size, calculate the number of requests for having a substantial sim.
    A substantial simulation contains a num of uniques which is at least 2.5 times the overall caches' size.
    We assue here 3 caches. Hence, the num of unqiues should be at least 2.5*3*DS_size.
    if rtrn_num_req_for_64, we always return the # of request for DS_size==64K. 
    """
    if DS_size <= 4000:
        return num_of_req[trace][4000]
    elif DS_size <= 10000:
        return num_of_req[trace][10000]
    elif DS_size <= 16000:
        return num_of_req[trace][16000]
    elif DS_size <= 64000:
        return num_of_req[trace][64000]
    else:
        return INF_INT
    

def reduce_trace_mem_print(trace_df, k_loc=1, read_clients_from_trace=False, read_locs_from_trace=False):
    """
    Reduces the memory print of the trace by using the smallest type that still supports the values in the trace
    Note: this configuration can support up to 2^8 locations, and traces of length up to 2^32

    """
    new_trace_df        = trace_df
    new_trace_df['key'] = trace_df['key'].astype('uint32')   
    if (read_clients_from_trace): # need to read the client assigned for each request in the input file?
        new_trace_df['client_id'] = trace_df['client_id'].astype('uint8')   # client to which this request is assigned
    
    if (read_locs_from_trace): # need to read the DSs assigned for each unique request in the input file?
        for i in range (k_loc):
            new_trace_df['%d'%i] = trace_df['%d'%i].astype('uint8')
    return new_trace_df


def gen_requests (trace_file_name, max_num_of_req=INF_INT, k_loc=1, num_of_clients=1):
    """
    Generates a trace of requests, given a trace file.
    """
    relative_path_trace_file_name = gen_relative_path_trace_file_name (trace_file_name)
    check_if_input_file_exists(relative_path_to_input_file=relative_path_trace_file_name)
    
    if (len(relative_path_trace_file_name.split ('.csv'))==2): # The input file is already a .csv parsed from the trace - no need to parse the trace
        return reduce_trace_mem_print (pd.read_csv (relative_path_trace_file_name).head(max_num_of_req))
    else: # need to parse the trace first
        return reduce_trace_mem_print (parse_list_of_keys (input_file_name=trace_file_name, num_of_req = max_num_of_req, print_output_to_file=False))
    # reduce_trace_mem_print (pd.read_csv (getTracesPath() + trace_file_name).head(max_num_of_req))


def optimal_BF_size_per_DS_size ():
    """
    Sizes of the bloom filters (number of cntrs), for chosen DS sizes, k=5 hash funcs, and designed false positive rate.
    The values are taken from https://hur.st/bloomfilter
    online resource calculating the optimal values
    """
    BF_size_for_DS_size = {}
    BF_size_for_DS_size[0.01] = {20: 197, 40: 394, 60: 591, 80: 788, 100: 985, 200: 1970, 400: 3940, 600: 5910, 800: 7880, 1000: 9849, 1200: 11819, 1400: 13789, 1600: 15759, 2000: 19698, 2500: 24623, 3000: 29547}
    BF_size_for_DS_size[0.02] = {20: 164, 40: 328, 60: 491, 80: 655, 100: 819, 200: 1637, 400: 3273, 600: 4909, 800: 6545, 1000: 8181, 1200: 9817, 1400: 11453, 1600: 13089}
    BF_size_for_DS_size[0.03] = {1000: 7299}
    BF_size_for_DS_size[0.04] = {1000: 6711}
    BF_size_for_DS_size[0.05] = {20: 126, 40: 251, 60: 377, 80: 502, 100: 628, 200: 1255, 400: 2510, 600: 3765, 800: 5020, 1000: 6275, 1200: 7530, 1400: 8784, 1600: 10039}
    return BF_size_for_DS_size 


def calc_service_cost_of_opt (accs_cost, comp_miss_cnt, missp, req_cnt):
    """
    Opt's behavior is not depended upon parameters such as the indicaror's size, and miss penalty.
    Hence, it suffices to run Opt only once per trace and network, and then calculate its service cost for other 
    parameters' values using this func'
    """
    return (accs_cost + comp_miss_cnt * missp) / req_cnt

def getTracesPath():
    """
    returns the path in which the traces files are found at this machine.
    Currently, traces files should be placed merely in the "/../traces/" subdir
    """
    return '../../traces/'
#   #return 'C:/Users/' + os.getcwd().split ("\\")[2] + '/Documents/traces/' if (os.getcwd().split ("\\")[0] == "C:") else '/home/icohen/traces/'

def calcOvhDsCost ():
    """
    Returns the loads of the 19-nodes OVH network, based on the distances and BWs    
    """
    full_path_to_rsrc   = os.getcwd() + "\\..\\resources\\"
    client_DS_dist_df   = pd.read_csv (full_path_to_rsrc + 'ovh_dist.csv',index_col=0)
    client_DS_dist      = np.array(client_DS_dist_df)
    client_DS_BW_df     = pd.read_csv (full_path_to_rsrc + 'ovh_bw.csv',index_col=0)
    client_DS_BW        = np.array(client_DS_BW_df)
    bw_regularization   = np.max(np.tril(client_DS_BW,-1)) 
    alpha = 0.5
    return 1 + alpha * client_DS_dist + (1 - alpha) * (bw_regularization / client_DS_BW) # client_DS_cost(i,j) will hold the access cost for client i accessing DS j


def exponential_window (old_estimate, new_val, alpha):
    """
    An accessory function to calculate an exponential averaging window. Currently unused.
    """
    return alpha * new_val + (1 - alpha) * old_estimate 

def bw_to_uInterval (DS_size, bpe, num_of_DSs, bw):
    """
    Given a requested bw [bits / system request], returns the per-cache uInterval, namely, the avg num of events this cache has to count before sending an update.
    An "event" here is either a user access to the cache, or an insertion to that cache.
    The simulator calculates the number of events implicitly, by assuming that each user request causes an event to a single cache -- 
    and hence, each cache sees an event once in num_of_DSs user requests on average. 
    """
    return int (round (DS_size * bpe * num_of_DSs) / bw)
 
def uInterval_to_Bw (DS_size, bpe, num_of_DSs, uInerval):
    """
    Given an update interval, estimate the BW it would require. Currently unused.
    """
    return (DS_size * bpe * num_of_DSs * (num_of_DSs-1)) / uInterval

def get_optimal_num_of_hashes (bpe):
    """
    Returns the optimal number of hash functions for a given number of Bits Per Element (actually, cntrs per element) in a Bloom filter
    """
    return int (bpe * np.log (2))

def error (str):
    print ('error: {}' .format (str))
    exit ()


def calc_designed_fpr (DS_size, BF_size, num_of_hashes):
    """
    returns the designed (inherent) fpr of a BF, based on the given cache size, BF size, and number of hash functions used by the BF.
    """
    return pow (1 - pow (1 - 1/BF_size, num_of_hashes * DS_size), num_of_hashes)


def gen_relative_path_trace_file_name (trace_file_name):
    """
    Given a trace's name, check whether the directory and the file exists.
    If the file exists, return the relative path to it.
    Else, print an appropriate error msg and exit.
    """
    traces_path = getTracesPath()
    if not (os.path.exists (traces_path)):
        error ('the traces directory {} does not exist' .format (traces_path))
    relative_path_trace_file_name = traces_path + trace_file_name 
    if not (os.path.isfile (relative_path_trace_file_name)):
        error ('the trace {} was not found' .format (relative_path_trace_file_name))
    return relative_path_trace_file_name

def parse_list_of_keys (input_file_name,
                        num_of_clients              = 1, # number of clients to choose from, when associating each request with a given client 
                        kloc                        = 1,  # number of DSs with which each unique item will be associated  
                        num_of_req                  = INF_INT, # maximum number of requests to be considered from the trace
                        print_output_to_file        = True, # When False, the func' returns the output as a dataframe, rather than printing it to a file
                        print_num_of_uniques        = False, # When True, print the number of unique items in the trace to the standard output
                        only_calc_num_of_uniques    = False # When True, only print to the screen the number of uniques, and returns
                        ):
    """
    Parses a trace whose format is merely a list of keys (each key in a different line). 
    Output: 
        if print_num_of_uniques:
            - print to the screen the overall num of requests in the trace, and the num of uniques among them.
        if only_calc_num_of_uniques:
            - return without generating an output.
        if print_output_to_file - generate an output is  a csv file, where:
            - the first col. is the keys,
            - If num_of_clients>1: add a 2nd col. containing the u.a.r.-generated id of the clients associated with this req.
        else, return a panda DataFrame, where:
            - the first col. is the keys,
            - If num_of_clients>1: add a 2nd col. containing the u.a.r.-generated id of the clients associated with this req.
    """

    relative_path_trace_file_name = gen_relative_path_trace_file_name (input_file_name)
    df = pd.read_csv (relative_path_trace_file_name, sep=' ', header=None, nrows = num_of_req)
        
    # associate each unique "url" in the input with a unique key 
    unique_urls = np.unique (df)
    url_lut_dict = dict(zip(unique_urls , range(unique_urls.size))) # generate dictionary to serve as a LUT of unique_key -> integer
    keys = np.array ([url_lut_dict[url] for url in df[0]]).astype('uint32')
    num_of_req = len(keys) 
    if print_num_of_uniques:
        print ('trace={}, {:.0f}K req, {:.0f}K uniques' .format (input_file_name.split('.')[0].split('/')[1], num_of_req/1000, len(unique_urls)/1000))

    if only_calc_num_of_uniques:
        return
    
    if (num_of_clients > 1):    # generate client assignments for each request
        client_assignment = np.random.RandomState(seed=42).randint(0 , num_of_clients , df.shape[0]).astype('uint8')
        
        unique_permutations_array  = np.array ([np.random.RandomState(seed=i).permutation(range(num_of_clients)) for i in range(unique_urls.size)]).astype('uint8') # generate permutation for each unique key in the trace
        unique_permutations_array  = unique_permutations_array [:, range (kloc)] # Select only the first kloc columns for each row (unique key) in the random permutation matrix    
        permutation_lut_dict = dict(zip(unique_urls , unique_permutations_array)) # generate dictionary to serve as a LUT of unique_key -> permutation
        permutations_array = np.array([permutation_lut_dict[url] for url in df[0]]).astype('uint8') # generate full permutations array for all requests. identical keys will get identical permutations
        permutations_df = pd.DataFrame(permutations_array)
        trace_df = pd.DataFrame(np.transpose([keys, client_assignment]))
        trace_df.columns = ['key', 'client_id']
        full_trace_df = pd.concat([trace_df, permutations_df], axis=1)
    
    else:
        full_trace_df = pd.DataFrame(np.transpose([keys]))
        full_trace_df.columns = ['key']
    
    if (print_output_to_file):
        full_trace_df.to_csv (relative_path_trace_file_name.split (".txt")[0] + '_{:.0f}Kreq.csv' .format (num_of_req/1000), 
                              index=False, header=True)
    else:
        return full_trace_df

def characterize_trace (trace, 
                        num_of_req=float ('inf')  
                        ):
    """
    Finds the trace's characteristic. Currently, this is merely finding the # of uniques within a given num of requests (starting from the trace's beginning). 
    """
    relative_path_trace_file_name = gen_relative_path_trace_file_name (trace_csv_file_name[trace])
    keys    = []
    req_cnt = 0
    
    # with open (full_path_input_file_name,  "r") as input_file:
    for line in open (relative_path_trace_file_name,  "r"): # as input_file: input_file:
        keys.append(line)
        req_cnt += 1
        if req_cnt > num_of_req:
            break
    
    uniq_keys       = np.unique(keys)
    print ('trace={}, {:.0f}K req, {:.0f}K uniques' .format (trace, req_cnt/1000, len(uniq_keys)/1000))

def get_trace_name (trace_file_name):
    """
    Given the file name of the trace (possibly including the path), return a short trace name.
    E.g., given the trace_file_name 'umass/storage/F2.spc.bz2.txt', the function returns 'F2'.
    """
    return trace_file_name.split("/")[-1].split('.')[0]

    ## historgram
    #count_df = trace.value_counts()
    #count_df[count_df > 1].plot()
    #hist_array = np.zeros(int(np.log2(count_df.max())) + 1)
    #for i in range(int(np.log2(count_df.max())) + 1):
    #    hist_array[i] = sum(count_df[(count_df >= 2**i) & (count_df < 2**(i+1))])
# parse_list_of_keys (input_file_name='arc/P3.lis.txt', print_output_to_file=True, print_num_of_uniques=True)

def getMachineStr ():
    """
    Returns a string that identifies the machine on which the program is running - e.g., on 'PC', or on 'HPC'. 
    """
    pwdStr = os.getcwd()
    if (pwdStr.find ('itamarc')>-1): # the string 'HPC' appears in the path only in HPC runs
        return 'HPC' # indicates that this sim runs on my PC
    return 'PC' # indicates that this sim runs on an HPC       

def indexOrNone(l : list, 
                elem):
    """
    if elem is found in a list, returns the first index in which it's found.
    else, return None
    """
    try:
        idx = l.index(elem)
        return idx
    except ValueError:
        return None
    
# def main ():
#     num_of_req = INF_INT
#     for num_of_req in [300000]:
#         characterize_trace (trace = 'IBM1', 
#                             num_of_req                  = num_of_req
#                             )
    # parse_list_of_keys (input_file_name             = wiki_txt_file_name, 
    #                     num_of_req                  = num_of_req,
    #                     print_output_to_file        = True,
    #                     print_num_of_uniques        = True,
    #                     only_calc_num_of_uniques    = False)
    
if __name__ == '__main__':
    # parse_list_of_keys (input_file_name='wiki/wiki1.1190448987.txt', num_of_req=6000000)
    # print (calc_num_of_req ('wiki', 1000))
    main ()