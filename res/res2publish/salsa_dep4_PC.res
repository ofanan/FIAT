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

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 42.91 | bw = 17.19 | hit_ratio = 0.86, 
// tot_access_cost = 13275294, non_comp_miss_cnt = 692, comp_miss_cnt = 813235
// ewma_window = 200
// spec accs cost = 2975003, num of spec hits = 10787
// num of ads per DS=[26917, 27113, 26966].  avg update interval = 222.2 req

Scarab.C4K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 14.79 | bw = 46.77 | hit_ratio = 0.56, 
// tot_access_cost = 5972580, non_comp_miss_cnt = 158806, comp_miss_cnt = 1614728
// ewma_window = 200
// spec accs cost = 1486342, num of spec hits = 17554
// num of ads per DS=[53829, 2757, 55766].  avg update interval = 106.8 req

Scarab.C4K.bpe14.4000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 125.84 | bw = 50.98 | hit_ratio = 0.59, 
// tot_access_cost = 9539479, non_comp_miss_cnt = 31404, comp_miss_cnt = 1614728
// ewma_window = 200
// spec accs cost = 4837275, num of spec hits = 41786
// num of ads per DS=[54582, 54408, 55254].  avg update interval = 73.1 req

F1.C4K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 21.82 | bw = 86.25 | hit_ratio = 0.31, 
// tot_access_cost = 2601526, non_comp_miss_cnt = 34979, comp_miss_cnt = 1696275
// ewma_window = 200
// spec accs cost = 1013516, num of spec hits = 5128
// num of ads per DS=[57465, 57644, 57709].  avg update interval = 43.4 req

F1.C4K.bpe14.2500Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 207.59 | bw = 86.34 | hit_ratio = 0.31, 
// tot_access_cost = 5163954, non_comp_miss_cnt = 16412, comp_miss_cnt = 1696275
// ewma_window = 200
// spec accs cost = 3582630, num of spec hits = 28940
// num of ads per DS=[56646, 56922, 57220].  avg update interval = 43.9 req

F2.C4K.bpe14.10000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 142.73 | bw = 41.48 | hit_ratio = 0.53, 
// tot_access_cost = 26366446, non_comp_miss_cnt = 65693, comp_miss_cnt = 4604026
// ewma_window = 200
// spec accs cost = 15935085, num of spec hits = 384479
// num of ads per DS=[3822, 3695, 156284].  avg update interval = 183.1 req

IBM1.C4K.bpe14.948Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 150.97 | bw = 60.80 | hit_ratio = 0.52, 
// tot_access_cost = 5195042, non_comp_miss_cnt = 3273, comp_miss_cnt = 456478
// ewma_window = 200
// spec accs cost = 4906860, num of spec hits = 354794
// num of ads per DS=[15102, 15117, 15200].  avg update interval = 62.6 req

F2.C4K.bpe14.10000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 15.38 | bw = 57.68 | hit_ratio = 0.54, 
// tot_access_cost = 14654606, non_comp_miss_cnt = 35594, comp_miss_cnt = 4604026
// ewma_window = 200
// spec accs cost = 3655595, num of spec hits = 4109
// num of ads per DS=[156535, 150221, 156458].  avg update interval = 64.8 req

IBM1.C4K.bpe14.948Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 20.97 | bw = 70.33 | hit_ratio = 0.4, 
// tot_access_cost = 2923293, non_comp_miss_cnt = 108835, comp_miss_cnt = 456478
// ewma_window = 200
// spec accs cost = 2637287, num of spec hits = 246912
// num of ads per DS=[15120, 15231, 25398].  avg update interval = 51.0 req

IBM7.C4K.bpe14.4006Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 49.24 | bw = 19.35 | hit_ratio = 0.85, 
// tot_access_cost = 13175292, non_comp_miss_cnt = 2269, comp_miss_cnt = 611301
// ewma_window = 200
// spec accs cost = 7123029, num of spec hits = 410863
// num of ads per DS=[20282, 20349, 20358].  avg update interval = 197.1 req

