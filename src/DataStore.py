"""
The class for a DataStore (cache).
The cache stores items using the LRU policy.
It also implements the cache-side algorithm for estimating FPR (false-positive ratio) and FNR (false-negative ratio),
as described in the paper:
"On the Power of False Negative Awareness in Indicator-based Caching Systems", Cohen, Einziger, Scalosub, ICDCS'21.
"""

import numpy as np
import mod_pylru, itertools, copy
import CountingBloomFilter as CBF
import MyConfig 
from printf import printf

class DataStore (object):

    def __init__(self, ID, size = 1000, bpe = 14, EWMA_alpha = 0.85, mr1_ewma_window_size = 100, 
                 max_fnr = 0.03, max_fpr = 0.03, verbose = [], uInterval = 1,
                 num_of_insertions_between_estimations = np.uint8 (50), # num of insertions between subsequent operations of estimating the fpr, fnr.  
                 DS_send_fpr_fnr_updates    = True, # When True, "send" (actually, merely collect) analysis of fpr, fnr, based on the # of bits set/reset in the stale and updated indicators.   
                 collect_mr_stat            = True, 
                 analyse_ind_deltas         = True,
                 designed_mr1               = 0.001, # inherent mr1, stemmed from the inherent FP of a Bloom filter.
                 use_EWMA                   = False, # when true, collect historical statistics using an Exp' Weighted Moving Avg.
                 initial_mr0                = 0.85, # initial value of mr0, before we have first statistics of the indications after the lastly advertised indicator.  
                 non_comp_miss_th           = 0.15, # if hist_based_uInterval and hit_ratio_based_uInterval, advertise an indicator each time (1-q)*(1-mr0) > mult1_th.
                 mult1_th                   = 0.22, # if hist_based_uInterval and hit_ratio_based_uInterval, advertise an indicator each time q*mr1 > mult1_th.  
                 mr0_ad_th                  = 0.7,
                 mr_output_file             = None, # When this input isn't known, log data about the mr to this file
                 use_indicator              = True, # when True, generate and maintain an indicator (BF). 
                 hist_based_uInterval       = False, # when True, advertise an indicator based on hist-based statistics (e.g., some threshold value of mr0, mr1, fpr, fnr).
                 ins_cnt_based_uInterval    = False, # when True, advertise an indicator based on the # of insertions since the last advertisement.
                 hit_ratio_based_uInterval  = False  
                 ):
        """
        Return a DataStore object with the following attributes:
            ID:                 datastore ID 
            size:               number of elements that can be stored in the datastore
            bpe:                Bits Per Element: number of cntrs in the CBF per a cached element (commonly referred to as m/n)
            EWMA_alpha:    sliding window parameter for miss-rate estimation 
            mr1_ewma_window_size:  Number of regular accesses between new performing new estimation of mr1 (prob' of a miss given a pos' ind'). 
            max_fnr, max_fpr : maximum allowed (estimated) fpr, fnr. When the estimated fnr is above max_fnr, or the estimated fpr is above mx_fpr, the DS sends an update.
                               (FPR: False Positive Ratio, FNR: False Negative Ratio).
                               currently usually unused, as the time to update is defined exclusively by the update interval.
            num_of_insertions_between_estimations : number of cache insertions between performing fresh estimations of fpr, and fnr.
                - Each time a new indicator is published, the update contains a fresh estimation, and a counter is reset. Then, each 
                  time the counter reaches num_of_insertions_between_estimations. a new fpr and fnr estimation is published, and the counter is reset.
            DS_send_fpr_fnr_updates - when True, the DS will estimate the fpr/fnr
            collect_mr_stat - when True, collect historical statistics about exclusion probabilities (mr_zero and mr_one).
            analyse_ind_deltas - When True, keep the stale (lastly-advertised) indicator and periodically compare the updated and the stale indicators to estimate (by analysis) fpr, fnr, and mr. 
            hit_ratio_based_uInterval - When True, decide when to advertise an indicator based on the estimated hit ratio     
            verbose:           how much details are written to the output
        """
        self.use_indicator           = use_indicator
        self.mr_output_file          = mr_output_file
        self.ID                      = ID
        self.cache_size              = size
        self.bpe                     = bpe
        self.BF_size                 = self.bpe * self.cache_size
        self.lg_BF_size              = np.log2 (self.BF_size) 
        self.num_of_hashes           = MyConfig.get_optimal_num_of_hashes (self.bpe)
        self.designed_fpr            = MyConfig.calc_designed_fpr (self.cache_size, self.BF_size, self.num_of_hashes)
        self.EWMA_alpha              = EWMA_alpha # "alpha" parameter of the Exponential Weighted Moving Avg estimation of mr0 and mr1
        self.initial_mr0             = initial_mr0
        self.mr0_cur                 = self.initial_mr0
        self.mr1_cur                 = 0
        self.mr1_ewma_window_size    = mr1_ewma_window_size
        self.mr0_ewma_window_size    = mr1_ewma_window_size
        self.use_EWMA                = use_EWMA # If true, use Exp' Weighted Moving Avg. Else, use flat history along the whole trace
        self.hist_based_uInterval    = hist_based_uInterval # when true, send advertisements according to the hist-based estimations of mr.
        self.ins_cnt_based_uInterval = ins_cnt_based_uInterval
        if (self.hist_based_uInterval):
            self.mr0_ad_th, self.mr1_ad_th = mr0_ad_th, 0.01 
            self.hit_ratio_based_uInterval = hit_ratio_based_uInterval
            if (self.hit_ratio_based_uInterval):
                self.non_comp_miss_th = non_comp_miss_th
            self.mult1_th            = mult1_th 
        self.fp_events_cnt           = int(0) # Number of False Positive events that happened in the current estimation window
        self.tn_events_cnt           = int(0) # Number of False Positive events that happened in the current estimation window
        self.reg_accs_cnt            = 0
        self.spec_accs_cnt           = 0
        self.max_fnr                 = max_fnr
        self.max_fpr                 = max_fpr
        self.updated_indicator       = CBF.CountingBloomFilter (size = self.BF_size, num_of_hashes = self.num_of_hashes)
        self.stale_indicator         = self.updated_indicator.gen_SimpleBloomFilter ()
        self.designed_mr1            = designed_mr1
        self.cache                   = mod_pylru.lrucache(self.cache_size) # LRU cache. for documentation, see: https://pypi.org/project/pylru/
        self.DS_send_fpr_fnr_updates = DS_send_fpr_fnr_updates # when true, need to periodically compare the stale BF to the updated BF, and estimate the fpr, fnr accordingly
        self.analyse_ind_deltas      = analyse_ind_deltas
        self.delta_th                = self.BF_size / self.lg_BF_size # threshold for number of flipped bits in the BF; below this th, it's cheaper to send only the "delta" (indices of flipped bits), rather than the full ind'         
        self.update_bw               = 0
        self.num_of_advertisements   = 0
        self.verbose                 = verbose 
        self.ins_since_last_ad       = np.uint32 (0) # cnt of insertions since the last advertisement of fresh indicator
        self.num_of_fpr_fnr_updates  = int (0) 
        self.use_only_updated_ind    = True if (uInterval == 1) else False
        self.uInterval               = uInterval if (self.use_only_updated_ind == False) else float('inf')
        self.collect_mr_stat         = collect_mr_stat
        if (self.DS_send_fpr_fnr_updates):
            self.fnr                    = 0 # Initially, there are no false indications
            self.fpr                    = 0 # Initially, there are no false indications
        
        self.num_of_insertions_between_estimations  = num_of_insertions_between_estimations
        self.ins_since_last_fpr_fnr_estimation      = int (0)
        if (MyConfig.VERBOSE_DEBUG in self.verbose):
            self.debug_file = open ("../res/fna.txt", "w")
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            self.q_file = open ('../res/q{}.txt' .format(self.ID), "w") 

    def __contains__(self, key):
        """
        test to see if key is in the cache
        enables using the syntax:
            key in datastore
        """
        return (key in self.cache)
            
    def access(self, key, is_speculative_accs = False):
        """
        - Accesses a key in the cache.
        - Return True iff the access was a hit.
        - Update the relevant cntrs (regular / spec access cnt, fp / tn cnt).
        - Update the mr0, mr1 (prob' of a miss, given a neg / pos ind'), if needed.
        """
        hit = True if (key in self.cache) else False          
        if hit: 
            self.cache[key] #Touch the element, so as to update the LRU mechanism

        # If no need to collect/print further stat, we can return
        if (not(self.collect_mr_stat)):
            return hit 
        
        # Now we know that we have to collect and print some stat
        if is_speculative_accs:
            self.spec_accs_cnt += 1
            if (not(hit)):
                self.tn_events_cnt += 1
            if (self.use_EWMA): 
                if (self.spec_accs_cnt % self.mr0_ewma_window_size == 0 and self.spec_accs_cnt>0):
                    self.update_mr0 ()
            else: # use "flat" history
                self.mr0_cur = float(self.tn_events_cnt) / float (self.spec_accs_cnt)
                # in case of flat history, tn_event_cnt and spec_accs_cnt are incremented forever; we never reset them
                if (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                    printf (self.mr_output_file, 'tn cnt={}, spec accs cnt={}, mr0={}\n' .format (self.tn_events_cnt, self.spec_accs_cnt, self.mr0_cur))
        else: # regular accs
            self.reg_accs_cnt += 1
            if (not(hit)):
                self.fp_events_cnt += 1
            if self.use_EWMA: 
                if (self.reg_accs_cnt % self.mr1_ewma_window_size == 0):
                    self.update_mr1 ()
            else: # use "flat" history
                self.mr1_cur = float(self.fp_events_cnt) / float (self.reg_accs_cnt) 
                # in case of flat history, fp_event_cnt and reg_accs_cnt are incremented forever; we never reset them
                if (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                    printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.fp_events_cnt, self.reg_accs_cnt, self.mr1_cur))
                
        return hit 

    def insert(self, key, req_cnt = -1):
        """
        - Inserts a key to the cache
        - Update the indicator
        - Check if it's time to send an update
        if key is already in the cache: return False
        otherwise: return True
        """
            # check to see if the insertion will cause the LRU key to be removed
            # if so, remove it from the updated indicator
			# Removal from the cache is implemented automatically by the cache object
        self.cache[key] = key
        if (self.use_indicator):
            if (self.cache.currSize() == self.cache.size()):
                self.updated_indicator.remove(self.cache.get_tail())
            self.updated_indicator.add(key)
            self.ins_since_last_ad                 += 1
            if (self.DS_send_fpr_fnr_updates):
                self.ins_since_last_fpr_fnr_estimation += 1
                if (self.ins_since_last_fpr_fnr_estimation == self.num_of_insertions_between_estimations): 
                    self.estimate_fnr_fpr_by_analysis (req_cnt) # Update the estimates of fpr and fnr, and check if it's time to send an update
                    self.num_of_fpr_fnr_updates += 1
                    self.ins_since_last_fpr_fnr_estimation = 0
            if self.hist_based_uInterval:
                if (self.num_of_advertisements==0 and self.ins_since_last_ad==self.uInterval): # force a "warmup" advertisement
                    return self.advertise_ind ()
            if self.ins_cnt_based_uInterval:
                if (self.ins_since_last_ad == self.uInterval):
                    self.advertise_ind ()
                
    def get_indication (self, key):
        """
        Query the (stale) indicator of this DS
        """
        if (self.use_only_updated_ind):
            return (key in self.updated_indicator)
        return (key in self.stale_indicator)

    def advertise_ind (self, check_delta_th = False):
        """
        Advertise an updated indicator.
        In practice, this means merely generate a new indicator (simple Bloom filter).
        If input check_delta_th==True then calculate the "deltas", namely, number of bits set / reset since the last update has been advertised.
        """
        
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_file, 'advertising\n') 
        self.num_of_advertisements += 1
        if (check_delta_th):
            updated_sbf = self.updated_indicator.gen_SimpleBloomFilter ()
            Delta = [sum (np.bitwise_and (~updated_sbf.array, self.stale_indicator.array)), sum (np.bitwise_and (updated_sbf.array, ~self.stale_indicator.array))]
            if (MyConfig.VERBOSE_DEBUG in self.verbose and sum (Delta) < self.delta_th):
                MyConfig.error ('sum_Delta = ', sum (Delta), 'delta_th = ', self.delta_th, 'Sending delta updates is cheaper\n')

        # Advertise an indicator by extracting a fresh (SBF) indicator from the updated (CBF) indicator 
        self.stale_indicator = self.updated_indicator.gen_SimpleBloomFilter () # "stale_indicator" is the snapshot of the current state of the ind', until the next update
        if self.analyse_ind_deltas: # Do we need to estimate fpr, fnr by analyzing the diff between the stale and updated indicators? 
            B1_st                                   = sum (self.stale_indicator.array)    # Num of bits set in the updated indicator
            self.fpr                                = pow ( B1_st / self.BF_size, self.num_of_hashes)
            self.fnr                                = 0 # Immediately after sending an update, the expected fnr is 0
        self.ins_since_last_ad = 0 # reset the cnt of insertions since the last advertisement of fresh indicator
        if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
            printf (self.mr_output_file, 'Advertising\n')
        
        if (self.collect_mr_stat):
            self.tn_events_cnt, self.fp_events_cnt, self.reg_accs_cnt, self.spec_accs_cnt = 0,0,0,0
            self.mr0_cur = self.initial_mr0
            self.mr1_cur = self.designed_mr1 

    def update_mr0(self):
        """
        update the miss-probability in case of a negative indication, using an exponential moving average.
        """
        #if (self.spec_accs_cnt==self.tn_events_cnt): # this is the first 
        self.mr0_cur = self.EWMA_alpha * float(self.tn_events_cnt) / float (self.mr0_ewma_window_size) + (1 - self.EWMA_alpha) * self.mr0_cur 
        if ((MyConfig.VERBOSE_LOG_MR in self.verbose) or (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose)): 
            printf (self.mr_output_file, 'tn cnt={}, spec accs cnt={}, mr0={:.4f}\n' .format (self.tn_events_cnt, self.spec_accs_cnt, self.mr0_cur))

        if self.hist_based_uInterval:
            if (self.hit_ratio_based_uInterval):
                if (MyConfig.VERBOSE_LOG_Q in self.verbose):
                    printf (self.q_file, 'in update mr0: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, reg accs cnt={}\n' 
                            .format (self.pr_of_pos_ind_estimation, self.mr0_cur, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur), self.mr1_cur, self.pr_of_pos_ind_estimation*self.mr1_cur, self.reg_accs_cnt)) 
                if ((self.num_of_advertisements>0) and (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur) > self.non_comp_miss_th):
                    if (MyConfig.VERBOSE_LOG_Q in self.verbose):
                        printf (self.q_file, 'calling from mr0\n')                     
                    self.advertise_ind()
            else:
                if self.mr0_cur < self.mr0_ad_th: 
                    self.advertise_ind()
        self.tn_events_cnt = int(0)
        
    def update_mr1(self):
        """
        update the miss-probability in case of a positive indication, using an exponential moving average.
        """
        self.mr1_cur = self.EWMA_alpha * float(self.fp_events_cnt) / float (self.mr1_ewma_window_size) + (1 - self.EWMA_alpha) * self.mr1_cur 
        if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
            printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.fp_events_cnt, self.reg_accs_cnt, self.mr1_cur))
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_file, 'in update mr1: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, reg accs cnt={}\n' 
                    .format (self.pr_of_pos_ind_estimation, self.mr0_cur, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur), self.mr1_cur, self.pr_of_pos_ind_estimation*self.mr1_cur, self.reg_accs_cnt)) 
        if self.hist_based_uInterval and (self.num_of_advertisements>0):
            if (self.hit_ratio_based_uInterval):
                if (self.pr_of_pos_ind_estimation*self.mr1_cur > self.mult1_th):
                    if (MyConfig.VERBOSE_LOG_Q in self.verbose):
                        printf (self.q_file, 'calling from mr1\n')                     
                    self.advertise_ind()
            else:           
                if self.mr1_cur > self.mr1_ad_th: 
                    self.advertise_ind()
        self.fp_events_cnt = int(0)
        
    def print_cache(self, head = 5):
        """
        test to see if key is in the cache
        """
        for i in itertools.islice(self.cache.dli(),head):
            print (i.key)
    
    def estimate_fnr_fpr_by_analysis (self, req_cnt = -1, key = -1):
        """
        Estimates the fnr and fpr, based on the diffs between the updated and the stale indicators. 
         (see the paper: "False Rate Analysis of Bloom Filter Replicas in Distributed Systems").
        The new values are written to self.fnr_fpr, where self.fnr_fpr[0] is the fnr, and self.fnr_fpr[1] is the fpr
        The optional inputs req_cnt and key are used only for debug.
        """
        updated_sbf = self.updated_indicator.gen_SimpleBloomFilter ()
        # Delta[0] will hold the # of bits that are reset in the updated array, and set in the stale array.
        # Delta[1] will hold the # of bits that are set in the updated array, and reset in the stale array.
        Delta       = [sum (np.bitwise_and (~updated_sbf.array, self.stale_indicator.array)), sum (np.bitwise_and (updated_sbf.array, ~self.stale_indicator.array))]
        B1_up       = sum (updated_sbf.array)             # Num of bits set in the updated indicator
        B1_st       = sum (self.stale_indicator.array)    # Num of bits set in the stale indicator
        self.fnr    = 1 - pow ( (B1_up-Delta[1]) / B1_up, self.num_of_hashes)
        self.fpr    = pow ( B1_st / self.BF_size, self.num_of_hashes)
        self.ins_since_last_fpr_fnr_estimation  = 0
