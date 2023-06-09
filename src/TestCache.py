"""
Test the LRU cache  
"""

import numpy as np
import mod_pylru, itertools, copy
import MyConfig 
from printf import printf

class TestCache (object):
    
    def __init__ (self, cache_size):
        self.cache_size = cache_size
        self.cache      = mod_pylru.lrucache(self.cache_size) # LRU cache. for documentation, see: https://pypi.org/project/pylru/
        self.indicator  = []

    def access (key):
        """
        - Accesses a key in the cache.
        """
        hit = (key in self.cache)          
        if hit: 
            self.cache[key] #Touch the element, so as to update the LRU mechanism
    
    def cache_is_full (self):
        return self.cache.currSize()==self.cache_size
        
    def insert(self, key, req_cnt = -1):
        """
        - Inserts a key to the cache. 
        """
        if self.cache_is_full(): 
            self.indicator.remove(self.cache.get_tail())
        self.cache[key] = key
        self.indicator.append (key)
    
    def print_cache (self):
        """
        print the cache content, and the indicator
        The function merely checks for each item in the universe (set of possible keys) is it's in the cahce, and if so - prints it.
        The func' assumes that the universe (possible keys) is small.
        """
        cache_content = []
        found_items_cntr = 0
        universe = range (10)
        for key in universe:
            if key in self.cache:
                cache_content.append (key)
                found_items_cntr += 1
                if found_items_cntr==self.cache_size:
                    break
        print ('cahce content={}' .format (cache_content))
        print ('indicator content={}' .format (self.indicator))
    
myTestCache = TestCache (cache_size=2)
myTestCache.insert (1)
myTestCache.print_cache()
myTestCache.insert (2)
myTestCache.print_cache()
myTestCache.insert (3)
myTestCache.print_cache()