IBM7.C4K.bpe14.4006Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.18 | bw = 20.68 | hit_ratio = 0.84, 
// tot_access_cost = 9052437, non_comp_miss_cnt = 45382, comp_miss_cnt = 611301
// ewma_window = 200
// spec accs cost = 2577644, num of spec hits = 195415
// num of ads per DS=[20585, 21969, 22748].  avg update interval = 184.0 req

Twitter17.C4K.bpe14.14000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 74.22 | bw = 28.14 | hit_ratio = 0.76, 
// tot_access_cost = 36845600, non_comp_miss_cnt = 13954, comp_miss_cnt = 3326741
// ewma_window = 200
// spec accs cost = 15428044, num of spec hits = 166927
// num of ads per DS=[2820, 2838, 112091].  avg update interval = 356.7 req

Twitter17.C4K.bpe14.14000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.38 | bw = 28.33 | hit_ratio = 0.75, 
// tot_access_cost = 26484282, non_comp_miss_cnt = 167708, comp_miss_cnt = 3326741
// ewma_window = 200
// spec accs cost = 5218306, num of spec hits = 17432
// num of ads per DS=[2929, 112723, 2838].  avg update interval = 354.5 req

Twitter45.C4K.bpe14.2000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 272.86 | bw = 34.16 | hit_ratio = 0.094, 
// tot_access_cost = 2357701, non_comp_miss_cnt = 30134, comp_miss_cnt = 1781101
// ewma_window = 200
// spec accs cost = 1951102, num of spec hits = 7089
// num of ads per DS=[1129, 1205, 1152].  avg update interval = 1721.2 req

Twitter45.C4K.bpe14.2000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 27.73 | bw = 34.37 | hit_ratio = 0.092, 
// tot_access_cost = 959391, non_comp_miss_cnt = 35763, comp_miss_cnt = 1781101
// ewma_window = 200
// spec accs cost = 552246, num of spec hits = 1157
// num of ads per DS=[1134, 1208, 1151].  avg update interval = 1717.7 req

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

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.19 | bw = 14.02 | hit_ratio = 0.9, 
// tot_access_cost = 13479184, non_comp_miss_cnt = 13610, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 3162303, num of spec hits = 234425
// num of ads per DS=[15114, 15158, 18334].  avg update interval = 370.3 req

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 31.39 | bw = 13.29 | hit_ratio = 0.9, 
// tot_access_cost = 14944724, non_comp_miss_cnt = 2676, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 4815577, num of spec hits = 327293
// num of ads per DS=[15005, 15043, 15131].  avg update interval = 398.4 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 6.98 | bw = 24.72 | hit_ratio = 0.84, 
// tot_access_cost = 8159560, non_comp_miss_cnt = 66064, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 1568203, num of spec hits = 55509
// num of ads per DS=[15127, 18376, 19881].  avg update interval = 224.8 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 48.30 | bw = 21.00 | hit_ratio = 0.85, 
// tot_access_cost = 10695648, non_comp_miss_cnt = 15700, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 4151084, num of spec hits = 138798
// num of ads per DS=[15573, 15218, 14858].  avg update interval = 262.9 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.48 | bw = 50.98 | hit_ratio = 0.49, 
// tot_access_cost = 3122027, non_comp_miss_cnt = 185264, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 630493, num of spec hits = 9897
// num of ads per DS=[6435, 6434, 6435].  avg update interval = 388.5 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 140.44 | bw = 57.90 | hit_ratio = 0.54, 
// tot_access_cost = 5395431, non_comp_miss_cnt = 68332, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 2907351, num of spec hits = 122769
// num of ads per DS=[9653, 9653, 9654].  avg update interval = 259.0 req

