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
import SimpleBloomFilter   as SBF
import MyConfig 
from printf import printf

class DataStore (object):

    # estimate_bw_of_candidate_indSize = lambda self, cur_bw_of_delta_ads_per_ins, curIndSize_lg_curIndSize i : cur_bw_of_delta_ads_per_ins*self.indS   

    # estimated_bw_of_cadnidate   = [self.potential_indSize[i] + bw_coeff*self.potential_indSize_lg_indSize[i] for i in range(len(self.potential_indSize))]

    def __init__(self, 
         ID,                             # datastore ID
         num_of_DSs,                     # overall number of DSs in the system
         size                   = 1000,  # number of elements that can be stored in the datastore
         bpe                    = 14,    # Bits Per Element: number of cntrs in the CBF per a cached element (commonly referred to as m/n)
         EWMA_alpha             = 0.85,  # sliding window parameter for miss-rate estimation
         EWMA_alpha_mr0         = 0.85,
         EWMA_alpha_mr1         = 0.85,
         mr1_ewma_window_size   = 100,   # Number of regular accesses between new performing new estimation of mr1 (prob' of a miss given a pos' ind'). 
         max_fnr = 0.03,max_fpr = 0.03,  # maximum allowed (estimated) fpr, fnr. When the estimated fnr is above max_fnr, or the estimated fpr is above mx_fpr, the DS sends an update.
                                         # fpr: False Positive Ratio, fnr: False Negative Ratio).
                                         # currently max_fnr, max_fpr are usually unused, 
         num_of_insertions_between_fpr_fnr_updates = np.uint8 (50), # num of insertions between subsequent operations of estimating the fpr, fnr.
                                                                # Each time a new indicator is published, the updated indicator contains a fresh estimation, and a counter is reset. 
                                                                # Then, each time the counter reaches num_of_insertions_between_fpr_fnr_updates. a new fpr and fnr estimation is published, and the counter is reset.
         verbose                    = [],# what output will be written. See macros in MyConfig.py 
         min_uInterval              = 100, # min num of insertions of new items into the cache before advertising again
         uInterval_factor           = 1, 
         send_fpr_fnr_updates       = True, # When True, "send" (actually, merely collect) analysis of fpr, fnr, based on the # of bits set/reset in the stale and updated indicators.   
         collect_mr_stat            = True,  
         analyse_ind_deltas         = True, # analyze the differences between the stale (last advertised) and the current, updated, indicator
         designed_mr1               = 0.001, # inherent mr1, stemmed from the inherent FP of a Bloom filter.
         use_EWMA                   = False, # when true, collect historical statistics using an Exp' Weighted Moving Avg.
         initial_mr0                = 0.88, # initial value of mr0, before we have first statistics of the indications after the lastly advertised indicator.  
         initial_mr1                = 0, # initial value of mr1, before we have first statistics of the indications after the lastly advertised indicator.  
         non_comp_miss_th           = 0.15, # if (!use_fixed_uInterval) AND hit_ratio_based_uInterval, advertise an indicator each time (1-q)*(1-mr0) > non_comp_miss_th.
         non_comp_accs_th           = 0.02, # if (!use_fixed_uInterval) AND hit_ratio_based_uInterval, advertise an indicator each time q*mr1 > non_comp_accs_th.
         mr0_ad_th                  = 0.9,
         mr1_ad_th                  = 0.01,
         mr_output_file             = None, # When this input isn't known, log data about the mr to this file
         use_indicator              = True, # when True, generate and maintain an indicator (BF).
         use_CountingBloomFilter    = False, # When True, keep both an "updated" CBF, and a "stale" simple BF, that is generated upon each advertisement. When False, use only a single, simple Bloom filter, that will be generated upon each advertisement (thus becoming stale).
         hit_ratio_based_uInterval  = False, # when True, consider the hit ratio when deciding whether to advertise a new indicator.
         settings_str               = "",    # a string that details the parameters of the current run. Used when writing to output files, as defined by verbose.
         scale_ind_delta_factor     = 1,     # multiplicative factor for the indicator size, while in delta mode. To be used by modes that scale it ('salsa2').         
         scale_ind_full_factor      = 1,     # multiplicative factor for the indicator size, while in full mode. To be used by modes that scale it ('salsa2').
         consider_delta_updates     = False, # when True, calculate the "deltas", namely, number of indicator's bits flipped since the last advertisement.  
         init_mr0_after_each_ad     = False,
         init_mr1_after_each_ad     = False,
         use_fixed_uInterval        = True,
         use_global_uInerval        = False,
         assume_ind_DSs             = True, # assume that the DSs, and in particular the exclusion prob' (the prob' that a req' datum isn't in the $, given its ind') are  mutuallyindependent.
         min_feasible_uInterval     = 10,
         delta_mode_period_param    = 10, # length of "sync periods" of the indicator's scaling alg.
         full_mode_period_param     = 10, # length of "period" that evaluates the benefits of switching to delta mode while being in full mode
         do_not_advertise_upon_insert = True,
         ):
        """
        Return a DataStore object. 
            For the DataStore's see documentation within the __init__ function.
        """
        self.ID                     = ID
        self.num_of_DSs             = num_of_DSs
        self.verbose                = verbose
        self.DS_size                = size
        self.cache                  = mod_pylru.lrucache(self.DS_size) # LRU cache. for documentation, see: https://pypi.org/project/pylru/
        self.settings_str           = settings_str
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            self.q_output_file = open ('../res/q{}_{}.txt' .format(self.ID, self.settings_str), "w") 
        self.collect_mr_stat        = collect_mr_stat
        self.use_indicator          = use_indicator # used e.g. for Opt, that merely checks whether the requested item is indeed cached
        if not(self.use_indicator): # if no indicator is used, no need for all the further fields
            return

        # inializations related to the indicator, statistics, and advertising mechanism
        self.init_mr0_after_each_ad = init_mr0_after_each_ad
        self.init_mr1_after_each_ad = init_mr1_after_each_ad
        self.consider_delta_updates = consider_delta_updates
        self.in_delta_mode          = self.consider_delta_updates # if considering delta updates, start in delta updates mode
        self.use_fixed_uInterval    = use_fixed_uInterval
        self.do_not_advertise_upon_insert = do_not_advertise_upon_insert
        # self.updated_mr0           = False # indicates whether mr0 wasn't updated since the last advertisement 
        # self.updated_mr1           = False # indicates whether mr1 wasn't updated since the last advertisement
        self.scale_ind_delta_factor  = scale_ind_delta_factor # multiplicative factor for the indicator size. To be used by modes that scale it ('salsa3').
        self.scale_ind_full_factor   = scale_ind_full_factor # multiplicative factor for the indicator size. To be used by modes that scale it ('salsa3').
        self.overall_ad_size         = 0
        self.num_of_full_ads         = 0
        self.num_of_periods_in_delta_ads  = 0
        self.total_ad_size_in_this_period = 0 # the ind' may be scaled, so need to measure the overall ind' size
        self.min_bpe                 = 10
        self.max_bpe                 = 15
        self.mr_output_file          = mr_output_file
        self.bpe                     = bpe
        self.ind_size                = self.bpe * self.DS_size
        self.lg_ind_size             = np.log2 (self.ind_size) 
        self.num_of_hashes           = MyConfig.get_optimal_num_of_hashes (self.bpe)
        self.use_CountingBloomFilter = use_CountingBloomFilter
        if use_CountingBloomFilter: 
            self.updated_indicator   = CBF.CountingBloomFilter (size = self.ind_size, num_of_hashes = self.num_of_hashes)
            self.stale_indicator     = self.updated_indicator.gen_SimpleBloomFilter ()
            if self.scale_ind_delta_factor!=1 or self.scale_ind_full_factor!=1:
                MyConfig.error ('Sorry. Scaling an indicator is not supported for CountingBloomFilter')
        else:
            self.stale_indicator        = SBF.SimpleBloomFilter (size = self.ind_size, num_of_hashes = self.num_of_hashes)
        self.EWMA_alpha                 = EWMA_alpha # "alpha" parameter of the Exponential Weighted Moving Avg estimation of mr0 and mr1
        self.EWMA_alpha_mr0             = EWMA_alpha_mr0 # "alpha" parameter of the Exponential Weighted Moving Avg estimation of mr0 
        self.EWMA_alpha_mr1             = EWMA_alpha_mr1 # "alpha" parameter of the Exponential Weighted Moving Avg estimation of mr0 
        self.initial_mr0                = initial_mr0
        self.initial_mr1                = initial_mr1
        self.assume_ind_DSs             = assume_ind_DSs
        self.use_EWMA                   = use_EWMA # If true, use Exp' Weighted Moving Avg. Else, use flat history along the whole trace
        self.mr1_ewma_window_size       = mr1_ewma_window_size
        self.mr1                        = self.initial_mr1
        self.fp_cnt                     = int(0) # Number of False Positive events that happened in the current estimation window
        if self.assume_ind_DSs:
            self.mr0                    = self.initial_mr0
            self.mr0_ewma_window_size   = mr1_ewma_window_size
            self.tn_cnt                 = int(0) # Number of False Positive events that happened in the current estimation window
            self.spec_accs_cnt          = int(0)
        else:
            self.tn_cnt                 = [0]               *self.num_of_DSs 
            self.spec_accs_cnt          = [0]               *self.num_of_DSs
            self.mr0                    = [self.initial_mr0]*self.num_of_DSs
        if not (self.use_fixed_uInterval):
            self.hit_ratio_based_uInterval = hit_ratio_based_uInterval
            if (self.hit_ratio_based_uInterval):
                self.non_comp_miss_th = non_comp_miss_th
                self.non_comp_accs_th = non_comp_accs_th
            else:
                self.mr0_ad_th, self.mr1_ad_th = mr0_ad_th, mr1_ad_th 
        
        
        self.reg_accs_cnt            = 0
        self.max_fnr                 = max_fnr
        self.max_fpr                 = max_fpr
        self.designed_fpr            = MyConfig.calc_designed_fpr (self.DS_size, self.ind_size, self.num_of_hashes)
        self.initial_mr1             = self.designed_fpr
        self.send_fpr_fnr_updates    = send_fpr_fnr_updates # when true, need to periodically compare the stale BF to the updated BF, and estimate the fpr, fnr accordingly
        self.analyse_ind_deltas      = analyse_ind_deltas
        self.delta_th                = self.ind_size / self.lg_ind_size # threshold for number of flipped bits in the BF; below this th, it's cheaper to send only the "delta" (indices of flipped bits), rather than the full ind'         
        self.update_bw               = 0
        self.num_of_advertisements   = 0
        self.ins_cnt_in_this_period = 0 # cnt of insertions since the last advertisement of fresh indicator
        self.num_of_fpr_fnr_updates  = int (0) 
        self.min_uInterval           = min_uInterval
        self.min_feasible_uInterval  = min_feasible_uInterval
        self.uInterval_factor        = uInterval_factor
        self.delta_mode_period_param = delta_mode_period_param
        self.full_mode_period_param  = full_mode_period_param
        self.num_of_ads_in_full_mode_period = 0
        self.re_init_mr0_param       = 10 
        self.bw_budget               = self.ind_size / self.min_uInterval # [bits / insertion]
        if MyConfig.VERBOSE_LOG_MR in self.verbose:
            printf (self.mr_output_file, 'bw budget={:.2f}\n' .format (self.bw_budget)) 
        self.ins_cnt_since_last_full_ad = 0 # cnt of insertions since the last advertisement of fresh indicator
        if MyConfig.VERBOSE_LOG_Q in self.verbose:
            printf (self.q_output_file, 'bw budget={:.2f}\n' .format (self.bw_budget)) 
 
        self.use_only_updated_ind    = True if (self.uInterval_factor * self.min_uInterval == 1) else False
        if (self.send_fpr_fnr_updates):
            self.fnr                 = 0 # Initially, there are no false indications
            self.fpr                 = 0 # Initially, there are no false indications
        
        self.num_of_insertions_between_fpr_fnr_updates  = num_of_insertions_between_fpr_fnr_updates
        self.ins_since_last_fpr_fnr_estimation      = int (0)

        self.num_of_sync_ads = int(0)       
        
        # Pre-computation for the potential indicator's sizes  
        if self.consider_delta_updates and self.scale_ind_delta_factor!=1: # if needed, pre-compute values for Lambert function (scaling of the ind' at delta mode)
            bpe                         = self.min_bpe
            self.potential_indSize      = []
            while bpe <= self.max_bpe:
                self.potential_indSize.append (int (bpe * self.DS_size))
                bpe *= self.scale_ind_delta_factor
            self.potential_indSize.append (self.max_bpe*self.DS_size)
            self.potential_indSize.append (self.bpe*self.DS_size)
            self.potential_indSize.sort()
            self.potential_indSize_lg_indSize = np.array ([item*np.log2(item) for item in self.potential_indSize])
            
    def __contains__(self, key):
        """
        test to see if key is in the cache
        enables using the syntax:
            key in datastore
        """
        return (key in self.cache)
            
    def access_salsa_dep (self, key, is_speculative_accs=False, num_of_pos_inds=0):
        """
        - Accesses a key in the cache using the salsa_dep alg'.
        - Return True iff the access was a hit.
        - Update the relevant cntrs (regular / spec access cnt, fp / tn cnt).
        - Update the mr0, mr1 (prob' of a miss, given a neg / pos ind'), if needed.
        """
        hit = key in self.cache          
        if hit: 
            self.cache[key] #Touch the element, so as to update the LRU mechanism

        # Now we know that we have to collect and print some stat
        self.num_of_pos_inds = num_of_pos_inds
        if is_speculative_accs:
            self.spec_accs_cnt[self.num_of_pos_inds] += 1
            if (not(hit)):
                self.tn_cnt[self.num_of_pos_inds] += 1
                if self.spec_accs_cnt[self.num_of_pos_inds]<100:
                    self.mr0[self.num_of_pos_inds] = self.initial_mr0
                else:
                    self.mr0[self.num_of_pos_inds] = float(self.tn_cnt[self.num_of_pos_inds]) / float (self.spec_accs_cnt[self.num_of_pos_inds])
                # in case of flat history, tn_event_cnt and spec_accs_cnt are incremented forever; we never reset them
                if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose: 
                    printf (self.mr_output_file, f'ins cnt since last full ad={self.ins_cnt_since_last_full_ad}, tn cnt={self.tn_cnt}, spec accs cnt={self.spec_accs_cnt}, mr0={self.mr0}\n')
        else: # regular accs
            self.reg_accs_cnt += 1
            if (not(hit)):
                self.fp_cnt += 1
            if self.use_EWMA: 
                if (self.reg_accs_cnt % self.mr1_ewma_window_size == 0):
                    self.update_mr1 ()
            else: # use "flat" history
                self.mr1 = float(self.fp_cnt) / float (self.reg_accs_cnt) 
                # in case of flat history, fp_event_cnt and reg_accs_cnt are incremented forever; we never reset them
                if (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                    printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.fp_cnt, self.reg_accs_cnt, self.mr1))
                
        return hit 

    
    def access (self, key, is_speculative_accs=False):
        """
        - Accesses a key in the cache.
        - Return True iff the access was a hit.
        - Update the relevant cntrs (regular / spec access cnt, fp / tn cnt).
        - Update the mr0, mr1 (prob' of a miss, given a neg / pos ind'), if needed.
        """
        hit = key in self.cache          
        if hit: 
            self.cache[key] #Touch the element, so as to update the LRU mechanism

        # If no need to collect/print further stat, we can return
        if (not(self.collect_mr_stat)):
            return hit 
        
        # Now we know that we have to collect and print some stat
        if is_speculative_accs:
            self.spec_accs_cnt += 1
            if (not(hit)):
                self.tn_cnt += 1
            if self.use_EWMA: 
                if self.spec_accs_cnt % self.mr0_ewma_window_size == 0 and self.spec_accs_cnt>0:
                    self.update_mr0 ()
            else: # use "flat" history
                self.mr0 = float(self.tn_cnt) / float (self.spec_accs_cnt)
                # in case of flat history, tn_event_cnt and spec_accs_cnt are incremented forever; we never reset them
                if MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose: 
                    printf (self.mr_output_file, f'ins cnt since last full ad={self.ins_cnt_since_last_full_ad}, tn cnt={self.tn_cnt}, spec accs cnt={self.spec_accs_cnt}, mr0={self.mr0}\n')
        else: # regular accs
            self.reg_accs_cnt += 1
            if (not(hit)):
                self.fp_cnt += 1
            if self.use_EWMA: 
                if (self.reg_accs_cnt % self.mr1_ewma_window_size == 0):
                    self.update_mr1 ()
            else: # use "flat" history
                self.mr1 = float(self.fp_cnt) / float (self.reg_accs_cnt) 
                # in case of flat history, fp_event_cnt and reg_accs_cnt are incremented forever; we never reset them
                if (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                    printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.fp_cnt, self.reg_accs_cnt, self.mr1))
                
        return hit 

    def insert (self, key, req_cnt=None, mr_vec=None):
        """
        If using an indicator:
        - If we maintain a Counting Bloom Filter (that should always reflect the list of cached items):         
            - If the cache is full:
                remove the victim element from the CBF.
            - Inserts the new key to the CBF
            - Inserts the new key to the cache and return
        - Else:
            - Inserts a key to the cache and return
        - If it's time to send an update, then send an update.
        """
        self.req_cnt = req_cnt
        self.mr_vec  = mr_vec
        
        if not (self.use_indicator):
            self.cache[key] = key
            return

        # now we know that we're using an indicator --> update insertions' cntrs.        
        self.ins_cnt_since_last_full_ad += 1
        self.ins_cnt_in_this_period     += 1
        if self.use_CountingBloomFilter:
            if (self.cache.currSize() == self.cache.size( )): # if cache is full, remove the victim item from the CBF
                self.updated_indicator.remove(self.cache.get_tail())
            self.updated_indicator.add(key)
        self.cache[key] = key
        if (self.send_fpr_fnr_updates):
            self.ins_since_last_fpr_fnr_estimation += 1
            if (self.ins_since_last_fpr_fnr_estimation == self.num_of_insertions_between_fpr_fnr_updates):
                self.estimate_fnr_fpr_by_analysis () # Update the estimates of fpr and fnr, and check if it's time to send an update
                self.num_of_fpr_fnr_updates           += 1
                self.ins_since_last_fpr_fnr_estimation = 0
        
        if self.do_not_advertise_upon_insert: # advertisements are dictated by central cntrlr - no need to locally consider  advertisement 
            return

        if self.use_fixed_uInterval:
            if self.ins_cnt_since_last_full_ad == self.min_uInterval:
                self.advertise_ind_full_mode(called_by_str='fixed uInterval')
                self.ins_cnt_since_last_full_ad = 0 
            return

        # now we know that this is an alg' that dynamically-scales the uInterval 
        if self.in_delta_mode:
            self.handle_ind_delta_mode ()
        else:
            self.handle_ind_full_mode ()

    def scale_ind_full_mode (self, factor):
        """
        scale the indicator and the update interval by a given factor.
        """
        self.bpe           *= factor
        self.min_uInterval  = int (self.min_uInterval * factor)
        self.ind_size       = int (self.ind_size       * factor) 
        self.num_of_hashes  = MyConfig.get_optimal_num_of_hashes (self.bpe)

    
    def get_indication (self, key):
        """
        Query the (stale) indicator of this DS
        """
        if (self.use_only_updated_ind):
            return (key in self.updated_indicator)
        return (key in self.stale_indicator)

    def genNewSBF (self):
        """
        Generate a new Simple Bloom Filter that represents all the currently cached items.
        """
        sbf = SBF.SimpleBloomFilter (size = self.ind_size, num_of_hashes = self.num_of_hashes)
        sbf.add_all (keys=[key for key in self.cache])
        return sbf

    def handle_ind_delta_mode (self, 
                       called_by_str = 'Unknown' # an optional string, identifying the caller.     
                       ):
        """
        Advertise an updated indicator, while in delta mode:
        - Assign the "stale BF" as the current update BF.
        - Update the advertisements bit count, ins cnt and bw accordingly.
        - If a full period have passed, reset the relevant counters.
        In practice, this means merely generate a new indicator (simple Bloom filter).
        """
        
        if self.ins_cnt_since_last_full_ad>=self.delta_mode_period_param * self.min_uInterval: # time to consider scaling, or at least send a keep-alive full ind'

            if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                printf (self.mr_output_file, f'\nfinished a period\n')                     
            self.num_of_periods_in_delta_ads += 1
            if self.scale_ind_delta_factor!=1:                                          
                self.scale_ind_delta_mode ()
            self.overall_ad_size               += self.ind_size # need to advertise a full ind' once in a period.
            if self.use_CountingBloomFilter: # extract the SBF from the updated CBF
                self.stale_indicator            = self.updated_indicator.gen_SimpleBloomFilter ()
            else:
                self.stale_indicator            = self.genNewSBF ()
            if MyConfig.VERBOSE_LOG_MR: 
                printf (self.mr_output_file, f'finished a delta period - advertising a full ind. ins_cnt_in_this_period={self.ins_cnt_since_last_full_ad}, mr0={self.mr0}, spec_cnt={self.spec_accs_cnt}\n') 
            self.num_of_advertisements         += 1

            cur_bw_of_delta_ads_per_ins = (self.total_ad_size_in_this_period + self.ind_size) / self.ins_cnt_since_last_full_ad
            
            if cur_bw_of_delta_ads_per_ins > self.bw_budget:
                # print ('Switching back to full cntr mode') 
                self.in_delta_mode = False

            self.num_of_sync_ads               += 1 
            self.ins_cnt_since_last_full_ad     = 0
            self.total_ad_size_in_this_period   = 0
            return # finished advertising an indicator
        
        if self.ins_cnt_since_last_full_ad % self.min_feasible_uInterval == 0:

            self.gen_updated_sbf()
            ad_size                             = int (np.log2 (self.ind_size) * np.sum ([np.bitwise_xor (self.updated_sbf.array, self.stale_indicator.array)]))
            self.total_ad_size_in_this_period  += ad_size
            self.overall_ad_size               += ad_size                              
            self.stale_indicator                = self.updated_sbf
            self.num_of_advertisements         += 1
            if MyConfig.VERBOSE_LOG_MR in self.verbose: 
                printf (self.mr_output_file, 'advertising delta. ind size={}, ad_size={}, ins_cnt_in_this_period={}, bw_in_cur_interval={:.1f}, mr0={:.3f}, spec_cnt={}\n' .format 
                        (self.ind_size, ad_size, self.ins_cnt_since_last_full_ad, self.total_ad_size_in_this_period / self.ins_cnt_since_last_full_ad, self.mr0, self.spec_accs_cnt))

    def handle_ind_full_mode (self):
        """
        Advertise an updated indicator, while in full mode:
        """
        if self.ins_cnt_since_last_full_ad == self.min_uInterval * self.uInterval_factor:
            if self.consider_delta_updates:
                if self.delta_update_is_cheaper():
                    self.num_of_ads_in_full_mode_period += 1
                if self.num_of_ads_in_full_mode_period==self.full_mode_period_param:                 
                    self.advertise_switch_to_delta_update()
                self.num_of_delta_ads_in_full_mode  = 0
                self.num_of_ads_in_full_mode_period = 0
            else:
                self.advertise_ind_full_mode (called_by_str='max_uInterval')
                self.ins_cnt_since_last_full_ad = 0 
            return
       
        # now we know that this is an alg' that dynamically-scales the uInterval, in Full mode 
        if (self.ins_cnt_since_last_full_ad==self.min_uInterval):
            if self.consider_delta_updates and self.delta_update_is_cheaper():
                self.advertise_switch_to_delta_update()
                return
            
        if (self.ins_cnt_since_last_full_ad>=self.min_uInterval):
            if self.should_advertise_by_mr0 (): 
                self.advertise_ind_full_mode (called_by_str='mr0')
                self.ins_cnt_since_last_full_ad = 0
                return
        
            if self.should_advertise_by_mr1 ():
                self.advertise_ind_full_mode (called_by_str='mr1')
                self.ins_cnt_since_last_full_ad = 0
                return
       
    def delta_update_is_cheaper (self):
        """
        Check whether advertising a delta requires less bits than advertising a full ind.
        - Update the fields
            - self.delta_ad_size (size of the delta update).
            - self.updated_sbf (a Simple Bloom Filter, representing the currently-cached items).
        - Returns true iff advertising a delta requires less bits than advertising a full ind. 
        """
        self.gen_updated_sbf()
        self.delta_ad_size = int (np.log2 (self.ind_size) * np.sum ([np.bitwise_xor (self.updated_sbf.array, self.stale_indicator.array)]))
        if MyConfig.VERBOSE_LOG_MR in self.verbose:
            printf (self.mr_output_file, 'delta_ad_size={}, ind size={}\n' .format (self.delta_ad_size, self.ind_size)) 
        
        return (self.delta_ad_size / self.ind_size) < 1 - 1/self.delta_mode_period_param
    
    def advertise_switch_to_delta_update (self):
        """
        Advertise a delta update after a period of full indicators:
        - Update relevant counters.
        - Assign self.stale_indicator <-- self.updated_sbf (update Simple Bloom Filter)  
        - If requested by self.verbose, print to log files.
        """
        if MyConfig.VERBOSE_LOG_Q in self.verbose:
            printf (self.q_output_file, f'switching to delta mode. ins cnt since last full ad={self.ins_cnt_since_last_full_ad}. advertising ad_size={self.delta_ad_size}\n')
        if MyConfig.VERBOSE_LOG_MR in self.verbose: 
            printf (self.mr_output_file, f'switching to delta mode. ins cnt since last full ad={self.ins_cnt_since_last_full_ad}. advertising ad_size={self.delta_ad_size}\n')
        self.in_delta_mode                 = True
        self.ins_cnt_since_last_full_ad    = 0
        self.total_ad_size_in_this_period  = 0
        self.overall_ad_size              += self.delta_ad_size 
        self.num_of_advertisements        += 1
        self.gen_updated_sbf () # generate a new self.updated_sbf  
        self.stale_indicator               = self.updated_sbf

    def advertise_ind_full_mode_salsa_dep (self, called_by_str):
        
        """
        Advertise an indicator while in the "full indicator" mode, when the alg' used is "salsa_dep".
        - Write to log files, if requested by the self.verbose.
        - If required, scale the indicator. We assume that only SBF (Simple Bloom Filter) can scale. Counting Bloom Filter doesnn't scale. 
        - Assign self.stale_indicator to the list of current cached items. 
          At this very moment self.stale_indicator will be fresh, but from now and on, until the next advertisement, it will gradually become stale again.
        - Later, if needed, analyzes the number of set bits in the self.stale_indicator.
        - Update counters.
        
        """
        if MyConfig.VERBOSE_LOG_MR in self.verbose: 
            printf (self.mr_output_file, 'advertising full. ins_cnt={}. called by {}\n' .format (self.ins_cnt_since_last_full_ad, called_by_str))                     

        if self.ins_cnt_in_this_period >= self.re_init_mr0_param * self.min_uInterval: 

            self.mr0 = [min (self.mr0[num_of_pos_inds], self.initial_mr0) for num_of_pos_inds in range(self.num_of_DSs)]
            self.ins_cnt_in_this_period = 0 
            if MyConfig.VERBOSE_LOG_MR in self.verbose:
                printf (self.mr_output_file, f'RE-INIT MR0. mr0={self.mr0}\n')
        if self.init_mr1_after_each_ad and not(self.in_delta_mode):
            self.fp_cnt, self.reg_accs_cnt = 0,0
            self.mr1 = self.initial_mr1 
        if self.init_mr0_after_each_ad and not(self.in_delta_mode):
            # self.tn_cnt, self.spec_accs_cnt = 0,0
            self.mr0 = [min (self.mr0[num_of_pos_inds], self.initial_mr0) for num_of_pos_inds in range(self.num_of_DSs)]
        
        if self.scale_ind_full_factor!=1: # consider scaling the indicator and the uInterval
            scale_ind_by = 1
            if (called_by_str=='mr0'):
                scale_ind_by = max(1/self.scale_ind_factor, self.min_bpe/self.bpe) 
            elif (called_by_str=='mr1'): # too many FPs --> enlarge the indicator
                scale_ind_by = min(self.scale_ind_factor, self.max_bpe/self.bpe)
            if scale_ind_by!=1: # need to scale the ind'
                self.scale_ind_full_mode(factor=scale_ind_by)
                if MyConfig.VERBOSE_LOG_MR in self.verbose: 
                    printf (self.mr_output_file, 'After scaling ind: bpe={:.1f}, min_uInterval={:.0f}, max_uInterval={:.0f}\n' .format (self.bpe, self.min_uInterval, self.min_uInterval*self.uInterval_factor))

        self.stale_indicator         = self.genNewSBF () # Assume here that we don't use CountingBloomFilter
        self.num_of_advertisements  += 1
        self.num_of_full_ads        += 1
        self.overall_ad_size        += self.ind_size
        self.fn_cnt = self.spec_accs_cnt = [0]*self.num_of_DSs

    
    def advertise_ind_full_mode (self, called_by_str):
        
        """
        Advertise an indicator while in the "full indicator" mode.
        - Write to log files, if requested by the self.verbose.
        - If required, scale the indicator. We assume that only SBF (Simple Bloom Filter) can scale. Counting Bloom Filter doesnn't scale. 
        - Assign self.stale_indicator to the list of current cached items. 
          At this very moment self.stale_indicator will be fresh, but from now and on, until the next advertisement, it will gradually become stale again.
        - Later, if needed, analyzes the number of set bits in the self.stale_indicator.
        - Update counters.
        
        """
        if not (self.assume_ind_DSs): # salsa_dep
            return self.advertise_ind_full_mode_salsa_dep(called_by_str)

        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'advertising full ind. ins_cnt={}. called by {}\n' .format (self.ins_cnt_since_last_full_ad, called_by_str))                     
        if MyConfig.VERBOSE_LOG_MR in self.verbose: 
            printf (self.mr_output_file, 'advertising full. ins_cnt={}. called by {}\n' .format (self.ins_cnt_since_last_full_ad, called_by_str))                     

        if self.use_CountingBloomFilter: # update the stale indicator also for the case of not (consider_delta_updates)
            self.stale_indicator = self.updated_indicator.gen_SimpleBloomFilter () # Extract a fresh SBF from the updated (CBF) indicator
        
        if self.analyse_ind_deltas: # Do we need to estimate fpr, fnr by analyzing the diff between the stale and updated indicators? 
            B1_st                                   = sum (self.stale_indicator.array)    # Num of bits set in the updated indicator
            self.fpr                                = pow ( B1_st / self.ind_size, self.num_of_hashes)
            self.fnr                                = 0 # Immediately after sending an update, the expected fnr is 0
        
        if self.collect_mr_stat:
            if self.ins_cnt_in_this_period >= self.re_init_mr0_param * self.min_uInterval: 
                self.tn_cnt, self.spec_accs_cnt = 0,0
                self.ins_cnt_in_this_period = 0 
                self.mr0 = min (self.mr0, self.initial_mr0)
                if MyConfig.VERBOSE_LOG_MR in self.verbose:
                    printf (self.mr_output_file, 'RE-INIT MR0. mr0={:.3f}\n' .format (self.mr0))
            if self.init_mr1_after_each_ad and not(self.in_delta_mode):
                self.fp_cnt, self.reg_accs_cnt = 0,0
                self.mr1 = self.initial_mr1 
            if self.init_mr0_after_each_ad and not(self.in_delta_mode):
                self.tn_cnt, self.spec_accs_cnt = 0,0
                self.mr0 = min (self.mr0, self.initial_mr0)
        
        if self.scale_ind_full_factor!=1: # consider scaling the indicator and the uInterval
            scale_ind_by = 1
            if (called_by_str=='mr0'):
                scale_ind_by = max(1/self.scale_ind_factor, self.min_bpe/self.bpe) 
            elif (called_by_str=='mr1'): # too many FPs --> enlarge the indicator
                scale_ind_by = min(self.scale_ind_factor, self.max_bpe/self.bpe)
            if scale_ind_by!=1: # need to scale the ind'
                self.scale_ind_full_mode(factor=scale_ind_by)
                if MyConfig.VERBOSE_LOG_MR in self.verbose: 
                    printf (self.mr_output_file, 'After scaling ind: bpe={:.1f}, min_uInterval={:.0f}, max_uInterval={:.0f}\n' .format (self.bpe, self.min_uInterval, self.min_uInterval*self.uInterval_factor))

        if not (self.use_CountingBloomFilter):
            self.stale_indicator = self.genNewSBF ()

        self.num_of_advertisements  += 1
        self.num_of_full_ads        += 1
        self.overall_ad_size        += self.ind_size

    def scale_ind_delta_mode (self):
        """
        Scale the indicator (if needed) while in "delta" mode.
        Update stat, and consider reverting to full_indicator mode, if needed.
        """
        curIndSize_lg_curIndSize    = self.ind_size * np.log2 (self.ind_size)
        num_insertions_per_period   = self.delta_mode_period_param * self.min_uInterval
        cur_bw_of_delta_ads_per_ins = self.ins_cnt_since_last_full_ad # self.total_ad_size_in_this_period / num_insertions_per_period 
        estimated_bw_of_cadnidate   = [cur_bw_of_delta_ads_per_ins * self.potential_indSize_lg_indSize[i]/curIndSize_lg_curIndSize + self.bw_budget/self.delta_mode_period_param  for i in range(len(self.potential_indSize))]
        if all([item > self.bw_budget for item in estimated_bw_of_cadnidate]): # Cannot satisfy the BW constraint using delta mode 
            self.min_uInterval      = int (self.ind_size / self.bw_budget) 
            self.in_delta_mode      = False

            if MyConfig.VERBOSE_LOG_MR in self.verbose: 
                printf (self.mr_output_file, 'Switching back to full mode. indSize={:.0f}, estimated_bw_of_cadnidate[0]={:.0f}\n' .format 
                        (self.ind_size, estimated_bw_of_cadnidate[0]))
            return         
        diffs_from_bw_budget        = [abs (item - self.bw_budget) for item in estimated_bw_of_cadnidate]
        val, idx                    = min((val, idx) for (idx, val) in enumerate(diffs_from_bw_budget))
         
        new_ind_size                = self.potential_indSize[idx]
        if new_ind_size!=self.ind_size: 
            self.ind_size               = new_ind_size
            self.bpe                    = int (self.ind_size / self.DS_size)
            self.num_of_hashes          = MyConfig.get_optimal_num_of_hashes (self.bpe)
            if MyConfig.VERBOSE_LOG_MR in self.verbose: 
                printf (self.mr_output_file, 'After scaling in delta mode: bpe={:.1f}, \n' .format (self.bpe))
                   
    def report_mr (self): 
        """
        report the status of the various counters and estimators. Used for logging and debugging.
        """
        printf (self.mr_output_file, f'ins cnt since last full ad={self.ins_cnt_since_last_full_ad}, tn cnt={self.tn_cnt}, spec accs cnt={self.spec_accs_cnt}, mr0={self.mr0}, ')
        printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.ID, self.fp_cnt, self.reg_accs_cnt, self.mr1))
    
    def update_mr0(self):
        """
        update mr0 (the miss-probability in case of a negative indication), using an exponential moving average.
        If the updated value of mr0 justifies it, advertising an indicator. 
        """
        self.mr0 = self.EWMA_alpha_mr0 * float(self.tn_cnt) / float (self.mr0_ewma_window_size) + (1 - self.EWMA_alpha_mr0) * self.mr0
        
        if MyConfig.VERBOSE_DEBUG in self.verbose and self.mr0>0.999:
            print (f'Note: mr0={self.mr0} at DS{self.ID}') 
            
        # self.updated_mr0 = True 
        if MyConfig.VERBOSE_LOG_MR in self.verbose: 
            printf (self.mr_output_file, f'in update mr0: req_cnt={self.req_cnt}, ins cnt since last full ad={self.ins_cnt_since_last_full_ad}, tn cnt={self.tn_cnt}, spec accs cnt={self.spec_accs_cnt}, mr0={self.mr0}, tn_by_pos_ind_cnt={self.tn_cnt}, spec_accs_by_pos_ind_cnt={self.spec_accs_cnt}\n') 
            
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'in update mr0: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, spec_accs_cnt={}, reg_accs_cnt={}, ins_cnt={}\n' 
                    .format (self.pr_of_pos_ind_estimation, self.mr0, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0), self.mr1, self.pr_of_pos_ind_estimation*self.mr1, self.spec_accs_cnt, self.reg_accs_cnt, self.ins_cnt_since_last_full_ad)) 
        self.tn_cnt = int(0)
        
    def should_advertise_by_mr0 (self):
        """
        Check whether it's required to advertise, based on:
        - the level of mr0 (the miss-probability in case of a negative indication), and 
        - the level of mult0 (mr0, times the prob' of a negative indication).
        Returns True if advertised.
        """
        if (self.ins_cnt_since_last_full_ad >= self.min_uInterval):
            if (self.hit_ratio_based_uInterval):
                if ((self.num_of_advertisements>0) and 
                    (1-self.pr_of_pos_ind_estimation)*(1-self.mr0) > self.non_comp_miss_th):
                    return True
            else:
                if self.assume_ind_DSs: 
                    if self.mr0 < self.mr0_ad_th: 
                        return True
                else: #salsa_dep
                    if any ([(self.mr0[num_of_pos_inds] < self.mr0_ad_th) for num_of_pos_inds in range (self.num_of_DSs)]):
                        return True
        return False
     
    def update_mr1(self):
        """
        update the miss-probability in case of a positive indication, using an exponential moving average.
        """
        self.mr1 = self.EWMA_alpha_mr1 * float(self.fp_cnt) / float (self.mr1_ewma_window_size) + (1 - self.EWMA_alpha_mr1) * self.mr1 
        # self.updated_mr1 = True 
        if MyConfig.VERBOSE_LOG_MR in self.verbose: 
            printf (self.mr_output_file, 'in update mr1: req_cnt={}, fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.req_cnt, self.fp_cnt, self.reg_accs_cnt, self.mr1))
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'in update mr1: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, spec_accs_cnt={}, reg_accs_cnt={}, ins_cnt={}\n' 
                    .format (self.pr_of_pos_ind_estimation, self.mr0, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0), self.mr1, self.pr_of_pos_ind_estimation*self.mr1, self.spec_accs_cnt, self.reg_accs_cnt, self.ins_cnt_since_last_full_ad)) 
        self.fp_cnt = int(0)
        
    def should_advertise_by_mr1 (self):
        """
        Check whether it's required to advertise, based on:
        - the level of mr1 (the miss-probability in case of a positive indication), and 
        - the level of mult0 (mr1, times the prob' of a positive indication).
        Returns True if advertised.
        """
        if (self.ins_cnt_since_last_full_ad >= self.min_uInterval):
            if (self.hit_ratio_based_uInterval):
                if ((self.num_of_advertisements>0) and 
                     self.pr_of_pos_ind_estimation * self.mr1 > self.non_comp_accs_th):
                    return True
            else:           
                if self.mr1 > self.mr1_ad_th: 
                    return True
        return False
        
    def print_cache(self, head = 5):
        """
        test to see if key is in the cache
        """
        for i in itertools.islice(self.cache.dli(),head):
            print (i.key)
            
    def gen_updated_sbf (self):
        """
        generate an updated Simple Bloom Filter, that lists the items currenlty cahched.
        """
        if self.use_CountingBloomFilter: # extract the SBF from the updated CBF
            self.updated_sbf = self.updated_indicator.gen_SimpleBloomFilter ()
        else: # Generate a new SBF
            self.updated_sbf = self.genNewSBF () 
        
    
    def estimate_fnr_fpr_by_analysis (self, key=None):
        """
        Estimates the fnr and fpr, based on the diffs between the updated and the stale indicators. 
         (see the paper: "False Rate Analysis of Bloom Filter Replicas in Distributed Systems").
        The new values are written to self.fnr_fpr, where self.fnr_fpr[0] is the fnr, and self.fnr_fpr[1] is the fpr
        The optional input key is used only for debug.
        """
        self.gen_updated_sbf()
        Delta1      = sum (np.bitwise_and (self.updated_sbf.array, ~self.stale_indicator.array)) # # of bits that are set in the updated array, and reset in the stale array.
        B1_up       = sum (self.updated_sbf.array)             # Num of bits set in the updated indicator
        B1_st       = sum (self.stale_indicator.array)    # Num of bits set in the stale indicator
        self.fnr    = 1 - pow ( (B1_up-Delta1) / B1_up, self.num_of_hashes)
        self.fpr    = pow ( B1_st / self.ind_size, self.num_of_hashes)
        self.ins_since_last_fpr_fnr_estimation  = 0