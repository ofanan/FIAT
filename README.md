## False-Indications Aware Tactics (FIAT)

This project provides tools to simulate access strategies and cache-content advertisement schemes for distributed caching. 
The simulator considers a user who is equipped by several caches, and receives from them periodical advertisements about the cached content. These advertisements use space-efficient approximated data structures (aka indicators) that are not totally accurate. The user selects which caches to access, to obtain the requested datum in the lowest price and maximum certainty possible.
Each cache independently runs a content-advertisement algorithm, to decide when to advertise a fresh indicator.
For details about the problem and the algorithms used, please refer to the following papers:

[1] I. Cohen, Gil Einziger, R. Friedman, and G. Scalosub, [Access Strategies for Network Caching](https://www.researchgate.net/profile/Itamar-Cohen-2/publication/346732877_Access_Strategies_for_Network_Caching/links/5fd27eeea6fdcc697bf6f924/Access-Strategies-for-Network-Caching.pdf), IEEE Transactions on Networking, Vol. 29(2), 2021, pp.609-622.
 
[2] I. Cohen, Gil Einziger, and G. Scalosub, [False Negative Awareness in Indicator-based Caching Systems](https://www.researchgate.net/publication/361178366_False_Negative_Awareness_in_Indicator-Based_Caching_Systems), IEEE Transactions on Networking, 2022, pp. 46-56.

[3] I. Cohen, [Self-Adjusting Cache Advertisement and Selection](https://www.researchgate.net/profile/Itamar-Cohen-2/publication/370398278_Self-Adjusting_Cache_Advertisement_and_Selection/links/645b3d4a6090c43d0f5e7c7c/Self-Adjusting-Cache-Advertisement-and-Selection.pdf), ACM International Conference on Systems and Storage. 2023.

The source files are described below. More detailed documentation is found within the source files.

# Directories
All source files are written in Python, and found in ./src.

The result files are written to ./res.

# source files

##### runner.py #
Runs a simulation, looping over all requested values of parameters (miss penalty, cache sizes, number of caches etc.).

##### DistCacheSimulator.py # 
A simulator that accepts system parameters (trace, number and size of caches, algorithm to run etc.); runs a simulation; and outputs the results to file.

##### client.py
Implements the client-side cache-selection algorithms.

##### DataStore.py
The class for a DataStore (cache). The cache stores items using the LRU policy.
It also implements the cache-side algorithm for estimating FPR (false-positive ratio) and FNR (false-negative ratio) and the exclusion probabilities. 
The cache itself is implemented in the file mod_pylru.py.

###### mod_pylru.py
Implementation of an LRU cache. Source code is taken from:
Copyright (C) Jay Hutchinson
https://github.com/jlhutch/pylru

##### SimpleBloomFilter.py, CountingBloomFilter.py, 
A Simple and a Counting Bloom filter. To study more about Bloom filters, consider the following links: [1](http://www.maxburstein.com/blog/creating-a-simple-bloom-filter), [2](https://hur.st/bloomfilter), [3](http://pages.cs.wisc.edu/~cao/papers/summary-cache/node8.html), [4](https://www.eecs.harvard.edu/~michaelm/postscripts/im2005b.pdf).

##### Wiki_parser.py, IBM_parser.py, Twitter_parser.py
Parse traces and output a .csv file, which includes a row with hashes of the keys in the trace. 

###### gen_graph.py
generates the OVH network which exemplifies a commercial CDN (Content Delivery Network), and saves it on a .csv file.

###### gen_cost_hist.py
Generates a histogram showing the cache access costs for the OVH network

##### MyConfig.py
This file contains several accessory functions, used throughout the project, e.g. for generating the string describing the settings of the simulation, and generate the list of requests from the trace.

##### node.py
An accessory function for the PGM access strategy algorithm, described in [1]. 
The function merges 2 input nodes.
Inputs: 2 nodes to merge, H and L, and r = log(beta)
Output: res_node - the result node, res_node.

##### candidate.py
A candidate sol' for the DSS (Data-Store-Selection) prob' (aka the "Cache-Selection" problem), consists of a list of DSs, theirs aggregate (mult' of) miss rate, and aggregate (sum of) accs cost

##### printf.py
An accessory function for format-printing to a file.

##### check_fpr_fnr_formulas.py
A script to compare the fpr, fnr, calculated by either the paper [2], or by an an older paper, which uses different model:
[3] Y. Zhu and H. Jiang, “False rate analysis of bloom filter replicas in distributed systems”, in ICPP, 2006, pp. 255–262.

##### Res_file_parser.py
Receives files that are the results of simulations, and generates plots.

##### tictoc.py
An accessory file for run-time measurements.

##### trace_checker.py
Checks the hit rate in a given cache trace.

##### MyConfig.py
Accessory file containing global parameters and accessory functions.