F2.C64K.bpe14.10000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 4.69 | bw = 13.80 | hit_ratio = 0.92, 
// tot_access_cost = 21542572, non_comp_miss_cnt = 61876, comp_miss_cnt = 783777
// ewma_window = 1280
// spec accs cost = 3162221, num of spec hits = 9788
// num of ads per DS=[23553, 24852, 24828].  avg update interval = 409.7 req

F2.C64K.bpe14.10000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 27.29 | bw = 12.53 | hit_ratio = 0.92, 
// tot_access_cost = 23240730, non_comp_miss_cnt = 48480, comp_miss_cnt = 783777
// ewma_window = 1280
// spec accs cost = 5143777, num of spec hits = 164962
// num of ads per DS=[22282, 17879, 17159].  avg update interval = 523.4 req

IBM1.C64K.bpe14.948Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 21.07 | bw = 74.45 | hit_ratio = 0.4, 
// tot_access_cost = 3000032, non_comp_miss_cnt = 109243, comp_miss_cnt = 456478
// ewma_window = 1280
// spec accs cost = 2792661, num of spec hits = 294239
// num of ads per DS=[11475, 11528, 25439].  avg update interval = 58.7 req

IBM1.C64K.bpe14.948Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 150.75 | bw = 66.04 | hit_ratio = 0.52, 
// tot_access_cost = 5438720, non_comp_miss_cnt = 1764, comp_miss_cnt = 456478
// ewma_window = 1280
// spec accs cost = 5295511, num of spec hits = 425062
// num of ads per DS=[11502, 11536, 11548].  avg update interval = 82.2 req

IBM7.C64K.bpe14.4006Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.42 | bw = 22.52 | hit_ratio = 0.83, 
// tot_access_cost = 9200379, non_comp_miss_cnt = 73075, comp_miss_cnt = 611301
// ewma_window = 1280
// spec accs cost = 3638749, num of spec hits = 760501
// num of ads per DS=[16685, 16968, 22728].  avg update interval = 213.2 req

IBM7.C64K.bpe14.4006Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 50.15 | bw = 21.08 | hit_ratio = 0.85, 
// tot_access_cost = 15986290, non_comp_miss_cnt = 5146, comp_miss_cnt = 611301
// ewma_window = 1280
// spec accs cost = 11496677, num of spec hits = 1179930
// num of ads per DS=[16287, 16355, 16381].  avg update interval = 245.2 req

Twitter17.C64K.bpe14.14000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.77 | bw = 7.03 | hit_ratio = 0.95, 
// tot_access_cost = 31943065, non_comp_miss_cnt = 54120, comp_miss_cnt = 639610
// ewma_window = 1280
// spec accs cost = 5263078, num of spec hits = 62996
// num of ads per DS=[9634, 11653, 12816].  avg update interval = 1231.6 req

Twitter17.C64K.bpe14.14000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.33 | bw = 6.39 | hit_ratio = 0.95, 
// tot_access_cost = 34225608, non_comp_miss_cnt = 8272, comp_miss_cnt = 639610
// ewma_window = 1280
// spec accs cost = 7604639, num of spec hits = 136243
// num of ads per DS=[9634, 9634, 9634].  avg update interval = 1453.2 req

Twitter45.C64K.bpe14.2000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 25.63 | bw = 76.56 | hit_ratio = 0.16, 
// tot_access_cost = 1009975, non_comp_miss_cnt = 72187, comp_miss_cnt = 1602943
// ewma_window = 1280
// spec accs cost = 332612, num of spec hits = 962
// num of ads per DS=[6441, 6443, 6440].  avg update interval = 310.5 req

Twitter45.C64K.bpe14.2000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact4.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 249.87 | bw = 77.47 | hit_ratio = 0.17, 
// tot_access_cost = 1843118, non_comp_miss_cnt = 56727, comp_miss_cnt = 1602943
// ewma_window = 1280
// spec accs cost = 1171263, num of spec hits = 18746
// num of ads per DS=[6441, 6443, 6441].  avg update interval = 310.5 req
