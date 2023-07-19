// format: e.g., scarab.C10K.bpe14.1000Kreq.3DSs.Kloc1.M30.B0.U1000.SALSA.m0_0.1_m1_0.01, where:
// scarab=trace file. 10K=the capacity of each cache. 14=num of Bits Per Element in the indicator.
// 1000Kreq - num of requests in the trace is 1000K.
// 3DSs- num of datastores (Caches) is 3. 
// Kloc1- each element is mapped to a single location (cache).
// M30 - missp is 30
// B0 - desired BW - for simulation with bandwidth const currently unused.
// U1000 - used fixed uInterval of 1000 insertions.
//     alternatively, the "U" field can say:
//     Ux-Uy, where x,y are min_u_uInterlva, max_num_uInterval.
// SALSA is the algorithm (aka "mode") used.
// m0_0.1_m1_0.01 informs the values of "mult0", "mult1" that are now 0.1 and 0.01, resp.

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA2.mr0th0.88.mr1th0.01.uIntFact999999.minFU10.alpha00.85.alpha10.25.per_param1 | service_cost = 9.88 | bw = 14.05 | hit_ratio = 0.72, 
// tot_access_cost = 8553089, non_comp_miss_cnt = 877187, comp_miss_cnt = 813235
// estimation window = 40
// spec accs cost = 109360, num of spec hits = 538
// num of ads per DS=[547, 475, 498].  avg update interval = 11842.1 req
// num of full ind ad=[507, 435, 458], num of periods in delta mode=[1, 1, 1]

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA2.mr0th0.88.mr1th0.01.uIntFact999999.minFU10.alpha00.85.alpha10.25.per_param2 | service_cost = 9.69 | bw = 14.55 | hit_ratio = 0.72, 
// tot_access_cost = 8638529, non_comp_miss_cnt = 837112, comp_miss_cnt = 813235
// estimation window = 40
// spec accs cost = 103920, num of spec hits = 555
// num of ads per DS=[673, 606, 649].  avg update interval = 9336.1 req
// num of full ind ad=[470, 392, 441], num of periods in delta mode=[1, 1, 1]

