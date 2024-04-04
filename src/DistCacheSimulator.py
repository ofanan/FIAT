import pandas as pd
import sys, pickle, random
import numpy as np
from   pathlib import Path
import DataStore, Client, candidate, node, MyConfig 
from   printf import printf
from numpy.core._rational_tests import denominator

class DistCacheSimulator(object):
    """
    A simulator that accepts system parameters (trace, number and size of caches, algorithm to run etc.), 
    runs a simulation, and outputs the results to a file.
    """
    
    # Called upon a miss. Check whether the miss is compulsory or not. 
    # Increments the relevant counter, and inserts the key (in practice, "key" is merely an integer) to self.k_loc DSs.
    # Called upon a miss. Check whether the miss is compulsory or not. Increments the relevant counter, and inserts the key to self.k_loc DSs.        
    handle_miss = lambda self: self.handle_compulsory_miss () if (self.is_compulsory_miss()) else self.handle_non_compulsory_miss ()

    # Decides which client will invoke this request. 
    # If there's a single client, the client_id always 1.
    # Else: 
    # - If self.use_given_client_per_item==True, this function will output the client selected by the given trace file.
    # - Else, the client will be selected uar among all clients.
    calc_client_id = lambda self: 0 if (self.num_of_clients==0) else (self.cur_req.client_id if (self.use_given_client_per_item) else random.randint(0, self.num_of_clients-1))
    
    # Returns the datastore (DS) to which a missed key should be inserted.
    # "i" means that this is the i-th DS to which this missed key is inserted. 
    # Note that 0 <= i <= k_loc - 1.
    # If self.use_given_DS_per_item==True, the returned DSs is the one stated in the given trace ("req_df").
    # Else, the DS is picked by a simplified "hash func'" of the key (actually, merely the key modulo the number of DSs. 
    select_DS_to_insert = lambda self, i : self.DS_list[self.cur_req['%d'%i]] if (self.use_given_DS_per_item) else self.DS_list[(self.cur_req.key+i) % self.num_of_DSs]    

    # Check whether it's time for a mid-report, and if so - output a mid-report
    mid_report = lambda self : self.gather_statistics(self.full_res_file) if (self.req_cnt % self.interval_between_mid_reports == 0 and self.req_cnt>0) else None

    def gen_settings_str (self, num_of_req=None):
        """
        Returns a formatted string based on the values of the given parameters' (e.g., num of caches, trace_name, update intervals etc.). 
        """
        num_of_req = num_of_req if (num_of_req!=None) else self.num_of_req
        
        # generate the initial string, that does not include the mode information
        uInterval_str = '{:.0f}' .format(self.min_uInterval)
        settings_str = \
            '{}.C{:.0f}K.bpe{:.0f}.{:.0f}Kreq.{:.0f}DSs.Kloc{:.0f}.M{:.0f}.B{:.0f}.U{}' .format (
            self.trace_name, self.DS_size/1000, self.bpe, num_of_req/1000, 
            self.num_of_DSs, self.k_loc, self.missp, self.bw, uInterval_str)
        
        # Add the string representing the mode   
        if (self.mode=='opt'):
            return '{}.{}' .format (settings_str, 'Opt')

        settings_str = '{}.{}' .format (settings_str, self.mode.upper()) 

        # Now we know that the mode isn't 'Opt'
        if self.calc_mr_by_hist and (not (self.mode.startswith('salsa'))):
            settings_str = '{}.{}{}' .format (
                settings_str,   
                'P' if self.use_perfect_hist else 'E', # 'E' for 'Estimated' 
                'ewma' if self.use_EWMA else 'flat')  # either exp-weighted-moving-avg, or simple, flat avg
        
        if (self.mode.startswith('salsa')):
            uIntFactToken = '{:.1f}' .format (self.uInterval_factor)
            settings_str = f'{settings_str}.mr0th{self.mr0_ad_th}.mr1th{self.mr1_ad_th}.uIntFact{uIntFactToken}.minFU{self.min_feasible_uInterval}.alpha0{self.EWMA_alpha_mr0}.alpha1{self.EWMA_alpha_mr1}.per_param{self.delta_mode_period_param}.scaleF{self.scale_ind_full_factor}.scaleD{self.scale_ind_delta_factor}' 
        return settings_str
    
    def gen_DSs(self):
        """
        Generate a list of empty DSs (Data Stores == caches)
        """
        self.DS_list = [DataStore.DataStore(
            ID                      = i, 
            num_of_DSs              = self.num_of_DSs,    
            size                    = self.DS_size, 
            bpe                     = self.bpe,
            min_uInterval           = self.min_uInterval,
            uInterval_factor        = self.uInterval_factor,
            consider_delta_updates  = self.consider_delta_updates,
            mr_output_file          = self.mr_output_file[i], 
            collect_mr_stat         = self.collect_mr_stat,  
            analyse_ind_deltas      = not (self.calc_mr_by_hist),
            EWMA_alpha              = self.EWMA_alpha,
            EWMA_alpha_mr0          = self.EWMA_alpha_mr0,
            EWMA_alpha_mr1          = self.EWMA_alpha_mr1,
            use_EWMA                = self.use_EWMA,
            use_indicator           = not (self.mode=='opt'), # Opt doesn't really use indicators - it "knows" the actual contents of the DSs
            non_comp_miss_th        = self.non_comp_miss_th,
            non_comp_accs_th        = self.non_comp_accs_th,
            initial_mr0             = self.initial_mr0,
            initial_mr1             = self.initial_mr1, # initial_mr1 is set by the DS to its designed fpr.
            mr0_ad_th               = self.mr0_ad_th,
            mr1_ad_th               = self.mr1_ad_th,
            settings_str            = self.gen_settings_str (num_of_req=self.trace_len), 
            mr1_ewma_window_size    = self.ewma_window_size,
            max_fpr                 = self.max_fpr, 
            max_fnr                 = self.max_fnr, 
            verbose                 = self.verbose, 
            scale_ind_delta_factor  = self.scale_ind_delta_factor,
            scale_ind_full_factor   = self.scale_ind_full_factor,
            init_mr0_after_each_ad  = self.re_init_after_each_ad,               
            init_mr1_after_each_ad  = self.re_init_after_each_ad,               
            use_fixed_uInterval     = self.use_fixed_uInterval,
            min_feasible_uInterval  = self.min_feasible_uInterval,
            send_fpr_fnr_updates    = not (self.calc_mr_by_hist),
            delta_mode_period_param = self.delta_mode_period_param, # length of "sync periods" of the indicator's scaling alg.
            full_mode_period_param  = self.full_mode_period_param, # length of "sync periods" of the indicator's scaling alg.
            use_CountingBloomFilter = self.use_CountingBloomFilter,
            assume_ind_DSs          = self.assume_ind_DSs,
            do_not_advertise_upon_insert         = self.do_not_advertise_upon_insert,
            num_of_insertions_between_fpr_fnr_updates   = self.num_of_insertions_between_fpr_fnr_updates,
            hit_ratio_based_uInterval               = self.hit_ratio_based_uInterval,
        ) for i in range(self.num_of_DSs)]
            
    def init_client_list(self):
        """
        Init a list of clients
        """
        
        self.client_list = [Client.Client(
                ID          = i, 
                num_of_DSs  = self.num_of_DSs, 
                window_size = int (self.min_uInterval/10), 
                verbose     = self.verbose, 
                k_loc       = self.k_loc, 
                missp       = self.missp) 
        for i in range(self.num_of_clients)]
    
    def init_mr_res_file (self, res_file_name):
        """
        Open the res file for writing results of 'measure_mr' sim, as follows:
        If a res file with the relevant name already exists - open it for appending.
        Else, open a new res file, and write to it comment header lines, explaining the file's format  
        """
        full_path_res_file_name = '../res/{}.res' .format(res_file_name)
        if Path(full_path_res_file_name).is_file(): # does this res file already exist?
            return (open (full_path_res_file_name,  'a'))
        res_file =  open (full_path_res_file_name,  'w')
        printf (res_file, '// Format:\n' )
        printf (res_file, '// bin | mode | (i0,m0),(i1,m1), ...\n' )
        printf (res_file, '// Where: bin is 0 for mr0, 1 for mr1.\n' )
        printf (res_file, '// mode is either: fullKnow, salsa2, or fnaa.\n' )
        printf (res_file, '// i0 is the insertion count when the estimated mr is m0; i1 is the insertion count when the estimated mr is m1, etc.\n')        
        return res_file
    
    def init_res_file (self, res_file_name):
        """
        Open the res file for writing, as follows:
        If a res file with the relevant name already exists - open it for appending.
        Else, open a new res file, and write to it comment header lines, explaining the file's format  
        """
        
        full_path_res_file_name = '../res/{}.res' .format(res_file_name)
        
        if Path(full_path_res_file_name).is_file(): # does this res file already exist?
            return (open (full_path_res_file_name,  "a"))
        else:
            res_file =  open (full_path_res_file_name,  "w")
            printf (res_file, '// format: e.g., scarab.C10K.bpe14.1000Kreq.3DSs.Kloc1.M30.B0.U1000.SALSA.m0_0.1_m1_0.01, where:\n' )
            printf (res_file, '// scarab=trace file. 10K=the capacity of each cache. 14=num of Bits Per Element in the indicator.\n' )
            printf (res_file, '// 1000Kreq - num of requests in the trace is 1000K.\n')
            printf (res_file, '// 3DSs- num of datastores (Caches) is 3. \n')
            printf (res_file, '// Kloc1- each element is mapped to a single location (cache).\n')
            printf (res_file, '// M30 - missp is 30\n')
            printf (res_file, '// B0 - desired BW - for simulation with bandwidth const currently unused.\n')
            printf (res_file, '// U1000 - used fixed uInterval of 1000 insertions.\n')
            printf (res_file, '//     alternatively, the "U" field can say:\n')
            printf (res_file, '//     Ux-Uy, where x,y are min_u_uInterlva, max_num_uInterval.\n')
            printf (res_file, '// SALSA is the algorithm (aka "mode") used.\n')
            printf (res_file, '// m0_0.1_m1_0.01 informs the values of "mult0", "mult1" that are now 0.1 and 0.01, resp.\n') 
            
            return res_file


    def __init__(self, 
                 EWMA_alpha_mr0 = 0.85,
                 EWMA_alpha_mr1 = 0.85,
                 res_file_name  = '_', 
                 trace_name     = '_', 
                 mode           = None, 
                 req_df         = None, 
                 client_DS_cost = [1], 
                 missp          = 100, 
                 k_loc          = 1, 
                 DS_size        = 10000, 
                 bpe            = 14, 
                 rand_seed      = 42, 
                 max_fpr        = 0.01, 
                 max_fnr        = 0.01, 
                 verbose        = [MyConfig.VERBOSE_RES], 
                 use_given_client_per_item   = False, # When true, associate each request with the client determined in the input trace ("req_df")                 
                 use_given_DS_per_item       = False, # When true, insert each missed request with the datastore(s) determined in the input trace ("req_df")
                 use_fixed_uInterval         = True, 
                 hit_ratio_based_uInterval   = False, # when True, send advertisements according to the hist-based estimations of the hit ratio
                 use_global_uInerval         = False, 
                 bw                 = 0, # Determine the update interval by a given bandwidth (currently usused)
                 min_uInterval      = 0,  
                 uInterval_factor   = float('inf'),  
                 calc_mr_by_hist    = True, # when false, calc mr by analysis of the BF
                 use_perfect_hist   = False, # when true AND calc_mr_by_hist, assume that the client always has a perfect knowledge about the fp/fn/tp/tn implied by each previous indication, by each DS (even if this DS wasn't accessed).
                 use_EWMA           = True, # when true, use Exp Window Moving Avg for estimating the mr (exclusion probabilities)
                 delta_mode_period_param = 10, # length of "sync periods" of the indicator's scaling alg.
                 full_mode_period_param  = 10, # length of "sync periods" of the indicator's scaling alg.
                 re_init_after_each_ad   = False, 
                 min_feasible_uInterval  = 10,
                 mr_type                 = 0, # Relevant only when the mode's name starts with 'measure_mr'. indicates whether to measure mr0, or mr1.
                 begin_log_mr_at_req_cnt = float ('inf') # the first request cnt at which a "detailed log mr" verbose mode will be applied.  
                 ):
        """
        Return a DistCacheSimulator object with the following attributes:
            mode:               e.g. 'opt', 'fnaa', 'fno'
            client_DS_cost:     2D array of costs. entry (i,j) is the cost from client i to DS j
            missp:               miss penalty
            k_loc:              number of DSs a missed key is inserted to
            DS_size:            size of DS 
            bpe:                Bits Per Element: number of cntrs in the CBF per a cached element (commonly referred to as m/n)
            use_redundancy_coef: When true, this allows decreasing the probability of speculative access (namely, and access upon a negative indication).
            max_fpr, max_fnr:   Allows for sending an update by some maximum allowed (estimated) fpr, fnr. 
                                When the estimated fnr is above max_fnr, or the estimated fpr is above max_fpr, the DS sends an update.
                                Currently unused.  
            verbose :           Amount of info written to output files. When 1 - write at the end of each sim' the cost, number of misses etc.
            bw:                 BW budged. Used to calculate the update interval when the uInterval isn't explicitly define in the input.
            uInterval:          update Interval, namely, number of insertions to each cache before this cache advertises a fresh indicator.
            use_given_client_per_item: if True, place each missed item in the location(s) defined for it in the trace. Else, select the location of a missed item based on hash. 
            use_EWMA            use Exp Weighted Moving Avg to estimate the current mr0, mr1.            
        """
        self.re_init_after_each_ad = re_init_after_each_ad
        self.EWMA_alpha         = 0.25  # exp' window's moving average's alpha parameter
        self.EWMA_alpha_mr0     = EWMA_alpha_mr0  # exp' window's moving average's alpha parameter
        self.EWMA_alpha_mr1     = EWMA_alpha_mr1  # exp' window's moving average's alpha parameter
        self.non_comp_miss_th   = 0.1
        self.non_comp_accs_th   = 0.01
        self.mr0_ad_th          = 0.88 
        self.mr1_ad_th          = 0.01 
        self.verbose            = verbose # Defines the log/res data printed out to files       
        self.use_perfect_hist   = use_perfect_hist       
        self.mode               = mode
        
        if MyConfig.VERBOSE_RES in self.verbose or MyConfig.VERBOSE_FULL_RES in self.verbose:
            if not(self.mode.startswith('measure_mr')): # 'measure_mr' opens its own .mr.res files. 
                self.res_file = self.init_res_file (res_file_name)
        if (MyConfig.VERBOSE_FULL_RES in self.verbose):
            self.full_res_file = self.init_res_file ('{}_full' .format (res_file_name))
        
        self.mr_type            = mr_type
        self.trace_name         = trace_name
        self.missp              = missp
        self.DS_size            = DS_size
        self.bpe                = bpe
        self.rand_seed          = rand_seed
        self.DS_insert_mode     = 1  #DS_insert_mode: mode of DS insertion (1: fix, 2: distributed, 3: ego). Currently only insert mode 1 is used
        if not (self.mode=='opt'): 
            self.calc_mr_by_hist = calc_mr_by_hist
        self.use_EWMA           = use_EWMA # use Exp Weighted Moving Avg to estimate the current mr0, mr1.
        self.num_of_clients     = client_DS_cost.shape[0]
        self.num_of_DSs         = client_DS_cost.shape[1]
        self.k_loc              = k_loc
        if (self.DS_insert_mode != 1):
            MyConfig.error ('sorry, currently only fix insert mode (1) is supported')

        if (self.k_loc > self.num_of_DSs):
            MyConfig.error ('k_loc must be at most num_of_DSs')

        self.client_DS_cost     = client_DS_cost # client_DS_cost(i,j) will hold the access cost for client i accessing DS j
        self.max_fnr            = max_fnr
        self.max_fpr            = max_fpr
                
        self.mr_of_DS           = np.zeros(self.num_of_DSs) # mr_of_DS[i] will hold the estimated miss rate of DS i 
        self.req_df             = req_df
        self.trace_len          = self.req_df.shape[0]
        self.pos_ind_cnt        = np.zeros (self.num_of_DSs , dtype='uint') #pos_ind_cnt[i] will hold the number of positive indications of indicator i in the current window
        self.leaf_of_DS         = np.array(np.floor(np.log2(self.client_DS_cost))).astype('uint8') # lg_client_DS_cost(i,j) will hold the lg2 of access cost for client i accessing DS j
        self.pos_ind_list       = [] #np.array (0, dtype = 'uint8') #list of the DSs with pos' ind' (positive indication) for the current request
        self.pr_of_pos_ind_estimation       = np.zeros (self.num_of_DSs , dtype='uint') #pr_of_pos_ind_estimation[i] will hold the estimation for the prob' that DS[i] gives positive ind' for a requested item.  

        self.window_alhpa         = 0.25 # window's alpha parameter for estimated parameters       
        self.mode                 = mode
        self.total_cost           = float(0)
        self.hit_cnt              = 0
        self.total_access_cost    = 0
        self.high_cost_mp_cnt     = 0 # counts the misses for cases where accessing DSs was too costly, so the alg' decided to access directly the mem
        self.comp_miss_cnt        = 0
        self.non_comp_miss_cnt    = 0
        self.FN_miss_cnt          = 0 # num of misses happened due to FN event
        self.tot_num_of_updates   = 0
        self.bw                   = bw
        self.initial_mr0          = (1 - 1.1*(self.client_DS_cost[0][i]/self.missp)) if self.re_init_after_each_ad else 0.88
               
        # If the uInterval is given in the input (as a non-negative value) - use it. 
        # Else, calculate uInterval by the given bw parameter.
        self.use_global_uInerval    = use_global_uInerval
        self.min_feasible_uInterval = min_feasible_uInterval
        self.min_uInterval          = min_uInterval
        self.ewma_window_size       = max (100, int(self.min_uInterval/10)) # window for parameters' estimation 
        self.uInterval_factor       = uInterval_factor 
        self.use_CountingBloomFilter=  False # Currently, none of the modes uses CountingBloomFilter. Instead, they use Simple Bloom Filters.
        if self.use_global_uInerval:
            self.do_not_advertise_upon_insert = True # Disallow each cache-initiated advertisement; instead, self will decide when to advertise, based on self counters.
            self.min_uInterval = MyConfig.bw_to_uInterval (self.DS_size, self.bpe, self.num_of_DSs, self.bw)
            self.advertise_cycle_of_DS = np.array ([ds_id * self.min_uInterval / self.num_of_DSs for ds_id in range (self.num_of_DSs)])
        else:
            self.do_not_advertise_upon_insert = False # default value. Usually we'd like the cache to consider advertising upon an insert of a new item
        self.cur_updating_DS = 0
        self.use_only_updated_ind = True if (self.min_uInterval == 1 and self.uInterval_factor==1) else False
        self.num_of_insertions_between_fpr_fnr_updates = int (self.min_uInterval/10)
        if (self.num_of_clients == 1):
            self.use_given_client_per_item = False # if there's only 1 client, all requests belong to this client, disregarding what was pre-computed in the trace file.
        else:
            self.use_given_client_per_item = use_given_client_per_item # When True, upon miss, the missed item is inserted to the location(s) specified in the given request traces input. When False, it's randomized for each miss request.
        self.use_given_DS_per_item = use_given_DS_per_item

        self.avg_DS_accessed_per_req = float(0)
        if (MyConfig.VERBOSE_CNT_FN_BY_STALENESS in self.verbose):
            lg_uInterval = np.log2 (self.min_uInterval).astype (int)
            self.PI_hits_by_staleness = np.zeros (lg_uInterval , dtype = 'uint32') #self.PI_hits_by_staleness[i] will hold the number of times in which a requested item is indeed found in any of the caches when the staleness of the respective indicator is at most 2^(i+1)
            self.FN_by_staleness      = np.zeros (lg_uInterval,  dtype = 'uint32') #self.FN_by_staleness[i]      will hold the number of FN events that occur when the staleness of that indicator is at most 2^(i+1)        else:

        self.delta_mode_period_param = delta_mode_period_param
        self.full_mode_period_param  = full_mode_period_param
        self.initial_mr1                    = MyConfig.calc_designed_fpr (self.DS_size, self.bpe*self.DS_size, MyConfig.get_optimal_num_of_hashes (self.bpe))
        self.begin_log_mr_at_req_cnt        = begin_log_mr_at_req_cnt
        if self.mode.startswith('measure_mr'):
            """
            simulate the system, where the cahce-selection alg' is a trivial cache-selection alg', that always relies on the indicator.
            periodically measure the mr0, (aka "the negative exclusion probability" - namely, the prob' that an item isn't in the DS, given a negative indication).  
            """
            self.assume_ind_DSs                 = (self.mode=='measure_mr_by_salsa_dep')   
            self.use_fixed_uInterval            = True
            self.do_not_advertise_upon_insert   = True
            self.hit_ratio_based_uInterval      = False
            self.collect_mr_stat                = False
            self.use_CountingBloomFilter        = False
            self.print_detailed_output          = False
            self.q_window_alpha                 = 0.25
            self.num_of_DSs                     = 3            
            self.indications                    = np.array (range (self.num_of_DSs), dtype = 'bool')
            self.resolution                     = np.array (range (self.num_of_DSs), dtype = 'bool')
            self.DSs2accs                       = []
            self.ins_cnt                        = np.zeros (self.num_of_DSs)
            self.mr_measure_window              = [self.min_uInterval/10, self.min_uInterval/10] # size of measure window for mr0, mr1. 
            self.q_measure_window               = self.mr_measure_window[0]
            self.naive_selection_alg            = 'all_plus_speculative'
            self.use_fna                        = True
            self.num_of_warmup_ads              = [self.DS_size/self.min_uInterval, self.DS_size/self.min_uInterval] # num of warmup advertisement before starting to print the mr. index 0 is for mr0, index 1 is for mr1. 
            self.num_of_ads_to_measure          = 4
            self.num_of_insertions_between_fpr_fnr_updates = self.mr_measure_window[0] 

            self.measure_mr_res_file            = [None for ds in range(self.num_of_DSs)]
            for ds in range (self.num_of_DSs):
                self.measure_mr_res_file[ds] = self.init_mr_res_file ('../res/{}_C{:.0f}K_U{:.0f}_bpe{:.0f}_measure_mr_{}_{}{}.mr' .format (
                        self.trace_name, self.DS_size/1000, self.min_uInterval, self.bpe, self.naive_selection_alg, 'detailed_' if self.print_detailed_output else '', ds))

        if (not(self.mode in ['opt', 'fnaa'])) and (not(self.mode.startswith('salsa'))) and (not(self.mode.startswith('measure_'))):
            MyConfig.error (f'Sorry, the selected mode {self.mode} is not supported.')

        if self.mode in ['opt', 'fnaa'] or self.mode.startswith('salsa'):
            self.speculate_accs_cost        = 0 # Total accs cost paid for speculative accs
            self.speculate_accs_cnt         = 0 # num of speculative accss, that is, accesses to a DS despite a miss indication
            self.speculate_hit_cnt          = 0 # num of hits among speculative accss
            self.indications                = np.array (range (self.num_of_DSs), dtype = 'bool')
            self.use_perfect_hist           = False
        
        if (self.mode == 'opt'):
            self.collect_mr_stat            = False												   
            self.calc_mr_by_hist            = False
            self.use_fixed_uInterval        = True
            self.hit_ratio_based_uInterval  = False
            self.assume_ind_DSs             = False

        if (self.mode == 'fnaa'):
            self.collect_mr_stat            = False
            self.calc_mr_by_hist            = False
            self.use_fixed_uInterval        = True
            self.hit_ratio_based_uInterval  = False
            self.assume_ind_DSs             = True
        
        if self.mode.startswith('salsa'):
            self.calc_mr_by_hist            = True
            self.collect_mr_stat            = True 
            self.use_fixed_uInterval        = False
            self.hit_ratio_based_uInterval  = False 
            self.assume_ind_DSs = not (self.mode.startswith('salsa_dep'))
        else:
            self.collect_mr_stat            = self.calc_mr_by_hist and (not (self.use_perfect_hist))
            self.consider_delta_updates     = False
            self.scale_ind_delta_factor     = 1
            self.scale_ind_full_factor      = 1

        if self.mode in ['salsa0', 'salsa_dep0']:
            self.scale_ind_delta_factor     = 1
            self.scale_ind_full_factor      = 1
            self.consider_delta_updates     = False
            self.ewma_window_size           = max (200, int(self.min_uInterval/5)) # window for parameters' estimation 
                        
        if self.mode in ['salsa1']:
            self.scale_ind_delta_factor     = 1
            self.scale_ind_full_factor      = 1.1
            self.consider_delta_updates     = False
            self.ewma_window_size           = max (200, int(self.min_uInterval/5)) # window for parameters' estimation 
                        
        if self.mode in ['salsa1', 'salsa_dep1']:
            self.scale_ind_delta_factor     = 1
            self.scale_ind_full_factor      = 1
            self.consider_delta_updates     = True
            self.ewma_window_size           = max (200, int(self.min_uInterval/5)) # window for parameters' estimation 
                        
        if self.mode in ['salsa2', 'salsa_dep2']:
            self.scale_ind_delta_factor     = 1
            self.scale_ind_full_factor      = 1.1
            self.consider_delta_updates     = True
            self.ewma_window_size           = max (200, int(self.min_uInterval/5)) # window for parameters' estimation 

        if self.mode in ['salsa3', 'salsa_dep3']:
            self.scale_ind_delta_factor     = 1.1
            self.scale_ind_full_factor      = 1.1
            self.consider_delta_updates     = True
            self.ewma_window_size           = max (200, int(self.min_uInterval/5)) # window for parameters' estimation 

        if self.mode.startswith('salsa') and (not (self.mode in ['salsa0', 'salsa1', 'salsa2', 'salsa_dep0', 'salsa_dep1', 'salsa_dep2', 'salsa_dep3'])):
            MyConfig.error ('In DistCacheSimulator.init(). sorry. Mode {} is not supported' .format(self.mode) )                                             
            
        if (self.calc_mr_by_hist and self.use_perfect_hist):
            self.neg_ind_cnt    = np.zeros (self.num_of_DSs)
            self.fp_cnt         = np.zeros (self.num_of_DSs)
            self.tn_cnt         = np.zeros (self.num_of_DSs)
            self.mr0        = np.ones  (self.num_of_DSs)
            self.mr1        = self.initial_mr1 * np.ones (self.num_of_DSs)
        
        self.init_client_list ()
        self.mr_output_file = [None]*self.num_of_DSs # will be filled by real files only if requested to log mr.
        if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose: 
            self.verbose.append (MyConfig.VERBOSE_LOG_MR) # Detailed mr log should include also "basic" mr log.
        if MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_SHORT_LOG in self.verbose:
            self.init_mr_output_files()
            self.zeros_ar            = np.zeros (self.num_of_DSs, dtype='uint16') 
            self.ones_ar             = np.ones  (self.num_of_DSs, dtype='uint16') 

        self.gen_DSs() #DS_list is the list of DSs
        if MyConfig.VERBOSE_DEBUG in self.verbose:
            self.debug_file = open (f'../res/{self.gen_settings_str(num_of_req=0)}_debug.txt', "w")


    def init_mr_output_files (self):
        """
        Init per-DS output file, to which the simulator writes data about the estimated mr (conditional miss rates, namely pr of a miss given a negative ind (mr0), or a positive ind (mr1)).
        The simulator also writes to this data (via Datastore.py) about each access whether it results in a True Positive, True Negative, False Positive, or False negative.
        """
        settings_str = self.gen_settings_str (num_of_req=self.trace_len)
        for ds in range (self.num_of_DSs):
            self.mr_output_file[ds] = open ('../res/{}_ds{}{}.mr' .format (settings_str, ds, '_dbg' if MyConfig.VERBOSE_DEBUG in self.verbose else ''), 'w')

    def DS_costs_are_homo (self):
        """
        returns true iff all the DS costs, of all clients, are identical
        """
        for i in range (self.num_of_clients):
            for j in range (self.num_of_DSs):
                if (self.client_DS_cost[i][j] != self.client_DS_cost[0][0]):
                    return False 
        return True

    def PGM_FNA_partition (self):
        """
        Performs the partition stage in the PGM-Staeleness-Aware alg'. 
        In a FNA (aka stale-aware) alg', the candidate DSs are all the DSs (even those with negative ind'), and
        therefore it's possible to perform the partition stage only once, instead of re-run it for each request.
        """

        self.DSs_in_leaf = [] # DSs_in_leaf[i] will hold the 2D list of DSs of client i, as described below
        self.num_of_leaves = np.zeros (self.num_of_clients, dtype = 'uint8') #num_of_leaves[i] will hold the # of leaves in PGM alg' when the client is i
        for client_id in range (self.num_of_clients):
            self.num_of_leaves[client_id] = np.max (np.take(self.leaf_of_DS [client_id], range (self.num_of_DSs))) + 1 
            DSs_in_leaf = [[]] # For the current client_id, DSs_in_leaf[j] will hold the list of DSs which belong leaf j, that is, the IDs of all the DSs with access in [2^j, 2^{j+1})
            for leaf_num in range (self.num_of_leaves[client_id]):
                DSs_in_leaf.append ([])
            for ds_id in (range(self.num_of_DSs)):
                DSs_in_leaf[self.leaf_of_DS[client_id][ds_id]].append(ds_id)
            self.DSs_in_leaf.append(DSs_in_leaf)
                

    def gather_statistics(self, res_file=None):
        """
        Accumulates and organizes the stat collected during the sim' run.
        This func' is usually called once at the end of each run of the python_simulator.
        """
        if not (MyConfig.VERBOSE_RES in self.verbose or MyConfig.VERBOSE_FULL_RES in self.verbose):
            return
        
        res_file = res_file if (res_file!=None) else self.res_file

        if (MyConfig.VERBOSE_CNT_FN_BY_STALENESS in self.verbose):
            printf (res_file, 'FN cnt by staleness      = {}\n' .format (self.FN_by_staleness))
            printf (res_file, 'PI hits cnt by staleness = {}\n' .format (self.PI_hits_by_staleness))
            for bin in range (len(self.FN_by_staleness)):
                printf (res_file, '({:.0f}, {:.07f})' .format (2**(bin+1), self.FN_by_staleness[bin]/self.PI_hits_by_staleness[bin]))

        self.total_access_cost  = np.sum ( [client.total_access_cost for client in self.client_list ] ) 
        self.hit_cnt            = np.sum ( [client.hit_cnt for client in self.client_list] )
        self.hit_ratio          = float(self.hit_cnt) / self.req_cnt
        self.non_comp_miss_cnt  = np.sum( [client.non_comp_miss_cnt for client in self.client_list ] )
        self.comp_miss_cnt      = np.sum( [client.comp_miss_cnt for client in self.client_list ] )
        self.high_cost_mp_cnt   = np.sum( [client.high_cost_mp_cnt for client in self.client_list ] )
        self.total_cost         = self.total_access_cost + self.missp * (self.comp_miss_cnt + self.non_comp_miss_cnt + self.high_cost_mp_cnt)
        self.mean_service_cost  = self.total_cost / self.req_cnt 
        if (self.mode in ['opt', 'measure fp fn']):
            bw = 0
        else:
            bw = np.sum([DS.overall_ad_size for DS in self.DS_list]) / float (self.req_cnt)
        settings_str            = self.gen_settings_str (num_of_req=self.req_cnt)
        printf (res_file, '\n{} | service_cost = {:.2f} | bw = {:.2f} | hit_ratio = {:.2}, \n'  .format (settings_str, self.mean_service_cost, bw, self.hit_ratio))

        printf (res_file, '// tot_access_cost = {:.0f}, non_comp_miss_cnt = {}, comp_miss_cnt = {}\n' .format 
           (self.total_access_cost, self.non_comp_miss_cnt, self.comp_miss_cnt) )                                 
        if (self.mode=='opt'):
            printf (res_file, '\n')
            return
        printf (res_file, '// ewma_window = {}\n' .format (self.ewma_window_size))
        num_of_fpr_fnr_updates = sum (DS.num_of_fpr_fnr_updates for DS in self.DS_list) / self.num_of_DSs
        if (self.mode == 'fnaa' and not(self.calc_mr_by_hist)):
            printf (res_file, '// num of insertions between fpr_fnr estimations = {}\n' .format (self.num_of_insertions_between_fpr_fnr_updates))
            printf (res_file, '// avg num of fpr_fnr updates = {:.0f}, fpr_fnr_updates bw = {:.4f}\n' 
                                .format (num_of_fpr_fnr_updates, num_of_fpr_fnr_updates/self.req_cnt))

        printf (res_file, '// spec accs cost = {:.0f}, num of spec hits = {:.0f}\n' .format (self.speculate_accs_cost, self.speculate_hit_cnt))             
        printf (res_file, '// num of ads per DS={}. ' .format ([DS.num_of_advertisements for DS in self.DS_list]))
        avg_num_of_ads = np.average([DS.num_of_advertisements for DS in self.DS_list])
        if (avg_num_of_ads==0): # deter division by 0
            printf (res_file, ' avg update interval = INF')
        else:
            printf (res_file, ' avg update interval = {:.1f} req' .format (float(self.req_cnt) / avg_num_of_ads))
        if self.hit_ratio_based_uInterval:
            printf (res_file, '\n// non_comp_miss_th={}, non_comp_accs_th={}\n' .format (self.non_comp_miss_th, self.non_comp_accs_th))
        if (self.hit_ratio < 0 or self.hit_ratio > 1):
            MyConfig.error ('error at simulator.gather_statistics: got hit_ratio={}. Please check the output file for details' .format (self.hit_ratio))
        if self.mode.startswith('salsa2'):
            printf (res_file, f'\n// num of full ind ad={[DS.num_of_full_ads for DS in self.DS_list]}, num of periods in delta mode={[DS.num_of_periods_in_delta_ads for DS in self.DS_list]}')
            printf (res_file, f'\n//num of sync ads={[DS.num_of_sync_ads for DS in self.DS_list]}')
        printf (res_file, '\n')
        
        
        
    def run_trace_measure_fp_fn (self):
        """
        Run a trace on a single cache, only to measure the FN, or FP ratio.
        """
        self.hit_cnt     = 0
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            if (self.cur_req.key in self.DS_list[0]): #hit 
                self.hit_cnt += 1
                if (self.cur_req.key in self.DS_list[0].stale_indicator): # True positive                    
                    self.DS_list[0].access(self.cur_req.key)
                else: # FN
                    self.FN_miss_cnt += 1
                    self.DS_list[0].insert (key = self.cur_req.key, req_cnt = self.req_cnt)
            else: # miss
                self.DS_list[0].insert (key = self.cur_req.key, req_cnt = self.req_cnt)
        printf (self.res_file, '({}, {})' .format (self.min_uInterval, self.FN_miss_cnt/self.hit_cnt))               
        
    
    def handle_single_req_naive_alg (self):
        """
        handle a single request performed by a naive algorithm.
        This includes:
        - Assign to self.pos_indications the list of DSs with positive indications for self.cur_req.key.
        - Assign to self.resolution the resolution (existence/non existence) of self.cur_req.key in each DS.
        - Assign to self.DSs2accs the list of DSs to access, according to the chosen selection alg'.
        - If inserting the item to a DS (happens only upon a miss), then set self.DS2insert = ID of this DS. Else, set self.DS2insert=None. 
        - if self.naive_selection_alg=='cheapest': 
          - access the DS with the minimal cost (actually, the first in the list, assuming the list is always ordered by non-decreasing costs) among those with positive indications.
          - if no pos indication exists, access a single, u.a.r. picked, $ with neg' ind. 
        - if self.naive_selection_alg=='all': 
          - Access all the DSs with positive indications.
          - if no pos indication exists, the alg' accesses a single, u.a.r. picked, $ with neg' ind. 
        - if self.naive_selection_alg=='all_plus_speculative': 
          - Access all the DSs with positive indications, plus a single u.a.r selected DS with a negative indication.
          - if no pos indication exists, access a single, u.a.r. picked, $ with neg' ind. 
        - If the access results in a miss, insert self.cur_req.key into one of the DS, as chosen by self.select_DS_to_insert. 
        - Returns True iff the self.cur_req.key is found in any of the accessed DSs. 
        """
        self.pos_indications = [ds for ds in range(self.num_of_DSs) if self.cur_req.key in self.DS_list[ds].stale_indicator]
        self.indications     = [self.cur_req.key in self.DS_list[ds].stale_indicator for ds in range (self.num_of_DSs)]
        self.resolution      = [self.cur_req.key in self.DS_list[ds]                 for ds in range (self.num_of_DSs)]
        if self.pos_indications==[]: # no positive indications
            self.DSs2accs = [random.randint (0, self.num_of_DSs-1)] if self.use_fna else [];
        else: # at least one positive indication
            if self.naive_selection_alg=='cheapest':
                self.DSs2accs = [self.pos_indications[0]] # assuming here that the Dss are sorted in an increasing order of accs cost
            elif self.naive_selection_alg=='all':
                self.DSs2accs = self.pos_indications
            elif self.naive_selection_alg=='all_plus_speculative':
                self.DSs2accs = self.pos_indications
                if len(self.DSs2accs)!=self.num_of_DSs: # not all DSs gave pos indication
                    self.DSs2accs.append (random.choice([ds for ds in range(self.num_of_DSs) if not (ds in self.pos_indications)]))
            else:
                MyConfig.error ('handle_single_req_naive_alg was called with an unknown selection algorithm {selection_alg}')
        
        hit = False # default value
        for ds2accs in self.DSs2accs:
            if self.resolution[ds2accs]==True:
                hit = True
                self.DS_list[ds2accs].cache[self.cur_req.key] #Touch the element, so as to update the LRU mechanism
                
        if hit: # hit --> need to insert the key to a cache
            self.DS2insert = None
        else: # miss --> need to insert the key to a cache    
            self.DS2insert = self.select_DS_to_insert(0).ID # pseudo-randomly select the DS to which the item will be inserted 
            self.DS_list[self.DS2insert].insert (key = self.cur_req.key, req_cnt = self.req_cnt) # miss --> insert the missed item into the DS
            self.ins_cnt[self.DS2insert] += 1
        return hit
        
        
    def check_warmup_ad_and_finish_report (self, ds):
        """
        Assigns self.finished_warmup_period[ds]=True iff the warmup advertisement period is done.
        Assigns self.finished_report_period[ds]=True iff the period in which report should be written to the .mr.res file is done.
        """
        if self.num_of_ads[ds] == self.num_of_warmup_ads[self.mr_type]: # Skip some warm-up period; later, write the results to file
            self.finished_warmup_period[ds] = True        
            if self.print_detailed_output: 
                printf (self.measure_mr_res_file[ds], f'\nfinished warmup of ds{ds}')
                            
        if self.finished_warmup_period[ds]: 
            if self.num_of_ads[ds] > self.num_of_warmup_ads[self.mr_type] + self.num_of_ads_to_measure: # Collected enough points
                self.finished_report_period[ds] = True

    def run_trace_measure_mr_full_knowledge (self):
        """
        Measuer and print to an output mr.res file either mr0, or mr1, as indicated in self.mr_tye.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        mr1, aka "the positive exclusion prob'", is the probability that an item isn't cached, given a positive indication for that item.
        The alg' runs the chosen naive selection alg' - that is, either "all" - which accesses all the DSs with positive ind', or "cheapest", which accesses the cheapest DS with a pos' ind'.
        The choice which naive DS selection alg' to run is set by the parameter self.naive_selection_alg.
        If self.use_fna==True, whenever all indicators show a negative ind', the selection alg' picks a u.a.r. DS to access. Else, the function accesses only caches with positive indications.   
        """
        self.ins_cnt                    = [0     for _ in range(self.num_of_DSs)]
        last_printed_ins_cnt            = [0     for _ in range(self.num_of_DSs)]
        self.num_of_ads                 = [0     for _ in range(self.num_of_DSs)]
        last_advertised_ins_cnt         = [0     for _ in range(self.num_of_DSs)]
        self.finished_warmup_period     = [False for _ in range(self.num_of_DSs)]
        self.finished_report_period     = [False for _ in range(self.num_of_DSs)]
        if self.mr_type==0:
            neg_ind_cnt                 = [0     for _ in range(self.num_of_DSs)]
            tn_cnt                      = [0     for _ in range(self.num_of_DSs)]
        else:
            pos_ind_cnt                 = [0     for _ in range(self.num_of_DSs)]
            fp_cnt                      = [0     for _ in range(self.num_of_DSs)]
            printed_mr1_for_DS          = [False for _ in range(self.num_of_DSs)]
        for ds in range(self.num_of_DSs):
            printf (self.measure_mr_res_file[ds], f'\n{self.mr_type} | fullKnow | ')
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]
            self.handle_single_req_naive_alg() # perform data access for this req and update self.indications, self.resolution and self.DSs2accs 
            
            for ds in range(self.num_of_DSs):

                # update counters based on the current indications and resolutions
                if self.finished_warmup_period[ds]:
                    if self.mr_type==0:
                        if self.indications[ds]==False: # negative indication for this DS
                            neg_ind_cnt[ds] += 1
                            if self.resolution[ds]==False:
                                tn_cnt[ds] += 1
                    else: #self.mr_type==1
                        if self.indications[ds]: # positive indication for this DS
                            pos_ind_cnt[ds] += 1
                            if self.resolution[ds]==False:
                                fp_cnt[ds] += 1
                
                if self.print_detailed_output and self.ins_cnt[ds]>0 and self.ins_cnt[ds] % self.mr_measure_window[1]==0: #$$
                    printf (self.measure_mr_res_file[ds], f'\nreq_cnt={self.req_cnt}, ins_cnt[{ds}]={self.ins_cnt[ds]}, pos_ind_cnt={pos_ind_cnt[ds]}, fp_cnt={fp_cnt[ds]}, num_of_ads={self.num_of_ads}, last_printed_ins_cnt={last_printed_ins_cnt[ds]}') 
                
                if self.finished_warmup_period[ds] and self.ins_cnt[ds]!=last_printed_ins_cnt[ds]: # Skip some warm-up period; later, write the results to file

                    if self.mr_type==0:
                        if neg_ind_cnt[ds]>0 and neg_ind_cnt[ds] % self.mr_measure_window[0]==0:
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], tn_cnt[ds]/neg_ind_cnt[ds]))
                            last_printed_ins_cnt[ds] = self.ins_cnt[ds]
                            neg_ind_cnt[ds] = 0
                            tn_cnt[ds]      = 0
                    else: #self.mr_type==1
                        if pos_ind_cnt[ds]>0 and pos_ind_cnt[ds] % self.mr_measure_window[1]==0:
                            if not(printed_mr1_for_DS[ds]):
                                printed_mr1_for_DS[ds] = True
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], fp_cnt[ds]/pos_ind_cnt[ds]))
                            last_printed_ins_cnt[ds] = self.ins_cnt[ds]
                            pos_ind_cnt[ds] = 0
                            fp_cnt     [ds] = 0

                if self.ins_cnt[ds] % self.min_uInterval == 0 and self.ins_cnt[ds]!=last_advertised_ins_cnt[ds]: # time to advertise
                    self.DS_list[ds].advertise_ind_full_mode (called_by_str='simulator')
                    if self.print_detailed_output:
                        if self.mr_type==0:
                            printf (self.measure_mr_res_file[ds], f'\nadvertised. ins_cnt[{ds}]={self.ins_cnt[ds]}, neg_ind_cnt[{ds}]={neg_ind_cnt[ds]}') 
                        else:
                            printf (self.measure_mr_res_file[ds], f'\nadvertised. ins_cnt[{ds}]={self.ins_cnt[ds]}, pos_ind_cnt[{ds}]={pos_ind_cnt[ds]}') 
                    if self.mr_type==0:
                        if neg_ind_cnt[ds] >= 100: # report only if we have enough data for it...
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], tn_cnt[ds]/neg_ind_cnt[ds]))
                    else:
                        if pos_ind_cnt[ds] >= 100: # report only if we have enough data for it...
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], fp_cnt[ds]/pos_ind_cnt[ds]))
                    self.num_of_ads[ds] += 1
                    self.check_warmup_ad_and_finish_report (ds)
                    last_advertised_ins_cnt[ds] = self.ins_cnt[ds]

                    if self.mr_type==0:
                        neg_ind_cnt[ds] = 0
                        tn_cnt[ds]      = 0
                    else:
                        pos_ind_cnt[ds] = 0
                        fp_cnt     [ds] = 0
                

            if all(self.finished_report_period):
                if self.mr_type==1:
                    for ds in range(self.num_of_DSs):
                        if not(printed_mr1_for_DS[ds]):
                            print (f'Warning: did not print any results for DS {ds}') 
                return  
    
    def run_trace_estimate_mr_by_salsa (self):
        """
        Estimate using SALSA estimation scheme and print to an output mr.res file either mr0, or mr1, as indicated in self.mr_tye.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        mr1, aka "the positive exclusion prob'", is the probability that an item isn't cached, given a positive indication for that item.
        Estimate mr0 and print to an output .res file mr0.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        The alg' runs the chosen naive selection alg' - that is, either "all" - which accesses all the DSs with positive ind', or "cheapest", which accesses the cheapest DS with a pos' ind'.
        Only the estimation uses a SALSA2-like mechanism; in order to make a meaningful comparison with the other estimations/measurements of mr0, 
        the selection alg' is NOT salsa, but a naive DS selection alg'.   
        The choice which naive DS selection alg' to run is set by the parameter self.naive_selection_alg.
        If self.use_fna==True, whenever all indicators show a negative ind', the selection alg' picks a u.a.r. DS to access. Else, the function accesses only caches with positive indications.   
        """
        if self.mr_type==0:
            neg_ind_cnt         = [0     for _ in range(self.num_of_DSs)]
            tn_cnt              = [0     for _ in range(self.num_of_DSs)]
            estimated_mr        = [self.initial_mr0 for _ in range(self.num_of_DSs)] 
        else:
            pos_ind_cnt         = [0     for _ in range(self.num_of_DSs)]
            fp_cnt              = [0     for _ in range(self.num_of_DSs)]
            printed_mr1_for_DS  = [False for _ in range(self.num_of_DSs)]
            estimated_mr        = [self.initial_mr1 for _ in range(self.num_of_DSs)] 

        self.ins_cnt            = [0     for _ in range(self.num_of_DSs)]
        self.num_of_ads         = [0     for _ in range(self.num_of_DSs)]
        self.finished_warmup_period  = [False for _ in range(self.num_of_DSs)]
        self.finished_report_period  = [False for _ in range(self.num_of_DSs)]
        
        for ds in range(self.num_of_DSs):
            printf (self.measure_mr_res_file[ds], f'\n{self.mr_type} | salsa2 | ')
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.handle_single_req_naive_alg() # perform data access for this req and update self.indications, self.resolution and self.DSs2accs 
            
            for ds in self.DSs2accs:

                if self.mr_type==0:
                    if self.indications[ds]==False: # negative indication for this DS
                        neg_ind_cnt[ds] += 1
                        if self.resolution[ds]==False:
                            tn_cnt[ds] += 1
                    if neg_ind_cnt[ds]>0 and neg_ind_cnt[ds] % self.mr_measure_window[0]==0:
                        estimated_mr [ds] = self.EWMA_alpha_mr0 * tn_cnt[ds]/neg_ind_cnt[ds] + (1-self.EWMA_alpha_mr0) * estimated_mr [ds] 
                        if self.finished_warmup_period[ds]: # Skip some warm-up period; later, write the results to file
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr[ds]))
                            neg_ind_cnt[ds] = 0
                            tn_cnt[ds]      = 0
                            
                else: #self.mr_type==1
                    if self.indications[ds]: # positive indication for this DS
                        pos_ind_cnt[ds] += 1
                        if self.resolution[ds]==False:
                            fp_cnt[ds] += 1

                    if pos_ind_cnt[ds]>0 and pos_ind_cnt[ds] % self.mr_measure_window[1]==0:
                        estimated_mr [ds] = self.EWMA_alpha_mr1 * fp_cnt[ds]/pos_ind_cnt[ds] + (1-self.EWMA_alpha_mr1) * estimated_mr [ds] 
                        if self.finished_warmup_period[ds]: # Skip some warm-up period; later, write the results to file
                            if not(printed_mr1_for_DS[ds]):
                                printed_mr1_for_DS[ds] = True
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr[ds]))
                            pos_ind_cnt[ds] = 0
                            fp_cnt[ds]      = 0

            if self.DS2insert==None: # there was no insertion to a DS
                continue
            
            # Now we know that the request resulted in a miss, and therefore was inserted into self.DS2insert
            if self.ins_cnt[self.DS2insert] % self.min_uInterval == 0: # time to advertise
                self.DS_list[self.DS2insert].advertise_ind_full_mode (called_by_str='simulator')
                self.num_of_ads[self.DS2insert]     += 1
                self.check_warmup_ad_and_finish_report (self.DS2insert)

            if all(self.finished_report_period):
                if self.mr_type==1:
                    for ds in range(self.num_of_DSs):
                        if not(printed_mr1_for_DS[ds]):
                            print (f'Warning: did not print any results for DS {ds}') 
                return  
    

    def run_trace_estimate_mr_by_salsa_dep (self):
        """
        Estimate using SALSA_DEP estimation scheme and print to an output mr.res file either mr0, or mr1, as indicated in self.mr_tye.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        mr1, aka "the positive exclusion prob'", is the probability that an item isn't cached, given a positive indication for that item.
        Estimate mr0 and print to an output .res file mr0.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        The alg' runs the chosen naive selection alg' - that is, either "all" - which accesses all the DSs with positive ind', or "cheapest", which accesses the cheapest DS with a pos' ind'.
        Only the estimation uses a SALSA_DEP-like mechanism; in order to make a meaningful comparison with the other estimations/measurements of mr0, 
        the selection alg' is NOT salsa, but a naive DS selection alg'.   
        The choice which naive DS selection alg' to run is set by the parameter self.naive_selection_alg.
        If self.use_fna==True, whenever all indicators show a negative ind', the selection alg' picks a u.a.r. DS to access. Else, the function accesses only caches with positive indications.   
        """
        if self.mr_type==0:
            neg_ind_cnt         = np.zeros([self.num_of_DSs,self.num_of_DSs])
            tn_cnt              = np.zeros([self.num_of_DSs,self.num_of_DSs])
            estimated_mr        = np.zeros([self.num_of_DSs,self.num_of_DSs]) 
        else:
            pos_ind_cnt         = [0     for _ in range(self.num_of_DSs)]
            fp_cnt              = [0     for _ in range(self.num_of_DSs)]
            printed_mr1_for_DS  = [False for _ in range(self.num_of_DSs)]
            estimated_mr        = [self.initial_mr1 for _ in range(self.num_of_DSs)] 

        self.ins_cnt            = [0     for _ in range(self.num_of_DSs)]
        self.num_of_ads         = [0     for _ in range(self.num_of_DSs)]
        self.finished_warmup_period  = [False for _ in range(self.num_of_DSs)]
        self.finished_report_period  = [False for _ in range(self.num_of_DSs)]
        
        for ds in range(self.num_of_DSs):
            printf (self.measure_mr_res_file[ds], f'\n{self.mr_type} | salsa_dep | ')
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.handle_single_req_naive_alg() # perform data access for this req and update self.indications, self.resolution and self.DSs2accs 
            num_of_pos_inds = sum (self.indications)
            
            for ds in self.DSs2accs:

                if self.mr_type==0:
                    if self.indications[ds]==False: # negative indication for this DS
                        neg_ind_cnt[ds][num_of_pos_inds] += 1
                        if self.resolution[ds]==False:
                            tn_cnt[ds][num_of_pos_inds] += 1
                    if neg_ind_cnt[ds][num_of_pos_inds]>0 and neg_ind_cnt[ds][num_of_pos_inds] % self.mr_measure_window[0]==0:
                        estimated_mr [ds][num_of_pos_inds] = self.EWMA_alpha_mr0 * tn_cnt[ds][num_of_pos_inds]/neg_ind_cnt[ds][num_of_pos_inds] + (1-self.EWMA_alpha_mr0) * estimated_mr [ds][num_of_pos_inds] 
                        if self.finished_warmup_period[ds]: # Skip some warm-up period; later, write the results to file
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr[ds]))
                            neg_ind_cnt[ds] = 0
                            tn_cnt[ds]      = 0
                            
                else: #self.mr_type==1
                    if self.indications[ds]: # positive indication for this DS
                        pos_ind_cnt[ds] += 1
                        if self.resolution[ds]==False:
                            fp_cnt[ds] += 1

                    if pos_ind_cnt[ds]>0 and pos_ind_cnt[ds] % self.mr_measure_window[1]==0:
                        estimated_mr [ds] = self.EWMA_alpha_mr1 * fp_cnt[ds]/pos_ind_cnt[ds] + (1-self.EWMA_alpha_mr1) * estimated_mr [ds] 
                        if self.finished_warmup_period[ds]: # Skip some warm-up period; later, write the results to file
                            if not(printed_mr1_for_DS[ds]):
                                printed_mr1_for_DS[ds] = True
                            printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr[ds]))
                            pos_ind_cnt[ds] = 0
                            fp_cnt[ds]      = 0

            if self.DS2insert==None: # there was no insertion to a DS
                continue
            
            # Now we know that the request resulted in a miss, and therefore was inserted into self.DS2insert
            if self.ins_cnt[self.DS2insert] % self.min_uInterval == 0: # time to advertise
                self.DS_list[self.DS2insert].advertise_ind_full_mode (called_by_str='simulator')
                self.num_of_ads[self.DS2insert]     += 1
                self.check_warmup_ad_and_finish_report (self.DS2insert)

            if all(self.finished_report_period):
                if self.mr_type==1:
                    for ds in range(self.num_of_DSs):
                        if not(printed_mr1_for_DS[ds]):
                            print (f'Warning: did not print any results for DS {ds}') 
                return  

    def run_trace_estimate_mr_by_fnaa (self):
        """
        Estimate using FNAA estimation scheme and print to an output mr.res file either mr0, or mr1, as indicated in self.mr_tye.
        mr0, aka "the negative exclusion prob'", is the probability that an item isn't cached, given a negative indication for that item.
        mr1, aka "the positive exclusion prob'", is the probability that an item isn't cached, given a positive indication for that item.
        The alg' runs the chosen naive selection alg' - that is, either "all" - which accesses all the DSs with positive ind', or "cheapest", which accesses the cheapest DS with a pos' ind'.
        Only the estimation uses a SALSA2-like mechanism; in order to make a meaningful comparison with the other estimations/measurements of mr0, 
        the selection alg' is NOT fnaa, but a naive DS selection alg'.   
        The choice which naive DS selection alg' to run is set by the parameter self.naive_selection_alg.
        If self.use_fna==True, whenever all indicators show a negative ind', the selection alg' picks a u.a.r. DS to access. Else, the function accesses only caches with positive indications.   
        """
        pos_ind_cnt             = [0     for _ in range(self.num_of_DSs)]
        estimated_pr_of_pos_ind = [0.5   for _ in range(self.num_of_DSs)] # q[ds] will hold the estimated prob' of pos' ind' in DS ds.
        estimated_hit_ratio     = [0.5   for _ in range(self.num_of_DSs)]
        self.ins_cnt            = [0     for _ in range(self.num_of_DSs)]
        self.num_of_ads              = [0     for _ in range(self.num_of_DSs)]
        self.finished_warmup_period  = [False for _ in range(self.num_of_DSs)]
        self.finished_report_period  = [False for _ in range(self.num_of_DSs)]
        estimated_fpr           = [0.0   for _ in range(self.num_of_DSs)]
        estimated_fnr           = [0.0   for _ in range(self.num_of_DSs)]
        estimated_mr0           = [0.0   for _ in range(self.num_of_DSs)]
        estimated_mr1           = [0.0   for _ in range(self.num_of_DSs)]
        zeros_ar                = [0.0   for _ in range(self.num_of_DSs)]
        ones_ar                 = [1.0   for _ in range(self.num_of_DSs)]
        last_reported_ins_cnt   = [0     for _ in range(self.num_of_DSs)]
        last_advertised_ins_cnt = [0     for _ in range(self.num_of_DSs)]
        advertised = False
        
        # print first initialization text to the output files
        for ds in range(self.num_of_DSs):
            printf (self.measure_mr_res_file[ds], f'\n{self.mr_type} | fnaa | ')
               
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.handle_single_req_naive_alg() # perform data access for this req and update self.indications, self.resolution and self.DSs2accs 

            pos_ind_cnt = [pos_ind_cnt[ds] + (1 if self.indications[ds] else 0) for ds in range(self.num_of_DSs)] 
            if self.print_detailed_output:
                printf (self.measure_mr_res_file[ds], 'pos_ind_cnt={}, ' .format (pos_ind_cnt))
            if self.req_cnt > 0:
                if self.req_cnt < self.q_measure_window:
                    estimated_pr_of_pos_ind  = [pos_ind_cnt[ds]/self.req_cnt for ds in range(self.num_of_DSs)]
                elif self.req_cnt % self.q_measure_window == 0:
                    estimated_pr_of_pos_ind = [self.q_window_alpha * pos_ind_cnt[ds] / self.q_measure_window + (1 - self.q_window_alpha) * estimated_pr_of_pos_ind[ds] for ds in range(self.num_of_DSs)]
                    pos_ind_cnt = zeros_ar
                for ds in range(self.num_of_DSs):
                    denominator = 1 - estimated_fpr[ds] - estimated_fnr[ds]
                    estimated_hit_ratio[ds] = 1 if denominator<=0 else min (1, max (0, (estimated_pr_of_pos_ind[ds] - estimated_fpr[ds]) / denominator))

            for ds in range(self.num_of_DSs):
                if self.print_detailed_output:
                    printf (self.measure_mr_res_file[ds], 'q={:.3f}, h={:.2f}, fpr={:.3f}, fnr={:.3f}\n' .format (estimated_pr_of_pos_ind[ds], estimated_hit_ratio[ds], estimated_fpr[ds], estimated_fnr[ds]))
                    
                # Check whether need to advertise and/or finish the warmup period and do so, if needed      
                if self.ins_cnt[ds]>0 and self.ins_cnt[ds] % self.min_uInterval == 0 and last_advertised_ins_cnt[ds]!=self.ins_cnt[ds]: # time to advertise                    
                    self.DS_list[ds].stale_indicator = self.DS_list[ds].genNewSBF ()
                    if self.print_detailed_output:
                        printf (self.measure_mr_res_file[ds], 'advertised\n')                    
                    self.num_of_ads[ds] += 1
                    last_advertised_ins_cnt[ds] = self.ins_cnt[ds]
                    self.check_warmup_ad_and_finish_report (ds)
                            
            if self.DS2insert: # if the request resulted in a miss, it was inserted into self.DS2insert; thus, we may have to update the relevant estimated_fpr, estimated_fnr.
                if self.ins_cnt[self.DS2insert]%self.num_of_insertions_between_fpr_fnr_updates == 0:
                    DS = self.DS_list[self.DS2insert]
                    updated_sbf = DS.genNewSBF ()
                    Delta1      = sum (np.bitwise_and (updated_sbf.array, ~DS.stale_indicator.array)) # # of bits that are set in the updated array, and reset in the stale array.
                    B1_up       = sum (updated_sbf.array)             # Num of bits set in the updated indicator
                    B1_st       = sum (DS.stale_indicator.array)    # Num of bits set in the stale indicator
                    estimated_fpr[DS.ID] = pow ( B1_st / DS.ind_size, DS.num_of_hashes)
                    estimated_fnr[DS.ID] = 1 - pow ( (B1_up-Delta1) / B1_up, DS.num_of_hashes)

            # if needed, update the relevant mr estimations
            for ds in range(self.num_of_DSs):                            # Update the estimated mr by the updated prob' of positive indication
                
                if not(self.finished_warmup_period[ds]):
                    continue
                if (self.indications[ds]): # positive ind' --> update mr1
                    if estimated_pr_of_pos_ind[ds] == 0: 
                        estimated_mr1[ds] = 1
                    elif (estimated_fpr[ds] == 0 or # If there're no FP, then upon a positive ind', the prob' that the item is NOT in the cache is 0 
                          estimated_hit_ratio[ds] == 1): #If the hit ratio is 1, then upon ANY indication (and, in particular, positive ind'), the prob' that the item is NOT in the cache is 0
                          estimated_mr1[ds] = 0 
                    else:
                        estimated_mr1[ds] = estimated_fpr[ds] * (1 - estimated_hit_ratio[ds]) / estimated_pr_of_pos_ind[ds]
                else: # negative ind' --> update mr0
                    if estimated_fnr[ds] == 0 or estimated_pr_of_pos_ind[ds] == 1 or estimated_hit_ratio[ds] == 1:
                        estimated_mr0[ds] = 1 
                    else:
                        estimated_mr0[ds] = (1 - estimated_fpr[ds]) * (1 - estimated_hit_ratio[ds]) / (1 - estimated_pr_of_pos_ind[ds]) 
        
                estimated_mr0[ds] = max (0, min (estimated_mr0[ds], 1)) # Verify that all mr values are feasible - that is, within [0,1].
                estimated_mr1[ds] = max (0, min (estimated_mr1[ds], 1)) # Verify that all mr values are feasible - that is, within [0,1].
                if self.mr_type==0:
                    if self.ins_cnt[ds]%self.mr_measure_window[0]==0 and last_reported_ins_cnt[ds]!=self.ins_cnt[ds]:
                        printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr0[ds] if self.mr_type==0 else estimated_mr0[ds]))
                        last_reported_ins_cnt[ds] = self.ins_cnt[ds]                    
                else:
                    if self.ins_cnt[ds]%self.mr_measure_window[0]==0 and last_reported_ins_cnt[ds]!=self.ins_cnt[ds]:
                        printf (self.measure_mr_res_file[ds], '({:.0f},{:.5f}),' .format (self.ins_cnt[ds], estimated_mr1[ds] if self.mr_type==0 else estimated_mr1[ds]))
                        last_reported_ins_cnt[ds] = self.ins_cnt[ds]

            if all(self.finished_report_period): 
                return  

                
    def run_trace_opt_hetro (self):
        """
        Run a full trace as Opt access strat' when the DS costs are heterogeneous
        """
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.client_id = self.calc_client_id()
            # get the list of caches holding the request
            true_answer_DS_list = np.array([DS_id for DS_id in range(self.num_of_DSs) if (self.cur_req.key in self.DS_list[DS_id])])

            if true_answer_DS_list.size == 0: # Miss: request is indeed not found in any DS 
                self.client_list[self.client_id].comp_miss_cnt += 1
                self.insert_key_to_DSs () 
            else:  # hit
                # find the cheapest DS holding the request
                access_DS_id = true_answer_DS_list[np.argmin( np.take( self.client_DS_cost[self.client_id] , true_answer_DS_list ) )]
                # We assume here that the cost of every DS < missp
                # update variables
                self.client_list[self.client_id].total_access_cost += self.client_DS_cost[self.client_id][access_DS_id]
                if (MyConfig.VERBOSE_DETAILED_LOG in self.verbose):
                    self.client_list[self.client_id].add_DS_accessed(self.req_cnt, [access_DS_id])
                # perform access. we know it will be successful
                self.DS_list[access_DS_id].access(self.cur_req.key)
                self.client_list[self.client_id].hit_cnt += 1
            if (MyConfig.VERBOSE_FULL_RES in self.verbose):
                self.mid_report ()

    def consider_advertise (self):
        """
        Used to decide whether to send an update when updates are sent "globally", namely, by some global requests count, 
        and not by the number of insertions of each concrete DS. 
        """
        remainder = self.req_cnt % self.min_uInterval
        for ds_id in range (self.num_of_DSs):
            if (remainder == self.advertise_cycle_of_DS[ds_id]):
                self.DS_list[ds_id].advertise_ind_full_mode ()
                self.tot_num_of_updates += 1


    def run_trace_pgm_fno_hetro (self):
        """
        Run a full trace where the access strategy is the PGM, as proposed in the journal paper "Access Strategies for Network Caching".
        This algorithm is FNO: False-Negative Oblivious, namely, it never accesses a cache with a negative indication.
        """
        for self.req_cnt in range(self.trace_len): # for each request in the trace...
            if self.use_global_uInerval:
                self.consider_advertise ()
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.client_id = self.calc_client_id()
            
            # self.pos_ind_list will hold the list of DSs with positive indications
            self.pos_ind_list = np.array ([int(DS.ID) for DS in self.DS_list if (self.cur_req.key in DS.updated_indicator) ]) if self.use_only_updated_ind else \
                                np.array ([int(DS.ID) for DS in self.DS_list if (self.cur_req.key in DS.stale_indicator) ])
            if (MyConfig.VERBOSE_CNT_FN_BY_STALENESS in self.verbose):
                self.cnt_fn_by_staleness ()
            if (len(self.pos_ind_list) == 0): # No positive indications --> FNO alg' has a miss
                self.handle_miss ()
                continue       
            if (self.calc_mr_by_hist):   
                self.estimate_mr1_by_history () # Update the estimated miss rates of the DSs; the updated miss rates of DS i will be written to mr_of_DS[i]
            else: 
                # Generate a vector "indications" containing the indications - to be used by the client
                indications = np.zeros (self.num_of_DSs, dtype = 'bool') 
                for i in self.pos_ind_list:
                    indications[i] = True  
                self.mr_of_DS = self.client_list [self.client_id].estimate_mr1_mr0_by_analysis (indications, fno_mode = True)
            self.access_pgm_fno_hetro ()
            if (MyConfig.VERBOSE_FULL_RES in self.verbose):
                self.mid_report ()

    def cnt_fn_by_staleness (self):
        """
        Counts the number of False Negative events that happen, as a function of the staleness, namely,
        the number of insertions since the last advertisement of a fresh indicator.
        """
        # true_answer_DS_list will hold the list of DSs which indeed have the key
        true_answer_DS_list = np.array([DS_id for DS_id in range(self.num_of_DSs) if (self.cur_req.key in self.DS_list[DS_id])])
        for DS_id in true_answer_DS_list:
            staleness = max (self.DS_list[DS_id].ins_cnt % self.DS_list[DS_id].uInterval, 2)
            bin = int (np.ceil (np.log2 (staleness))) - 1 # bin is the lg' of the # of insertions since the last update by cache DS_id
            self.PI_hits_by_staleness[bin] += 1
            if (not (self.cur_req.key in self.DS_list[DS_id].stale_indicator)):
                self.FN_by_staleness[bin] += 1

    def cnt_mr0_by_staleness (self):
        """
        Counts the number of False Negative events that happen, as a function of the staleness, namely,
        the number of insertions since the last advertisement of a fresh indicator.
        """
        # true_answer_DS_list will hold the list of DSs which indeed have the key
        true_answer_DS_list = np.array([DS_id for DS_id in range(self.num_of_DSs) if (self.cur_req.key in self.DS_list[DS_id])])
        for DS_id in true_answer_DS_list:
            staleness = max (self.DS_list[DS_id].ins_cnt % self.DS_list[DS_id].uInterval, 2)
            bin = int (np.ceil (np.log2 (staleness))) - 1 # bin is the lg' of the # of insertions since the last update by cache DS_id
            self.PI_hits_by_staleness[bin] += 1
            if (not (self.cur_req.key in self.DS_list[DS_id].stale_indicator)):
                self.FN_by_staleness[bin] += 1

    def run_trace_pgm_fna_hetro (self):
        """
        Run a full trace where the access strategy is the PGM, as proposed in the journal paper "Access Strategies for Network Caching".
        This algorithm is FNA: False-Negative Aware, namely, it may access a cache despite a negative indication.
        """
        self.PGM_FNA_partition () # Performs the partition stage in the PGM-Staleness-Aware alg'.
        for self.req_cnt in range(self.trace_len): # for each request in the trace...
            if self.req_cnt==self.begin_log_mr_at_req_cnt:
                settings.error ('in DistCacheSimulator.begin_log_mr_at_req_cnt') #$$$$$
                self.verbose.append (MyConfig.VERBOSE_DETAILED_LOG_MR)
                self.verbose.append (MyConfig.VERBOSE_LOG_MR)
                self.init_mr_output_files ()
                for ds in range (self.num_of_DSs):
                    self.DS_list[ds].mr_output_file = self.mr_output_file[ds]

            if self.req_cnt==self.begin_log_mr_at_req_cnt + 20:
                MyConfig.error (f'DistCacheSimulator is aborting sim at req cnt {self.req_cnt}')
            if self.use_global_uInerval:
                self.consider_advertise () # If updates are sent "globally", namely, by all $s simultaneously, maybe we should send update now 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.client_id = self.calc_client_id ()
            self.indications = [self.cur_req.key in self.DS_list[i].stale_indicator for i in range (self.num_of_DSs)]
            if self.calc_mr_by_hist: 
                if self.use_perfect_hist: # theoretical alg', w perfect hist
                    self.handle_single_req_pgm_fna_mr_by_perfect_hist ()
                else: # SALSA
                    if self.hit_ratio_based_uInterval:
                        for ds_id in range(self.num_of_DSs): #$$$ we assume here there exists only a single client
                            self.DS_list[ds_id].pr_of_pos_ind_estimation = self.client_list[0].pr_of_pos_ind_estimation[ds_id]     
                    self.calc_mr_of_DSs_salsa  ()
                    self.access_pgm_fna_hetro ()
            
                    if self.hit_ratio_based_uInterval and all([DS.num_of_advertisements>0 for DS in self.DS_list]): # Need to calculate the "q", namely, the prbob of pos ind, for each CS, and all the DSs have already advertised at least one indicator
                        for client in self.client_list:
                            client.update_q (self.indications)

            else: # Use analysis to estimate mr0, mr1  (FNAA)
                self.mr_of_DS   = self.client_list [self.client_id].estimate_mr1_mr0_by_analysis (self.indications)
                self.access_pgm_fna_hetro ()
            if (MyConfig.VERBOSE_FULL_RES in self.verbose):
                self.mid_report ()

    def calc_mr_of_DSs_salsa (self): 
        """
        calc mr (aka "Exclusion probability": namely, the prob' that the data isn't in a DS, given the indication for this DS).
        This func' is used by salsa algorithms only.
        """
        if MyConfig.VERBOSE_DEBUG in self.verbose:            
            printf (self.debug_file, '\nreq_cnt={} ' .format(self.req_cnt))
            for ds in range(self.num_of_DSs):
                printf (self.debug_file, '{:.4f} ' .format (self.DS_list[ds].mr1 if self.indications[ds] else self.DS_list[ds].mr0 ))
                # self.mr_of_DS[ds] = self.DS_list[ds].mr1 if self.indications[ds] else 0.85
                self.mr_of_DS[ds] = self.DS_list[ds].mr1 if self.indications[ds] else self.DS_list[ds].mr0  # Set the mr (exclusion probability), given either a pos, or a neg, indication.
        if self.assume_ind_DSs: # assume independent exclusion prob'
            for ds in range (self.num_of_DSs):
                self.mr_of_DS[ds] = self.DS_list[ds].mr1 if self.indications[ds] else self.DS_list[ds].mr0  # Set the mr (exclusion probability), given either a pos, or a neg, indication.
            return

        # Now we know that this is an alg that considers DS inter-dependencies (aka salsa_dep)
        # Hence, for mr1, consider the single mr1 counter at each DS. For mr0, test the concrete counter with the corresponding # of pos indications as in the current request.
        self.num_of_pos_inds = sum(self.indications)
        for ds in range (self.num_of_DSs):
            if self.indications[ds]:
                self.mr_of_DS[ds] = self.DS_list[ds].mr1 
            else: 
                self.mr_of_DS[ds] = self.DS_list[ds].mr0[self.num_of_pos_inds]
        

    def handle_single_req_pgm_fna_mr_by_perfect_hist (self):
        """
        run a single request, when the algorithm mode is 'fnaa' and assuming perfect history knowledge.
        This includes:
        - Calculate mr of each datastore.
        - Access the DSs accordingly.
        - Update the stat according to the real answers (whether the item is indeed found in each cache).
        - Update mr0, mr1, accordingly.
        """
        
        for ds in range (self.num_of_DSs):
            
            # The lines below reset the estimators and counters when the DS advertises a new indicator. 
            if (self.DS_list[ds].ins_since_last_ad==0): # This DS has just sent an indicator --> reset all counters and estimations
                self.mr0[ds] = 1
                self.mr1[ds] = self.initial_mr1
                self.fp_cnt[ds], self.tn_cnt[ds], self.pos_ind_cnt[ds], self.neg_ind_cnt[ds] = 0, 0, 0, 0  
            
            self.mr_of_DS[ds] = self.mr1[ds] if self.indications[ds] else self.mr0[ds]  # Set the mr (exclusion probability), given either a pos, or a neg, indication.
        self.access_pgm_fna_hetro ()
        for ds in range (self.num_of_DSs):
            real_answer = (self.cur_req.key in self.DS_list[ds]) 
            if (self.indications[ds]):  # pos ind
                self.pos_ind_cnt[ds] += 1
                if (real_answer == False):
                    self.fp_cnt += 1 
            else:  # neg ind'
                self.neg_ind_cnt[ds] += 1
                if (real_answer == False):
                    self.tn_cnt[ds] += 1

        if self.use_EWMA: # Use Exp Weighted Moving Avg to calculate mr0 and mr1
            for ds in range (self.num_of_DSs):            
                if self.pos_ind_cnt[ds] == self.ewma_window_size:
                    
                    self.mr1[ds] = self.EWMA_alpha * float(self.fp_cnt[ds]) / float(self.ewma_window_size) + (1 - self.EWMA_alpha) * self.mr1[ds]
                    
                    if (MyConfig.VERBOSE_LOG_MR in self.verbose):
                        printf (self.mr_output_file[ds], 'last_mr1={}, emwa_mr1={}\n' 
                                .format (self.fp_cnt[ds] / self.ewma_window_size, self.mr1[ds]))
                    self.fp_cnt[ds] = 0
                    self.pos_ind_cnt [ds] = 0
                if self.neg_ind_cnt[ds] == self.ewma_window_size:
                    self.mr0[ds] = self.EWMA_alpha * self.tn_cnt[ds] / self.ewma_window_size + (1 - self.EWMA_alpha) * self.mr0[ds]
                    if (MyConfig.VERBOSE_LOG_MR in self.verbose):
                        printf (self.mr_output_file[ds], 'last_mr0={:.4f}, emwa_mr0={:.4f}\n' 
                                .format (self.tn_cnt[ds] / self.ewma_window_size, self.mr0[ds]))
                    self.tn_cnt[ds] = 0
                    self.neg_ind_cnt [ds] = 0
        else: # not using exp weighted moving avg --> use a simple flat history estimation
            for ds in range (self.num_of_DSs):
                self.mr0[ds] = (self.tn_cnt[ds] / self.neg_ind_cnt[ds]) if (self.neg_ind_cnt[ds] > 0) else 1
                self.mr1[ds] = (self.fp_cnt[ds] / self.pos_ind_cnt[ds]) if (self.pos_ind_cnt[ds] > 0) else self.initial_mr1


    def print_est_mr_func (self):
        """
        print the estimated mr (miss rate) probabilities.
        """
        
        # Estimate mr0, by letting the clients calculate mr, where they think that all the indications were negative  
        printf (self.est_mr0_output_file, 'mr0={}, ' .format (self.client_list [self.client_id].estimate_mr1_mr0_by_analysis (indications=self.zeros_ar, quiet=True))) 
        printf (self.est_mr0_output_file, 'q={}, ' .format (self.client_list [self.client_id].pr_of_pos_ind_estimation)) 
        printf (self.est_mr0_output_file, 'hit ratio={}\n' .format (self.client_list [self.client_id].hit_ratio)) 
    
    def run_simulator (self, interval_between_mid_reports):
        """
        Run a simulation, gather statistics and prints outputs
        """
        np.random.seed(self.rand_seed)
        num_of_req = self.trace_len
        self.interval_between_mid_reports = interval_between_mid_reports if (interval_between_mid_reports != None) else self.trace_len # if the user didn't request mid_reports, have only a single report, at the end of the trace
        print (f'running {self.gen_settings_str (num_of_req=num_of_req)} with verbose={self.verbose}')
        
        if (self.mode == 'measure_mr_fullKnow'):
            self.run_trace_measure_mr_full_knowledge() 
        elif (self.mode == 'measure_mr_by_salsa'):
            self.run_trace_estimate_mr_by_salsa() 
        elif (self.mode == 'measure_mr_by_salsa_dep'):
            self.run_trace_estimate_mr_by_salsa_dep() 
        elif (self.mode == 'measure_mr_by_fnaa'):
            self.run_trace_estimate_mr_by_fnaa() 
        elif (self.mode == 'measure_mr1'):
            self.run_trace_measure_mr1()
        elif (self.mode == 'measure fp fn'):
            self.run_trace_measure_fp_fn ()
        elif self.mode == 'opt':
            self.run_trace_opt_hetro ()
            self.gather_statistics ()
        elif (self.mode == 'fno'):
            self.run_trace_pgm_fno_hetro ()
            self.gather_statistics ()
        elif self.mode in ['fnaa'] or self.mode.startswith('salsa'):
            self.run_trace_pgm_fna_hetro ()
            self.gather_statistics()
        else: 
            MyConfig.error  ('Wrong mode: {}\n' .format (self.mode))

        
    def estimate_mr1_by_history (self):
        """
        Update the estimated miss rate ("exclusion probability") of each DS, based on the history.
        This estimation is good only for false-negative-oblivious algorithms, i.e. algorithms that don't access caches with negative ind'  
        """
        self.mr_of_DS = np.array([DS.mr1 for DS in self.DS_list]) # For each 1 <= i<= n, Copy the miss rate estimation of DS i to mr_of_DS(i)

    def handle_compulsory_miss (self):
        """
        Called upon a compulsory miss, namely, a fail to retreive a request from any DS, while the request is indeed not stored in any of the DSs.
        The func' increments the relevant counter, and inserts the key to self.k_loc DSs.
        """
        self.client_list[self.client_id].comp_miss_cnt += 1
        self.insert_key_to_DSs ()

    def handle_non_compulsory_miss (self):
        """
        Called upon a non-compulsory miss, namely, a fail to retreive a request from any DS, while the request is actually stored in at least one DS.
        The func' increments the relevant counter, and inserts the key to self.k_loc DSs.
        """
        self.client_list[self.client_id].non_comp_miss_cnt += 1
        if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose and sum(self.indications)>0:  
            for DS in self.DS_list:
                printf (self.mr_output_file[DS.ID], f'in DistCacheSimulator.handle_non_comp_miss(): ')
                DS.report_mr ()
        self.insert_key_to_DSs ()
        if (MyConfig.VERBOSE_DEBUG in self.verbose and self.client_list[self.client_id].non_comp_miss_cnt > self.req_cnt+1):
            MyConfig.error ('num non_comp_miss_cnt={}, req_cnt={}\n' .format (self.client_list[self.client_id].non_comp_miss_cnt, self.req_cnt))

    def insert_key_to_closest_DS(self, req):
        """
        Currently unused
        """
        # check to see if one needs to insert key to closest cache too
        if self.DS_insert_mode == 2:
            self.DS_list[self.client_id].insert(req.key)

    def insert_key_to_DSs (self):
        """
        insert key to all k_loc DSs.
        The DSs to which the key is inserted are either: 
        - Defined by the input (parsed) trace (if self.use_given_client_per_item==True)
        - Chosen as a "hash" (actually, merely a modulo calculation) of the key 
        """
        for i in range(self.k_loc):
            self.select_DS_to_insert(i).insert (key = self.cur_req.key, req_cnt = self.req_cnt)
            if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose:
                for ds in range (self.num_of_DSs):
                    printf (self.mr_output_file[ds], f'inserting missed req {self.req_cnt} to DS {self.select_DS_to_insert(i).ID}\n')
                    
    def is_compulsory_miss (self):
        """
        Returns true iff the access is compulsory miss, namely, the requested datum is indeed not found in any DS.
        """
        return (np.array([DS for DS in self.DS_list if self.cur_req.key in DS]).size == 0) # cur_req is indeed not stored in any DS 

    def find_homo_sol (self, sorted_list_of_DSs):
        """
        Find the best solution when costs are homogeneous. The alg' is based on the "potential" alg' from the paper "Access Strategies in Network Caching". 
        """
        # By default, the proposal is to access no DS, resulting in 0 access cost, and an expected miss ratio of 1
        cur_accs_cost           = 0 
        cur_expected_miss_ratio = 1
        cur_expected_total_cost = self.missp
        self.sol                = []
        for DS_id in sorted_list_of_DSs:
            nxt_accs_cost           = cur_accs_cost + 1
            nxt_expected_miss_ratio = cur_expected_miss_ratio * self.mr_of_DS[DS_id] 
            nxt_expected_total_cost = nxt_accs_cost + nxt_expected_miss_ratio * self.missp  
            if (nxt_expected_total_cost < cur_expected_total_cost): # Adding this DS indeed decreases the expected total cost
                cur_accs_cost           = nxt_accs_cost
                cur_expected_miss_ratio = nxt_expected_miss_ratio
                cur_expected_total_cost = nxt_expected_total_cost
                self.sol.append (DS_id)
            else: # Adding more DSs may only increase the total cost
                break
    
        
    def access_pgm_fno_hetro (self):
        """
        Run the PGM alg' detailed in the paper: Access Strategies for Network Caching, Journal version.
        Run PGM in its FNO (false negative oblivious) variant, namely, consider only caches with positive indications. 
        """ 

        # Partition stage
        ###############################################################################################################
        # leaf_of_DS (i,j) holds the leaf to which DS with cost (i,j) belongs, that is, log_2 (DS(i,j))

        # leaves_of_DSs_w_pos_ind will hold the leaves of the DSs with pos' ind'
        cur_num_of_leaves = np.max (np.take(self.leaf_of_DS[self.client_id], self.pos_ind_list)) + 1

        # DSs_in_leaf[j] will hold the list of DSs which belong leaf j, that is, the IDs of all the DSs with access in [2^j, 2^{j+1})
        DSs_in_leaf = [[]]
        for leaf_num in range (cur_num_of_leaves):
            DSs_in_leaf.append ([])
        for ds in (self.pos_ind_list):
            DSs_in_leaf[self.leaf_of_DS[self.client_id][ds]].append(ds)

        # Generate stage
        ###############################################################################################################
        # leaf[j] will hold the list of candidate DSs of V^0_j in the binary tree
        leaf = [[]]
        for leaf_num in range (cur_num_of_leaves-1): # Append additional cur_num_of_leaves-1 leaves
            leaf.append ([])

        for leaf_num in range (cur_num_of_leaves):

            # df_of_DSs_in_cur_leaf will hold the IDs, miss rates and access costs of the DSs in the current leaf
            num_of_DSs_in_cur_leaf = len(DSs_in_leaf[leaf_num])
            df_of_DSs_in_cur_leaf = pd.DataFrame({
                'DS ID': DSs_in_leaf[leaf_num],
                'mr': np.take(self.mr_of_DS, DSs_in_leaf[leaf_num]), #miss rate
                'ac': np.take(self.client_DS_cost[self.client_id], DSs_in_leaf[leaf_num]) #access cost
            })


            df_of_DSs_in_cur_leaf.sort_values(by=['mr'], inplace=True) # sort the DSs in non-dec. order of miss rate


            leaf[leaf_num].append(candidate.candidate ([], 1, 0)) # Insert the empty set to the leaf
            cur_mr = 1
            cur_ac = 0

            # For each prefix_len \in {1 ... number of DSs in the current leaf},
            # insert the prefix at this prefix_len to the current leaf
            for pref_len in range (1, num_of_DSs_in_cur_leaf+1):
                cur_mr *= df_of_DSs_in_cur_leaf.iloc[pref_len - 1]['mr']
                cur_ac += df_of_DSs_in_cur_leaf.iloc[pref_len - 1]['ac']
                leaf[leaf_num].append(candidate.candidate(df_of_DSs_in_cur_leaf.iloc[range(pref_len)]['DS ID'], cur_mr, cur_ac))

        # Merge stage
        ###############################################################################################################
        r = np.ceil(np.log2(self.missp)).astype('uint8')
        num_of_lvls = (np.ceil(np.log2 (cur_num_of_leaves))).astype('uint8') + 1
        if (num_of_lvls == 1): # Only 1 leaf --> nothing to merge. The candidate full solutions will be merely those in this single leaf
            cur_lvl_node = leaf
        else:
            prev_lvl_nodes = leaf
            num_of_nodes_in_prev_lvl = cur_num_of_leaves
            num_of_nodes_in_cur_lvl = np.ceil (cur_num_of_leaves / 2).astype('uint8')
            for lvl in range (1, num_of_lvls):
                cur_lvl_node = [None]*num_of_nodes_in_cur_lvl
                for j in range (num_of_nodes_in_cur_lvl):
                    if (2*(j+1) > num_of_nodes_in_prev_lvl): # handle edge case, when the merge tree isn't a full binary tree
                        cur_lvl_node[j] = prev_lvl_nodes[2*j]
                    else:
                        cur_lvl_node[j] = node.merge(prev_lvl_nodes[2*j], prev_lvl_nodes[2*j+1], r, self.missp)
                num_of_nodes_in_prev_lvl = num_of_nodes_in_cur_lvl
                num_of_nodes_in_cur_lvl = (np.ceil(num_of_nodes_in_cur_lvl / 2)).astype('uint8')
                prev_lvl_nodes = cur_lvl_node

        min_final_candidate_phi = self.missp + 1 # Will hold the total cost among by all final sols checked so far
        for final_candidate in cur_lvl_node[0]:  # for each of the candidate full solutions
            final_candidate_phi = final_candidate.phi(self.missp)
            if (final_candidate_phi < min_final_candidate_phi): # if this sol' is cheaper than any other sol' found so far', take this new sol'
                final_sol = final_candidate
                min_final_candidate_phi = final_candidate_phi

        if (len(final_sol.DSs_IDs) == 0): # the alg' decided to not access any DS
            self.handle_miss ()
            return

        # Now we know that the alg' decided to access at least one DS
        # Add the costs and IDs of the selected DSs to the statistics
        self.client_list[self.client_id].total_access_cost += final_sol.ac
        if (MyConfig.VERBOSE_DETAILED_LOG in self.verbose):
            self.client_list[self.client_id].add_DS_accessed(self.req_cnt, final_sol.DSs_IDs)

        if (self.calc_mr_by_hist):
            # perform access. the function access() returns True if successful, and False otherwise
            accesses = np.array([self.DS_list[DS_id].access(self.cur_req.key) for DS_id in final_sol.DSs_IDs])
            if any(accesses):   #hit
                self.client_list[self.client_id].hit_cnt += 1
            else:               # Miss
                self.handle_miss ()
            return

        # Now we know that the calculation of mr is not by hist
        hit = False # default value
        for DS_id in final_sol.DSs_IDs:
            if (self.DS_list[DS_id].access(self.cur_req.key)): # hit
                hit = True
                
                #Upon hit, the DS sends the update evaluation of fpr, fnr, to the clients.
                self.client_list [self.client_id].fnr[DS_id] = self.DS_list[DS_id].fnr;   
                self.client_list [self.client_id].fpr[DS_id] = self.DS_list[DS_id].fpr;  
        if (hit):
            self.client_list[self.client_id].hit_cnt += 1
        else:               # Miss
            self.handle_miss ()


    def access_pgm_fna_hetro (self):
        """
        Run the PGM alg' detailed in the paper: Access Strategies for Network Caching, Journal version.
        Run PGM in its FNA (false-negative aware) variant, namely, consider also caches with negative indications. 
        """ 

        req                     = self.cur_req

        # Partition stage is done once, statically, based on the DSs' costs
        ###############################################################################################################

        # Generate stage
        ###############################################################################################################
        cur_num_of_leaves = self.num_of_leaves[self.client_id] 
        DSs_in_leaf = self.DSs_in_leaf[self.client_id]

        # leaf[j] will hold the list of candidate DSs of V^0_j in the binary tree
        leaf = [[]]
        for leaf_num in range (cur_num_of_leaves-1): # Append additional cur_num_of_leaves-1 leaves
            leaf.append ([])

        for leaf_num in range (cur_num_of_leaves):

            # df_of_DSs_in_cur_leaf will hold the IDs, miss rates and access costs of the DSs in the current leaf
            num_of_DSs_in_cur_leaf = len(DSs_in_leaf[leaf_num])
            df_of_DSs_in_cur_leaf = pd.DataFrame({
                'DS ID': DSs_in_leaf[leaf_num],
                'mr': np.take (self.mr_of_DS, DSs_in_leaf[leaf_num]), #miss rate
                'ac': np.take (self.client_DS_cost[self.client_id], DSs_in_leaf[leaf_num]) #access cost
            })

            df_of_DSs_in_cur_leaf.sort_values(by=['mr'], inplace=True) # sort the DSs in non-dec. order of miss rate


            leaf[leaf_num].append(candidate.candidate ([], 1, 0)) # Insert the empty set to the leaf
            cur_mr = 1
            cur_ac = 0

            # For each prefix_len \in {1 ... number of DSs in the current leaf},
            # insert the prefix at this prefix_len to the current leaf
            for pref_len in range (1, num_of_DSs_in_cur_leaf+1):
                cur_mr *= df_of_DSs_in_cur_leaf.iloc[pref_len - 1]['mr']
                if MyConfig.VERBOSE_DEBUG in self.verbose and cur_mr>1 or cur_mr<0:
                    MyConfig.error (f'cur_mr={cur_mr}')                     
                cur_ac += df_of_DSs_in_cur_leaf.iloc[pref_len - 1]['ac']
                leaf[leaf_num].append(candidate.candidate(df_of_DSs_in_cur_leaf.iloc[range(pref_len)]['DS ID'], cur_mr, cur_ac))

        # Merge stage
        ###############################################################################################################
        r = np.ceil(np.log2(self.missp)).astype('uint8')
        num_of_lvls = (np.ceil(np.log2 (cur_num_of_leaves))).astype('uint8') + 1
        if (num_of_lvls == 1): # Only 1 leaf --> nothing to merge. The candidate full solutions will be merely those in this single leaf
            cur_lvl_node = leaf
        else:
            prev_lvl_nodes = leaf
            num_of_nodes_in_prev_lvl = cur_num_of_leaves
            num_of_nodes_in_cur_lvl = np.ceil (cur_num_of_leaves / 2).astype('uint8')
            for lvl in range (1, num_of_lvls):
                cur_lvl_node = [None]*num_of_nodes_in_cur_lvl
                for j in range (num_of_nodes_in_cur_lvl):
                    if (2*(j+1) > num_of_nodes_in_prev_lvl): # handle edge case, when the merge tree isn't a full binary tree
                        cur_lvl_node[j] = prev_lvl_nodes[2*j]
                    else:
                        cur_lvl_node[j] = node.merge(prev_lvl_nodes[2*j], prev_lvl_nodes[2*j+1], r, self.missp)
                num_of_nodes_in_prev_lvl = num_of_nodes_in_cur_lvl
                num_of_nodes_in_cur_lvl = (np.ceil(num_of_nodes_in_cur_lvl / 2)).astype('uint8')
                prev_lvl_nodes = cur_lvl_node

        min_final_candidate_phi = self.missp + 1 # Will hold the total cost among by all final sols checked so far
        for final_candidate in cur_lvl_node[0]:  # for each of the candidate full solutions
            final_candidate_phi = final_candidate.phi(self.missp)
            if (final_candidate_phi < min_final_candidate_phi): # if this sol' is cheaper than any other sol' found so far', take this new sol'
                final_sol = final_candidate
                min_final_candidate_phi = final_candidate_phi

        if (len(final_sol.DSs_IDs) == 0): # the alg' decided to not access any DS
            self.handle_miss ()
            return

        # Now we know that the alg' decided to access at least one DS
        # Add the costs and IDs of the selected DSs to the statistics
        self.client_list[self.client_id].total_access_cost += final_sol.ac

        # perform access
        self.sol = final_sol.DSs_IDs
        already_hit = False # will become True once accessing at least one DS for the current request results in a hit 
        if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose:
            for ds in range(self.num_of_DSs):
                printf (self.mr_output_file[ds], f'req_cnt={self.req_cnt}, inds={self.indications}, sol={self.sol}\n')
        for DS_id in self.sol:
            is_speculative_accs = not (self.indications[DS_id])
            if is_speculative_accs: #A speculative accs 
                self.                             speculate_accs_cost += self.client_DS_cost [self.client_id][DS_id] # Update the whole system's data (used for statistics)
                self.client_list [self.client_id].speculate_accs_cost += self.client_DS_cost [self.client_id][DS_id] # Update the relevant client's data (used for adaptive / learning alg') 
            if self.assume_ind_DSs: 
                # accs_was_hit will become True iff this concrete accss to this DS resulted in a hit
                accs_was_hit = self.DS_list[DS_id].access(self.cur_req.key, is_speculative_accs)
            else: 
                accs_was_hit = self.DS_list[DS_id].access_salsa_dep(self.cur_req.key, is_speculative_accs, num_of_pos_inds=self.num_of_pos_inds)
            if accs_was_hit: # hit
                if not (already_hit) and is_speculative_accs: # this is the first hit; for each speculative req, we want to count at most a single hit 
                    self.                             speculate_hit_cnt += 1  # Update the whole system's speculative hit cnt (used for statistics) 
                    self.client_list [self.client_id].speculate_hit_cnt += 1  # Update the relevant client's speculative hit cnt (used for adaptive / learning alg')
                already_hit = True
                
                # If mr is not evaluated by history, then upon hit, the DS sends the updated evaluation of fpr, fnr, to the clients 
                if (not (self.calc_mr_by_hist)): 
                    self.client_list [self.client_id].fnr[DS_id] = self.DS_list[DS_id].fnr;  
                    self.client_list [self.client_id].fpr[DS_id] = self.DS_list[DS_id].fpr;  
        if already_hit:   
            self.client_list[self.client_id].hit_cnt += 1
        else: # Miss
            self.handle_miss ()