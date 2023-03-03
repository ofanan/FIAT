import pandas as pd
import sys, pickle, random
import numpy as np
# from numpy.core._multiarray_umath import dtype

import DataStore, Client, candidate, node, MyConfig 
from   printf import printf

"""
key is an integer
"""

class Simulator(object):
    """
    A simulator that accepts system parameters (trace, number and size of caches, algorithm to run etc.), 
    runs a simulation, and outputs the results to a file.
    """
    
    # Called upon a miss. Check whether the miss is compulsory or not. 
    # Increments the relevant counter, and inserts the key to self.k_loc DSs.
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
    mid_report = lambda self : self.gather_statistics() if (self.req_cnt % self.interval_between_mid_reports == 0 and self.req_cnt>0) else None

    def gen_settings_string (self, num_of_req=None):
        """
        Returns a formatted string based on the values of the given parameters' (e.g., num of caches, trace_file_name, update intervals etc.). 
        """
        num_of_req = num_of_req if (num_of_req!=None) else self.num_of_req
        # generate the initial string, that does not include the mode information    
        settings_str = \
            '{}.C{:.0f}K.bpe{:.0f}.{:.0f}Kreq.{:.0f}DSs.Kloc{:.0f}.M{:.0f}.B{:.0f}.U{:.0f}' .format (
            self.trace_file_name, self.DS_size/1000, self.bpe, num_of_req/1000, 
            self.num_of_DSs, self.k_loc, self.missp, self.bw, self.uInterval)
        
        # Add the string representing the mode   
        if (self.mode=='opt'):
            return '{}.{}' .format (settings_str, 'Opt')

        settings_str = '{}.{}' .format (settings_str, self.mode.upper()) 

        # Now we know that the mode isn't 'Opt'
        if self.calc_mr_by_hist:
            settings_str = '{}.H{}{}' .format (
                settings_str,   
                'P' if self.use_perfect_hist else 'E', # 'E' for 'Estimated' 
                'ewma' if self.use_EWMA else 'flat')  # either exp-weighted-moving-avg, or simple, flat avg
        else: # mode isn't 'Opt', and the mr-estimation is BF-analysis-based
            settings_str = '{}A' .format (settings_str) # 'A' stands for 'by Analysis'
        
        if (self.hist_based_uInterval):
            return '{}.adH' .format (settings_str) # history-based advertisements
        else:
            return '{}.adF' .format (settings_str) # fixed-update-interval advertisements
        
                
    def init_DS_list(self):
        """
        Init a list of empty DSs (Data Stores == caches)
        """
        self.DS_list = [DataStore.DataStore(ID = i, size = self.DS_size, bpe = self.bpe, mr1_estimation_window = self.estimation_window, 
                        max_fpr = self.max_fpr, max_fnr = self.max_fnr, verbose = self.verbose, uInterval = self.uInterval,
                        num_of_insertions_between_estimations = self.num_of_insertions_between_estimations,
                        DS_send_fpr_fnr_updates  = not (self.calc_mr_by_hist),
                        mr_output_file = self.mr_output_file[i],
                        # currently the mr stat is collected for all the DSs by the simulator. The DSs don't need to collect further mr stat
                        collect_mr_stat     = not (self.use_perfect_hist),
                        analyse_ind_deltas  = True,
                        EWMA_alpha          = self.EWMA_alpha,
                        designed_mr1        = self.designed_mr1,
                        use_EWMA            = self.use_EWMA,
                        use_indicator       = not (self.mode=='opt'), # Opt doesn't really use indicators - it "knows" the actual contents of the DSs
                        hist_based_uInterval = self.hist_based_uInterval
                        ) 
                        for i in range(self.num_of_DSs)]
            
    def init_client_list(self):
        """
        Init a list of clients
        """
        
        self.client_list = [Client.Client(ID = i, num_of_DSs = self.num_of_DSs, estimation_window = self.estimation_window, verbose = self.verbose, 
        use_redundan_coef = self.use_redundan_coef, k_loc = self.k_loc, missp = self.missp,
        verbose_file = self.output_file) 
        for i in range(self.num_of_clients)]
    
    def __init__(self, output_file, trace_file_name, 
                 mode, req_df, client_DS_cost, missp=100, k_loc=1, DS_size = 10000, 
                 bpe = 14, rand_seed = 42, use_redundan_coef = False, max_fpr = 0.01, max_fnr = 0.01, verbose=[MyConfig.VERBOSE_RES], 
                 use_given_client_per_item  = False, # When true, associate each request with the client determined in the input trace ("req_df")                 
                 use_given_DS_per_item      = False, # When true, insert each missed request with the datastore(s) determined in the input trace ("req_df")
                 bw                 = 0, # Determine the update interval by a given bandwidth (currently usused)
                 uInterval          = -1, # update interval, namely, number of new insertions to a datastore between sequencing advertisements of a fresh indicator 
                 log_mr             = False, # When true, write the estimated and real miss rates (the conditional miss ratio) to a file.
                 calc_mr_by_hist    = True, # when false, calc mr by analysis of the BF
                 use_perfect_hist   = True, # when true AND calc_mr_by_hist, assume that the client always has a perfect knowledge about the fp/fn/tp/tn implied by each previous indication, by each DS (even if this DS wasn't accessed).
                 use_EWMA           = False, # when true, use Exp Window Moving Avg for estimating the mr (exclusion probabilities)  
                 hist_based_uInterval = False # when true, send advertisements according to the hist-based estimations of mr.
                 ):
        """
        Return a Simulator object with the following attributes:
            mode:               e.g. 'opt', 'fna', 'fno'
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
        self.EWMA_alpha         = 0.25  # exp' window's moving average's alpha parameter 
        self.output_file        = output_file
        self.trace_file_name    = trace_file_name
        self.missp              = missp
        self.DS_size            = DS_size
        self.bpe                = bpe
        self.rand_seed          = rand_seed
        self.DS_insert_mode     = 1  #DS_insert_mode: mode of DS insertion (1: fix, 2: distributed, 3: ego). Currently only insert mode 1 is used
        self.calc_mr_by_hist    = calc_mr_by_hist
        self.use_perfect_hist   = use_perfect_hist
        if (self.calc_mr_by_hist and not(self.use_perfect_hist)):
            self.in_exploration = True # if using practical hist, we must begin with some exploration of the mr's     
        self.use_EWMA           = use_EWMA # use Exp Weighted Moving Avg to estimate the current mr0, mr1.
        self.mode               = mode
        self.num_of_clients     = client_DS_cost.shape[0]
        self.num_of_DSs         = client_DS_cost.shape[1]
        self.k_loc              = k_loc
        if (self.DS_insert_mode != 1):
            print ('sorry, currently only fix insert mode (1) is supported')
            exit ()

        if (self.k_loc > self.num_of_DSs):
            print ('error: k_loc must be at most num_of_DSs')
            exit ()

        self.client_DS_cost     = client_DS_cost # client_DS_cost(i,j) will hold the access cost for client i accessing DS j
        self.est_win_factor     = 10
        self.estimation_window  = 100 #self.DS_size / self.est_win_factor # window for parameters' estimation 
        self.max_fnr            = max_fnr
        self.max_fpr            = max_fpr
        self.verbose            = verbose # Used for debug / analysis: a higher level verbose prints more msgs to the Screen / output file.       
                
        self.mr_of_DS           = np.zeros(self.num_of_DSs) # mr_of_DS[i] will hold the estimated miss rate of DS i 
        self.req_df             = req_df
        self.trace_len          = self.req_df.shape[0]
        self.use_redundan_coef  = use_redundan_coef
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
        self.hist_based_uInterval = hist_based_uInterval
        
        # If the uInterval is given in the input (as a non-negative value) - use it. 
        # Else, calculate uInterval by the given bw parameter.
        if (uInterval == -1): # Should calculate uInterval by the given bw parameter
            self.use_global_uInerval = True
            self.uInterval = MyConfig.bw_to_uInterval (self.DS_size, self.bpe, self.num_of_DSs, bw)
            self.update_cycle_of_DS = np.array ( [ds_id * self.uInterval / self.num_of_DSs for ds_id in range (self.num_of_DSs)]) 
        else:
            self.use_global_uInerval = False
            self.uInterval = uInterval
        self.cur_updating_DS = 0
        self.use_only_updated_ind = True if (uInterval == 1) else False
        self.num_of_insertions_between_estimations = np.uint8 (50)
        if (self.num_of_clients == 1):
            self.use_given_client_per_item = False # if there's only 1 client, all requests belong to this client, disregarding what was pre-computed in the trace file.
        else:
            self.use_given_client_per_item = use_given_client_per_item # When True, upon miss, the missed item is inserted to the location(s) specified in the given request traces input. When False, it's randomized for each miss request.
        self.use_given_DS_per_item = use_given_DS_per_item

        self.avg_DS_accessed_per_req = float(0)
        if (MyConfig.VERBOSE_CNT_FN_BY_STALENESS in self.verbose):
            lg_uInterval = np.log2 (self.uInterval).astype (int)
            self.PI_hits_by_staleness = np.zeros (lg_uInterval , dtype = 'uint32') #self.PI_hits_by_staleness[i] will hold the number of times in which a requested item is indeed found in any of the caches when the staleness of the respective indicator is at most 2^(i+1)
            self.FN_by_staleness      = np.zeros (lg_uInterval,  dtype = 'uint32') #self.FN_by_staleness[i]      will hold the number of FN events that occur when the staleness of that indicator is at most 2^(i+1)        else:

        self.designed_mr1   = 0.001 # The inherent (designed) positive exclusion prob', stemmed from inaccuracy of the indicator. Note that this is NOT exactly fpr
        if (self.calc_mr_by_hist and self.use_perfect_hist):
            self.neg_ind_cnt    = np.zeros (self.num_of_DSs)
            self.fp_cnt         = np.zeros  (self.num_of_DSs)
            self.tn_cnt         = np.zeros  (self.num_of_DSs)
            self.mr0_cur        = np.ones  (self.num_of_DSs)
            self.mr1_cur        = self.designed_mr1 * np.ones (self.num_of_DSs)
        
        self.init_client_list ()
        if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose):
            self.init_mr_output_files()
            self.zeros_ar            = np.zeros (self.num_of_DSs, dtype='uint16') 
            self.ones_ar             = np.ones  (self.num_of_DSs, dtype='uint16') 
        self.log_mr_in_warmup = True # Even if requested, begin to write this output to a file only after long warmup period.
        self.init_DS_list() #DS_list is the list of DSs

    def init_mr_output_files (self):
        """
        Init per-DS output file, to which the simulator writes data about the estimated mr (conditional miss rates, namely pr of a miss given a negative ind (mr0), or a positive ind (mr1)).
        The simulator also writes to this data (via Datastore.py) about each access whether it results in a True Positive, True Negative, False Positive, or False negative.
        """
        settings_str = self.gen_settings_string (num_of_req=self.trace_len)
        self.mr_output_file = [None]*self.num_of_DSs
        for ds in range (self.num_of_DSs):
            self.mr_output_file[ds] = open ('../res/{}_ds{}.mr' .format (settings_str, ds), 'w')

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
                

    def gather_statistics(self):
        """
        Accumulates and organizes the stat collected during the sim' run.
        This func' is usually called once at the end of each run of the python_simulator.
        """
        if not (MyConfig.VERBOSE_RES in self.verbose):
            return

        if (MyConfig.VERBOSE_CNT_FN_BY_STALENESS in self.verbose):
            printf (self.output_file, 'FN cnt by staleness      = {}\n' .format (self.FN_by_staleness))
            printf (self.output_file, 'PI hits cnt by staleness = {}\n' .format (self.PI_hits_by_staleness))
            for bin in range (len(self.FN_by_staleness)):
                printf (self.output_file, '({:.0f}, {:.07f})' .format (2**(bin+1), self.FN_by_staleness[bin]/self.PI_hits_by_staleness[bin]))
        self.total_access_cost  = np.sum ( [client.total_access_cost for client in self.client_list ] ) 
        self.hit_cnt            = np.sum ( [client.hit_cnt for client in self.client_list ] )
        self.hit_ratio          = float(self.hit_cnt) / self.req_cnt
        self.non_comp_miss_cnt  = np.sum( [client.non_comp_miss_cnt for client in self.client_list ] )
        self.comp_miss_cnt      = np.sum( [client.comp_miss_cnt for client in self.client_list ] )
        self.high_cost_mp_cnt   = np.sum( [client.high_cost_mp_cnt for client in self.client_list ] )
        self.total_cost         = self.total_access_cost + self.missp * (self.comp_miss_cnt + self.non_comp_miss_cnt + self.high_cost_mp_cnt)
        self.mean_service_cost  = self.total_cost / self.req_cnt 
        settings_str            = self.gen_settings_string (num_of_req=self.req_cnt)
        printf (self.output_file, '\n\n{} | service_cost = {}\n'  .format (settings_str, self.mean_service_cost))
        bw_in_practice =  int (round ( self.tot_num_of_updates * self.DS_size * self.bpe * (self.num_of_DSs - 1) / self.req_cnt) ) #Each update is a full indicator, sent to n-1 DSs)
        if (self.bw != bw_in_practice):
            printf (self. output_file, '//Note: requested bw was {:.0f}, but actual bw was {:.0f}\n' .format (self.bw, bw_in_practice))
        printf (self.output_file, '// tot_access_cost = {:.0f}, hit_ratio = {:.2}, non_comp_miss_cnt = {}, comp_miss_cnt = {}\n' .format 
           (self.total_access_cost, self.hit_ratio, self.non_comp_miss_cnt, self.comp_miss_cnt) )                                 
        num_of_fpr_fnr_updates = sum (DS.num_of_fpr_fnr_updates for DS in self.DS_list) / self.num_of_DSs
        printf (self.output_file, '// estimation window = {}, ' .format (self.estimation_window))
        if (self.mode == 'fna' and not(self.calc_mr_by_hist)):
            printf (self.output_file, '// num of insertions between fpr_fnr estimations = {}\n' .format (self.num_of_insertions_between_estimations))
            printf (self.output_file, '// avg num of fpr_fnr updates = {:.0f}, fpr_fnr_updates bw = {:.4f}\n' 
                                .format (num_of_fpr_fnr_updates, num_of_fpr_fnr_updates/self.req_cnt))

        if (MyConfig.VERBOSE_RES in self.verbose and self.mode=='fna'):
            printf (self.output_file, '// spec accs cost = {:.0f}, num of spec hits = {:.0f}' .format (self.speculate_accs_cost, self.speculate_hit_cnt))             
        # if (self.mode != 'opt'):
        printf (self.output_file, '\n// num of ads per DS={}' .format ([DS.num_of_advertisements for DS in self.DS_list]))
        printf (self.output_file, '\n// avg update interval = {} req' .format (float(self.req_cnt) / np.average([DS.num_of_advertisements for DS in self.DS_list])))
        if (self.hit_ratio < 0 or self.hit_ratio > 1):
            MyConfig.error ('error at simulator.gather_statistics: got hit_ratio={}. Please check the output file for details' .format (self.hit_ratio))

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
        printf (self.output_file, '({}, {})' .format (self.uInterval, self.FN_miss_cnt/self.hit_cnt))               

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
            self.mid_report ()

    def consider_send_update (self):
        """
        Used to decide whether to send an update when updates are sent "globally", namely, by some global requests count, 
        and not by the number of insertions of each concrete DS. 
        """
        if (not(self.use_global_uInerval)): # To be used only if we have a "globally calculated uInterval"
            return
        remainder = self.req_cnt % self.uInterval
        for ds_id in range (self.num_of_DSs):
            if (remainder == self.update_cycle_of_DS[ds_id]):
                self.DS_list[ds_id].send_update (check_delta_th=False)
                self.tot_num_of_updates += 1


    def run_trace_pgm_fno_hetro (self):
        """
        Run a full trace where the access strategy is the PGM, as proposed in the journal paper "Access Strategies for Network Caching".
        This algorithm is FNO: False-Negative Oblivious, namely, it never accesses a cache with a negative indication.
        """
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            self.consider_send_update ()
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


    def run_trace_pgm_fna_hetro (self):
        """
        Run a full trace where the access strategy is the PGM, as proposed in the journal paper "Access Strategies for Network Caching".
        This algorithm is FNA: False-Negative Aware, namely, it may access a cache despite a negative indication.
        """
        self.PGM_FNA_partition () # Performs the partition stage in the PGM-Staeleness-Aware alg'.
            
        for self.req_cnt in range(self.trace_len): # for each request in the trace... 
            if (MyConfig.VERBOSE_LOG_MR in self.verbose): # requested to print to output estimated and real (historic stat) about the miss rate, and the initial warmup time is finished.
                self.log_mr_in_warmup = False
            self.consider_send_update () # If updates are sent "globally", namely, by all $s simultaneously, maybe we should send update now 
            self.cur_req = self.req_df.iloc[self.req_cnt]  
            self.client_id = self.calc_client_id ()
            for i in range (self.num_of_DSs):
                self.indications[i] = True if (self.cur_req.key in self.DS_list[i].stale_indicator) else False #self.indication[i] holds the indication of DS i for the cur request
            if (self.calc_mr_by_hist):
                self.handle_single_req_pgm_fna_mr_by_perfect_hist  () if self.use_perfect_hist else \
                self.handle_single_req_pgm_fna_mr_by_practical_hist ()
            else: # Use analysis to estimate mr0, mr1 
                self.mr_of_DS   = self.client_list [self.client_id].estimate_mr1_mr0_by_analysis (self.indications)
            self.mid_report ()

    def handle_single_req_pgm_fna_mr_by_practical_hist (self):
        """
        run a single request, when the algorithm mode is 'fna' and using practical, partial history knowledge.
        The history is collected by the DSs themselves.
        """
        # handle the non-exploration case: obtain mr estimations, and access DSs accordingly
        for ds in range (self.num_of_DSs):            
            self.mr_of_DS[ds] = self.DS_list[ds].mr1_cur if self.indications[ds] else self.DS_list[ds].mr0_cur  # Set the mr (exclusion probability), given either a pos, or a neg, indication.
        self.access_pgm_fna_hetro ()

    def handle_single_req_pgm_fna_mr_by_perfect_hist (self):
        """
        run a single request, when the algorithm mode is 'fna' and assuming perfect history knowledge.
        This includes:
        - Calculate mr of each datastore.
        - Access the DSs accordingly.
        - Update the stat according to the real answers (whether the item is indeed found in each cache).
        - Update mr0, mr1, accordingly.
        """
        
        if (self.hist_based_uInterval): # in a hist-based uInterval, we need a "warmup" first advertisement
            for DS in self.ds_list:
                DS.advertise_ind () 
        for ds in range (self.num_of_DSs):
            
            # The lines below reset the estimators and counters when the DS advertises a new indicator. 
            if (self.DS_list[ds].ins_since_last_ad==0): # This DS has just sent an indicator --> reset all counters and estimations
                self.mr0_cur[ds] = 1
                self.mr1_cur[ds] = self.designed_mr1
                self.fp_cnt[ds], self.tn_cnt[ds], self.pos_ind_cnt[ds], self.neg_ind_cnt[ds] = 0, 0, 0, 0  
            
            self.mr_of_DS[ds] = self.mr1_cur[ds] if self.indications[ds] else self.mr0_cur[ds]  # Set the mr (exclusion probability), given either a pos, or a neg, indication.
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

        if (self.use_EWMA): # Use Exp Weighted Moving Avg to calculate mr0 and mr1
            for ds in range (self.num_of_DSs):            
                if (self.pos_ind_cnt[ds] == self.estimation_window):
                    
                    self.mr1_cur[ds] = self.EWMA_alpha * float(self.fp_cnt[ds]) / float(self.estimation_window) + (1 - self.EWMA_alpha) * self.mr1_cur[ds]
                    
                    if (MyConfig.VERBOSE_LOG_MR in self.verbose):
                        printf (self.mr_output_file[ds], 'last_mr1={}, emwa_mr1={}\n' 
                                .format (self.fp_cnt[ds] / self.estimation_window, self.mr1_cur[ds]))
                    self.fp_cnt[ds] = 0
                    self.pos_ind_cnt [ds] = 0
                if (self.neg_ind_cnt[ds] == self.estimation_window):
                    self.mr0_cur[ds] = self.EWMA_alpha * self.tn_cnt[ds] / self.estimation_window + (1 - self.EWMA_alpha) * self.mr0_cur[ds]
                    if (MyConfig.VERBOSE_LOG_MR in self.verbose):
                        printf (self.mr_output_file[ds], 'last_mr0={:.4f}, emwa_mr0={:.4f}\n' 
                                .format (self.tn_cnt[ds] / self.estimation_window, self.mr0_cur[ds]))
                    self.tn_cnt[ds] = 0
                    self.neg_ind_cnt [ds] = 0
        else: # not using exp weighted moving avg --> use a simple flat history estimation
            for ds in range (self.num_of_DSs):
                self.mr0_cur[ds] = (self.tn_cnt[ds] / self.neg_ind_cnt[ds]) if (self.neg_ind_cnt[ds] > 0) else 1
                self.mr1_cur[ds] = (self.fp_cnt[ds] / self.pos_ind_cnt[ds]) if (self.pos_ind_cnt[ds] > 0) else self.designed_mr1


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
        print ('running', self.gen_settings_string (num_of_req=num_of_req))
        self.interval_between_mid_reports = interval_between_mid_reports if (interval_between_mid_reports != None) else self.trace_len # if the user didn't request mid_reports, have only a single report, at the end of the trace
        if (self.mode == 'measure fp fn'):
            self.run_trace_measure_fp_fn ()
        elif self.mode == 'opt':
            self.run_trace_opt_hetro ()
            self.gather_statistics ()
        elif (self.mode == 'fno'):
            self.run_trace_pgm_fno_hetro ()
            self.gather_statistics ()
        elif (self.mode == 'fna'):
            self.speculate_accs_cost    = 0 # Total accs cost paid for speculative accs
            self.speculate_accs_cnt     = 0 # num of speculative accss, that is, accesses to a DS despite a miss indication
            self.speculate_hit_cnt      = 0 # num of hits among speculative accss
            self.indications            = np.array (range (self.num_of_DSs), dtype = 'bool')
            self.run_trace_pgm_fna_hetro ()
            self.gather_statistics()
        else: 
            printf (self.output_file, 'Wrong mode: {:.0f}\n' .format (self.mode))

        
    def estimate_mr1_by_history (self):
        """
        Update the estimated miss rate ("exclusion probability") of each DS, based on the history.
        This estimation is good only for false-negative-oblivious algorithms, i.e. algorithms that don't access caches with negative ind'  
        """
        self.mr_of_DS = np.array([DS.mr1_cur for DS in self.DS_list]) # For each 1 <= i<= n, Copy the miss rate estimation of DS i to mr_of_DS(i)

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
        self.insert_key_to_DSs ()
        if (self.client_list[self.client_id].non_comp_miss_cnt > self.req_cnt+1):
            MyConfig.error ('error: num non_comp_miss_cnt={}, req_cnt={}\n' .format (self.client_list[self.client_id].non_comp_miss_cnt, self.req_cnt))

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
                    
    def is_compulsory_miss (self):
        """
        Returns true iff the access is compulsory miss, namely, the requested datum is indeed not found in any DS.
        """
        return (np.array([DS_id for DS_id in range(self.num_of_DSs) if (self.cur_req.key in self.DS_list[DS_id])]).size == 0) # cur_req is indeed not stored in any DS 

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
        # Now we know that there exists at least one positive indication
        #self.pos_ind_list = [int(i) for i in self.pos_ind_list] # cast pos_ind_list to int

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
        hit = False
        for DS_id in final_sol.DSs_IDs:
            is_speculative_accs = not (self.indications[DS_id])
            if (is_speculative_accs): #A speculative accs 
                self.                             speculate_accs_cost += self.client_DS_cost [self.client_id][DS_id] # Update the whole system's data (used for statistics)
                self.client_list [self.client_id].speculate_accs_cost += self.client_DS_cost [self.client_id][DS_id] # Update the relevant client's data (used for adaptive / learning alg') 
            if (self.DS_list[DS_id].access(self.cur_req.key, is_speculative_accs)): # hit
                if (not (hit) and (not (self.indications[DS_id]))): # this is the first hit; for each speculative req, we want to count at most a single hit 
                    self.                             speculate_hit_cnt += 1  # Update the whole system's speculative hit cnt (used for statistics) 
                    self.client_list [self.client_id].speculate_hit_cnt += 1  # Update the relevant client's speculative hit cnt (used for adaptive / learning alg')
                hit = True
                
                # If mr is not evaluated by history, then upon hit, the DS sends the updated evaluation of fpr, fnr, to the clients 
                if (not (self.calc_mr_by_hist)): 
                    self.client_list [self.client_id].fnr[DS_id] = self.DS_list[DS_id].fnr;  
                    self.client_list [self.client_id].fpr[DS_id] = self.DS_list[DS_id].fpr;  
        if (hit):   
            self.client_list[self.client_id].hit_cnt += 1
        else: # Miss
            self.handle_miss ()
