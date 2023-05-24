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

    def __init__(self, 
         ID,                             # datastore ID
         size                   = 1000,  # number of elements that can be stored in the datastore
         bpe                    = 14,    # Bits Per Element: number of cntrs in the CBF per a cached element (commonly referred to as m/n)
         EWMA_alpha             = 0.85,  # sliding window parameter for miss-rate estimation
         mr1_ewma_window_size   = 100,   # Number of regular accesses between new performing new estimation of mr1 (prob' of a miss given a pos' ind'). 
         max_fnr = 0.03,max_fpr = 0.03,  # maximum allowed (estimated) fpr, fnr. When the estimated fnr is above max_fnr, or the estimated fpr is above mx_fpr, the DS sends an update.
                                         # fpr: False Positive Ratio, fnr: False Negative Ratio).
                                         # currently max_fnr, max_fpr are usually unused, 
         num_of_insertions_between_estimations = np.uint8 (50), # num of insertions between subsequent operations of estimating the fpr, fnr.
                                                                # Each time a new indicator is published, the updated indicator contains a fresh estimation, and a counter is reset. 
                                                                # Then, each time the counter reaches num_of_insertions_between_estimations. a new fpr and fnr estimation is published, and the counter is reset.
         verbose                    = [],# what output will be written. See macros in MyConfig.py 
         min_uInterval              = 1, # min num of insertions of new items into the cache before advertising again
         uInterval_factor           = 1, 
         send_fpr_fnr_updates       = True, # When True, "send" (actually, merely collect) analysis of fpr, fnr, based on the # of bits set/reset in the stale and updated indicators.   
         collect_mr_stat            = True,  
         analyse_ind_deltas         = True, # analyze the differences between the stale (last advertised) and the current, updated, indicator
         designed_mr1               = 0.001, # inherent mr1, stemmed from the inherent FP of a Bloom filter.
         use_EWMA                   = False, # when true, collect historical statistics using an Exp' Weighted Moving Avg.
         initial_mr0                = 0.85, # initial value of mr0, before we have first statistics of the indications after the lastly advertised indicator.  
         non_comp_miss_th           = 0.15, # if (!use_fixed_uInterval) AND hit_ratio_based_uInterval, advertise an indicator each time (1-q)*(1-mr0) > non_comp_miss_th.
         non_comp_accs_th           = 0.02, # if (!use_fixed_uInterval) AND hit_ratio_based_uInterval, advertise an indicator each time q*mr1 > non_comp_accs_th.
         mr0_ad_th                  = 0.9,
         mr1_ad_th                  = 0.01,
         mr_output_file             = None, # When this input isn't known, log data about the mr to this file
         use_indicator              = True, # when True, generate and maintain an indicator (BF).
         use_CountingBloomFilter    = False, # When True, keep both an "updated" CBF, and a "stale" simple BF, that is generated upon each advertisement. When False, use only a single, simple Bloom filter, that will be generated upon each advertisement (thus becoming stale).
         hit_ratio_based_uInterval  = False, # when True, consider the hit ratio when deciding whether to advertise a new indicator.
         settings_str               = "",    # a string that details the parameters of the current run. Used when writing to output files, as defined by verbose.
         scale_ind_factor           = 1,     # multiplicative factor for the indicator size. To be used by modes that scale it ('salsa3').
         consider_delta_updates     = False, # when True, calculate the "deltas", namely, number of indicator's bits flipped since the last advertisement.  
         init_mr0_after_each_ad     = False,
         init_mr1_after_each_ad     = False,
         use_fixed_uInterval        = True,
         ):
        """
        Return a DataStore object. 
            For the DataStore's see documentation within the __init__ function.
        """
        self.ID                      = ID
        self.verbose                 = verbose 
        self.cache_size              = size
        self.cache                   = mod_pylru.lrucache(self.cache_size) # LRU cache. for documentation, see: https://pypi.org/project/pylru/
        self.settings_str            = settings_str
        self.use_fixed_uInterval     = use_fixed_uInterval
        if (MyConfig.VERBOSE_DEBUG in self.verbose):
            self.debug_file = open ('../res/fna_{}.txt' .format (self.settings_str), "w")
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            self.q_output_file = open ('../res/q{}_{}.txt' .format(self.ID, self.settings_str), "w") 
        self.collect_mr_stat         = collect_mr_stat
        self.use_indicator           = use_indicator # used e.g. for Opt, that merely checks whether the requested item is indeed cached
        if not(self.use_indicator): # if no indicator is used, no need for all the further fields
            return

        # inializations related to the indicator, statistics, and advertising mechanism
        self.init_mr0_after_each_ad  = init_mr0_after_each_ad
        self.init_mr1_after_each_ad  = init_mr1_after_each_ad
        self.consider_delta_updates  = consider_delta_updates
        self.use_fixed_uInterval     = use_fixed_uInterval 
        # self.updated_mr0 = False # indicates whether mr0 wasn't updated since the last advertisement 
        # self.updated_mr1 = False # indicates whether mr1 wasn't updated since the last advertisement
        self.in_delta_mode           = False
        self.scale_ind_factor        = scale_ind_factor # multiplicative factor for the indicator size. To be used by modes that scale it ('salsa3').
        self.overall_ad_size         = 0
        self.total_ad_size_in_this_period = 0 # the ind' may be scaled, so need to measure the overall ind' size
        self.min_bpe                 = 5
        self.max_bpe                 = 15
        self.mr_output_file          = mr_output_file
        self.bpe                     = bpe
        self.ind_size                = self.bpe * self.cache_size
        self.lg_ind_size             = np.log2 (self.ind_size) 
        self.num_of_hashes           = MyConfig.get_optimal_num_of_hashes (self.bpe)
        self.use_CountingBloomFilter = use_CountingBloomFilter
        if use_CountingBloomFilter: 
            self.updated_indicator   = CBF.CountingBloomFilter (size = self.ind_size, num_of_hashes = self.num_of_hashes)
            self.stale_indicator     = self.updated_indicator.gen_SimpleBloomFilter ()
            if (self.scale_ind_factor!=1):
                MyConfig.error ('Sorry. Scaling an indicator is not supported for CountingBloomFilter')
        else:
            self.stale_indicator     = SBF.SimpleBloomFilter (size = self.ind_size, num_of_hashes = self.num_of_hashes)
        self.EWMA_alpha              = EWMA_alpha # "alpha" parameter of the Exponential Weighted Moving Avg estimation of mr0 and mr1
        self.initial_mr0             = initial_mr0
        self.mr0_cur                 = self.initial_mr0
        self.mr1_cur                 = 0
        self.mr1_ewma_window_size    = mr1_ewma_window_size
        self.mr0_ewma_window_size    = mr1_ewma_window_size
        self.use_EWMA                = use_EWMA # If true, use Exp' Weighted Moving Avg. Else, use flat history along the whole trace
        if not (self.use_fixed_uInterval):
            self.hit_ratio_based_uInterval = hit_ratio_based_uInterval
            if (self.hit_ratio_based_uInterval):
                self.non_comp_miss_th = non_comp_miss_th
                self.non_comp_accs_th = non_comp_accs_th
            else:
                self.mr0_ad_th, self.mr1_ad_th = mr0_ad_th, mr1_ad_th 
        self.fp_events_cnt           = int(0) # Number of False Positive events that happened in the current estimation window
        self.tn_events_cnt           = int(0) # Number of False Positive events that happened in the current estimation window
        self.reg_accs_cnt            = 0
        self.spec_accs_cnt           = 0
        self.max_fnr                 = max_fnr
        self.max_fpr                 = max_fpr
        self.designed_fpr            = MyConfig.calc_designed_fpr (self.cache_size, self.ind_size, self.num_of_hashes)
        self.initial_mr1             = self.designed_fpr
        self.send_fpr_fnr_updates    = send_fpr_fnr_updates # when true, need to periodically compare the stale BF to the updated BF, and estimate the fpr, fnr accordingly
        self.analyse_ind_deltas      = analyse_ind_deltas
        self.delta_th                = self.ind_size / self.lg_ind_size # threshold for number of flipped bits in the BF; below this th, it's cheaper to send only the "delta" (indices of flipped bits), rather than the full ind'         
        self.update_bw               = 0
        self.num_of_advertisements   = 0
        self.ins_cnt_in_this_period  = 0 # cnt of insertions since the last advertisement of fresh indicator
        self.ins_cnt_in_this_reinit_mr0_period = 0 # cnt of insertions since the last advertisement of fresh indicator
        self.num_of_fpr_fnr_updates  = int (0) 
        self.min_uInterval           = min_uInterval
        self.min_feasible_uInterval  = 10
        self.uInterval_factor        = uInterval_factor
        self.period                  = 10 * self.min_uInterval  
        self.bw_budget               = self.ind_size / self.min_uInterval # [bits / insertion]
        if MyConfig.VERBOSE_LOG_Q in self.verbose:
            printf (self.q_output_file, 'bw budget={:.2f}\n' .format (self.bw_budget)) 
 
        self.use_only_updated_ind    = True if (self.uInterval_factor * self.min_uInterval == 1) else False
        if (self.send_fpr_fnr_updates):
            self.fnr                 = 0 # Initially, there are no false indications
            self.fpr                 = 0 # Initially, there are no false indications
        
        self.num_of_insertions_between_estimations  = num_of_insertions_between_estimations
        self.ins_since_last_fpr_fnr_estimation      = int (0)
        
        if self.consider_delta_updates and self.scale_ind_factor!=1: # if needed, pre-compute values for Lambert function (scaling of the ind' at delta mode)
            bpe                         = self.min_bpe
            self.potential_indSize      = []
            while bpe <= self.max_bpe:
                self.potential_indSize.append (int (bpe * self.cache_size))
                bpe *= self.scale_ind_factor
            self.potential_indSize.append (self.max_bpe*self.cache_size)
            self.potential_indSize.append (self.bpe*self.cache_size)
            self.potential_indSize.sort()
            self.potential_indSize_lg_indSize = np.array ([item*np.log2(item) for item in self.potential_indSize])
            
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
        self.cache[key] = key
        if not (self.use_indicator):
            return
        
        self.ins_cnt_in_this_period += 1
        self.ins_cnt_in_this_reinit_mr0_period += 1
        if self.use_CountingBloomFilter:
            if (self.cache.currSize() == self.cache.size()): # if cache is full, remove the victim item from the CBF
                self.updated_indicator.remove(self.cache.get_tail())
            self.updated_indicator.add(key)
        if (self.send_fpr_fnr_updates):
            self.ins_since_last_fpr_fnr_estimation += 1
            if (self.ins_since_last_fpr_fnr_estimation == self.num_of_insertions_between_estimations):
                self.estimate_fnr_fpr_by_analysis (req_cnt) # Update the estimates of fpr and fnr, and check if it's time to send an update
                self.num_of_fpr_fnr_updates           += 1
                self.ins_since_last_fpr_fnr_estimation = 0

        if self.use_fixed_uInterval:
            if self.ins_cnt_in_this_period >= self.min_uInterval:
                self.advertise_ind_full_mode(called_by_str='fixed uInterval')
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
        
        if self.ins_cnt_in_this_period>=self.period: # time to consider scaling, or at least send a keep-alive full ind'

            if self.scale_ind_factor!=1:                                          
                self.scale_ind_delta_mode (bw_in_cur_interval=self.total_ad_size_in_this_period / self.ins_cnt_in_this_period)
            self.ins_cnt_in_this_period         = 0
            self.total_ad_size_in_this_period   = 0
            self.overall_ad_size               += self.ind_size # even if not scaled, need to advertise a full ind' once in a period.
            if self.use_CountingBloomFilter: # extract the SBF from the updated CBF
                self.stale_indicator            = self.updated_indicator.gen_SimpleBloomFilter ()
            else:
                self.stale_indicator            = self.genNewSBF ()
            if (MyConfig.VERBOSE_LOG_Q in self.verbose):
                printf (self.q_output_file, 'advertising delta. ins_cnt_in_this_period ={}\n' .format (self.ins_cnt_in_this_period))                     
            if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
                printf (self.q_output_file, 'advertising delta. ins_cnt_in_this_period={}\n' .format (self.ins_cnt_in_this_period))                     
            self.num_of_advertisements  += 1
            return # finished advertising an indicator
        
        if self.ins_cnt_in_this_period % self.min_feasible_uInterval == 0:

            if self.use_CountingBloomFilter: # extract the SBF from the updated CBF
                self.updated_sbf                     = self.updated_indicator.gen_SimpleBloomFilter ()
            else: # Generate a new SBF
                self.updated_sbf = self.genNewSBF () 
            ad_size                             = int (np.log2 (self.ind_size) * np.sum ([np.bitwise_xor (self.updated_sbf.array, self.stale_indicator.array)]))
            self.total_ad_size_in_this_period  += ad_size
            self.overall_ad_size               += ad_size                              
            self.stale_indicator                = self.updated_sbf 
            self.num_of_advertisements         += 1
            if MyConfig.VERBOSE_LOG_Q in self.verbose:
                printf (self.q_output_file, 'advertising delta. ind size={}, ad_size={}, ins_cnt_in_this_period={}, bw_in_cur_interval={:.1f}, \n' .format 
                        (self.ind_size, ad_size, self.ins_cnt_in_this_period, self.total_ad_size_in_this_period / self.ins_cnt_in_this_period)) 

    def handle_ind_full_mode (self):
        """
        Advertise an updated indicator, while in full mode:
        """
        if self.ins_cnt_in_this_period >= self.min_uInterval * self.uInterval_factor:
            if self.consider_delta_updates and self.delta_update_is_cheaper():
                self.advertise_switch_to_delta_update()
            else:
                self.advertise_ind_full_mode (called_by_str='max_uInterval')
                self.ins_cnt_in_this_period = 0 
            return
       
        # now we know that this is an alg' that dynamically-scales the uInterval, in Full mode 
        if (self.ins_cnt_in_this_period>=self.min_uInterval):
            if self.consider_delta_updates and self.delta_update_is_cheaper():
                self.advertise_switch_to_delta_update()
                return
            
            if self.should_advertise_by_mr0 (): 
                self.advertise_ind_full_mode (called_by_str='mr0')
                self.ins_cnt_in_this_period = 0
                return

            if self.consider_advertise_by_mr1 ():
                self.advertise_ind_full_mode (called_by_str='mr1')
                self.ins_cnt_in_this_period = 0
                return
       
    def delta_update_is_cheaper (self):
        """
        Check whether advertising a delta requires less bits than advertising a full ind.
        - Update the fields
            - self.delta_ad_size (size of the delta update).
            - self.updated_sbf (a Simple Bloom Filter, representing the currently-cached items).
        - Returns true iff advertising a delta requires less bits than advertising a full ind. 
        """
        if self.use_CountingBloomFilter: 
            self.updated_sbf = self.updated_indicator.gen_SimpleBloomFilter () # Extract a fresh SBF from the updated (CBF) indicator
        else: # Generate a new SBF
            self.updated_sbf = self.genNewSBF ()

        self.delta_ad_size = int (np.log2 (self.ind_size) * np.sum ([np.bitwise_xor (self.updated_sbf.array, self.stale_indicator.array)]))
        if MyConfig.VERBOSE_LOG_Q in self.verbose:
            printf (self.q_output_file, 'delta_ad_size={}, ind size={}\n' .format (self.delta_ad_size, self.ind_size)) 
        return self.delta_ad_size < self.ind_size
    
    def advertise_switch_to_delta_update (self):
        """
        Advertise a delta update after a period of full indicators:
        - Update relevant counters.
        - Assign self.stale_indicator <-- self.updated_sbf (update Simple Bloom Filter)  
        - If requested by self.verbose, print to log files.
        """
        self.in_delta_mode                 = True
        self.ins_cnt_in_this_period        = 0
        self.total_ad_size_in_this_period  = 0
        self.num_of_advertisements        += 1
        self.overall_ad_size              += self.delta_ad_size  
        if MyConfig.VERBOSE_LOG_Q in self.verbose:
            printf (self.q_output_file, 'switching to delta mode. advertising ad_size={}, ins_cnt={}\n' .format(self.delta_ad_size, self.ins_cnt_in_this_period))
        self.stale_indicator = self.updated_sbf  

    def advertise_ind_full_mode (self, called_by_str):
        
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'advertising. ins_cnt={}. called by {}\n' .format (self.ins_cnt_in_this_period, called_by_str))                     
        if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
            printf (self.q_output_file, 'advertising. ins_cnt={}. called by {}\n' .format (self.ins_cnt_in_this_period, called_by_str))                     

        if self.use_CountingBloomFilter: # update the stale indicator also for the case of not (consider_delta_updates)
            self.stale_indicator = self.updated_indicator.gen_SimpleBloomFilter () # Extract a fresh SBF from the updated (CBF) indicator
        else: # Generate a new SBF
            self.stale_indicator = self.genNewSBF ()
        
        if self.analyse_ind_deltas: # Do we need to estimate fpr, fnr by analyzing the diff between the stale and updated indicators? 
            B1_st                                   = sum (self.stale_indicator.array)    # Num of bits set in the updated indicator
            self.fpr                                = pow ( B1_st / self.ind_size, self.num_of_hashes)
            self.fnr                                = 0 # Immediately after sending an update, the expected fnr is 0
        
        if self.collect_mr_stat:
            if self.ins_cnt_in_this_reinit_mr0_period >= self.period: 
            #self.init_mr0_after_each_ad:
                self.tn_events_cnt, self.spec_accs_cnt = 0,0
                self.ins_cnt_in_this_reinit_mr0_period = 0 
                self.mr0_cur = min (self.mr0_cur, self.initial_mr0)
                if MyConfig.VERBOSE_LOG_Q in self.verbose:
                    printf (self.q_output_file, 'RE-INIT MR0. mr0={}\n' .format (self.mr0_cur))
            if self.init_mr1_after_each_ad and not(self.in_delta_mode):
                self.fp_events_cnt, self.reg_accs_cnt = 0,0
                self.mr1_cur = self.initial_mr1 
        
        if self.scale_ind_factor!=1: # consider scaling the indicator and the uInterval
            scale_ind_by = 1
            if (called_by_str=='mr0'):
                scale_ind_by = max(1/self.scale_ind_factor, self.min_bpe/self.bpe) 
            elif (called_by_str=='mr1'): # too many FPs --> enlarge the indicator
                scale_ind_by = min(self.scale_ind_factor, self.max_bpe/self.bpe)
            if scale_ind_by!=1: # need to scale the ind'
                self.scale_ind_full_mode(factor=scale_ind_by)
                if MyConfig.VERBOSE_LOG_Q in self.verbose: 
                    printf (self.q_output_file, 'After scaling ind: bpe={:.1f}, min_uInterval={:.0f}, max_uInterval={:.0f}\n' .format (self.bpe, self.min_uInterval, self.min_uInterval*self.uInterval_factor))
        self.num_of_advertisements += 1
        self.overall_ad_size       += self.ind_size

    def scale_ind_delta_mode (self, bw_in_cur_interval):
        """
        Scale the indicator (if needed) while in "delta" mode.
        Update stat, and consider reverting to full_indicator mode, if needed.
        """
        cur_IndSize                 = self.ind_size
        curIndSize_lg_curIndSize    = self.ind_size * np.log2 (self.ind_size)
        diffs_from_desiredRatio     = [abs (self.potential_indSize_lg_indSize[i]/curIndSize_lg_curIndSize - (self.bw_budget - self.potential_indSize[i])/ bw_in_cur_interval) for i in range(len(self.potential_indSize))]
        val, idx                    = min((val, idx) for (idx, val) in enumerate(diffs_from_desiredRatio))
        if idx==0 and bw_in_cur_interval * self.potential_indSize_lg_indSize[0]/curIndSize_lg_curIndSize > self.bw_budget:
            self.min_uInterval = int (self.ind_size / self.bw_budget) 
            self.in_delta_mode = False

            if MyConfig.VERBOSE_LOG_Q in self.verbose: 
                printf (self.q_output_file, 'Switching back to full mode. cur bw={}, indSize={}, curIndSize_lg_curIndSize={}, self.potential_indSize_lg_indSize[0]={}, \n' .format 
                        (bw_in_cur_interval, self.ind_size, curIndSize_lg_curIndSize, self.potential_indSize_lg_indSize[0]))        
         
         # scaled ind' size is the min' feasible val.             
        new_ind_size                = self.potential_indSize[idx]
        if new_ind_size!=self.ind_size: 
            self.ind_size               = new_ind_size
            self.bpe                    = int (self.ind_size / self.cache_size)
            self.num_of_hashes          = MyConfig.get_optimal_num_of_hashes (self.bpe)
            if MyConfig.VERBOSE_LOG_Q in self.verbose: 
                printf (self.q_output_file, 'After scaling in delta mode: bpe={:.1f}, \n' .format (self.bpe))
                   
    def update_mr0(self):
        """
        update mr0 (the miss-probability in case of a negative indication), using an exponential moving average.
        If the updated value of mr0 justifies it, advertising an indicator. 
        """
        self.mr0_cur = self.EWMA_alpha * float(self.tn_events_cnt) / float (self.mr0_ewma_window_size) + (1 - self.EWMA_alpha) * self.mr0_cur
        # self.updated_mr0 = True 
        if ((MyConfig.VERBOSE_LOG_MR in self.verbose) or (MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose)): 
            printf (self.mr_output_file, 'tn cnt={}, spec accs cnt={}, mr0={:.4f}\n' .format (self.tn_events_cnt, self.spec_accs_cnt, self.mr0_cur))
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'in update mr0: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, spec_accs_cnt={}, reg_accs_cnt={}, ins_cnt={}\n' 
                    .format (self.pr_of_pos_ind_estimation, self.mr0_cur, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur), self.mr1_cur, self.pr_of_pos_ind_estimation*self.mr1_cur, self.spec_accs_cnt, self.reg_accs_cnt, self.ins_cnt_in_this_period)) 
        self.tn_events_cnt = int(0)
        
    def should_advertise_by_mr0 (self):
        """
        Check whether it's required to advertise, based on:
        - the level of mr0 (the miss-probability in case of a negative indication), and 
        - the level of mult0 (mr0, times the prob' of a negative indication).
        Returns True if advertised.
        """
        if (self.ins_cnt_in_this_period >= self.min_uInterval):
            if (self.hit_ratio_based_uInterval):
                if ((self.num_of_advertisements>0) and 
                    (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur) > self.non_comp_miss_th):
                    return True
            else:
                if self.mr0_cur < self.mr0_ad_th: 
                    return True
        return False
     
    def update_mr1(self):
        """
        update the miss-probability in case of a positive indication, using an exponential moving average.
        """
        self.mr1_cur = self.EWMA_alpha * float(self.fp_events_cnt) / float (self.mr1_ewma_window_size) + (1 - self.EWMA_alpha) * self.mr1_cur 
        # self.updated_mr1 = True 
        if (MyConfig.VERBOSE_LOG_MR in self.verbose or MyConfig.VERBOSE_DETAILED_LOG_MR in self.verbose): 
            printf (self.mr_output_file, 'fp cnt={}, reg accs cnt={}, mr1={:.4f}\n' .format (self.fp_events_cnt, self.reg_accs_cnt, self.mr1_cur))
        if (MyConfig.VERBOSE_LOG_Q in self.verbose):
            printf (self.q_output_file, 'in update mr1: q={:.2f}, mr0={:.2f}, mult0={:.2f}, mr1={:.4f}, mult1={:.4f}, spec_accs_cnt={}, reg_accs_cnt={}, ins_cnt={}\n' 
                    .format (self.pr_of_pos_ind_estimation, self.mr0_cur, (1-self.pr_of_pos_ind_estimation)*(1-self.mr0_cur), self.mr1_cur, self.pr_of_pos_ind_estimation*self.mr1_cur, self.spec_accs_cnt, self.reg_accs_cnt, self.ins_cnt_in_this_period)) 
        self.fp_events_cnt = int(0)
        
    def consider_advertise_by_mr1 (self):
        """
        Check whether it's required to advertise, based on:
        - the level of mr1 (the miss-probability in case of a positive indication), and 
        - the level of mult0 (mr1, times the prob' of a positive indication).
        Returns True if advertised.
        """
        if (self.ins_cnt_in_this_period >= self.min_uInterval):
            if (self.hit_ratio_based_uInterval):
                if ((self.num_of_advertisements>0) and 
                     self.pr_of_pos_ind_estimation * self.mr1_cur > self.non_comp_accs_th):
                    return True
            else:           
                if self.mr1_cur > self.mr1_ad_th: 
                    return True
        return False
        
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
        self.updated_sbf = self.updated_indicator.gen_SimpleBloomFilter ()
        # Delta[0] will hold the # of bits that are reset in the updated array, and set in the stale array.
        # Delta[1] will hold the # of bits that are set in the updated array, and reset in the stale array.
        Delta       = [sum (np.bitwise_and (~self.updated_sbf.array, self.stale_indicator.array)), sum (np.bitwise_and (self.updated_sbf.array, ~self.stale_indicator.array))]
        B1_up       = sum (self.updated_sbf.array)             # Num of bits set in the updated indicator
        B1_st       = sum (self.stale_indicator.array)    # Num of bits set in the stale indicator
        self.fnr    = 1 - pow ( (B1_up-Delta[1]) / B1_up, self.num_of_hashes)
        self.fpr    = pow ( B1_st / self.ind_size, self.num_of_hashes)
        self.ins_since_last_fpr_fnr_estimation  = 0