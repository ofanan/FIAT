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

scarab.C10K.bpe14.100Kreq.3DSs.Kloc1.M100.B0.U1000.SALSA.m0_0.1_m1_0.01 | service_cost = 41.17 | bw = 103.60 | hit_ratio = 0.63, 
// tot_access_cost = 398704, non_comp_miss_cnt = 1253, comp_miss_cnt = 35931
// estimation window = 1000
// spec accs cost = 296020, num of spec hits = 10398
// num of ads per DS=[12, 12, 13].  avg update interval = 8108.1 req

