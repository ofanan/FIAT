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

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 6.20 | bw = 17.17 | hit_ratio = 0.86, 
// tot_access_cost = 12673773, non_comp_miss_cnt = 3546, comp_miss_cnt = 813235
// ewma_window = 200
// spec accs cost = 2385611, num of spec hits = 7604
// num of ads per DS=[26947, 27147, 27220].  avg update interval = 221.4 req

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 42.91 | bw = 17.19 | hit_ratio = 0.86, 
// tot_access_cost = 13275294, non_comp_miss_cnt = 692, comp_miss_cnt = 813235
// ewma_window = 200
// spec accs cost = 2975003, num of spec hits = 10787
// num of ads per DS=[26917, 27113, 26966].  avg update interval = 222.2 req

Scarab.C4K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 14.44 | bw = 45.50 | hit_ratio = 0.58, 
// tot_access_cost = 6956839, non_comp_miss_cnt = 79245, comp_miss_cnt = 1614728
// ewma_window = 200
// spec accs cost = 2366482, num of spec hits = 98157
// num of ads per DS=[2582, 55169, 55813].  avg update interval = 105.7 req

Scarab.C4K.bpe14.4000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 125.84 | bw = 50.98 | hit_ratio = 0.59, 
// tot_access_cost = 9539479, non_comp_miss_cnt = 31404, comp_miss_cnt = 1614728
// ewma_window = 200
// spec accs cost = 4837275, num of spec hits = 41786
// num of ads per DS=[54582, 54408, 55254].  avg update interval = 73.1 req

F1.C4K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 21.82 | bw = 86.25 | hit_ratio = 0.31, 
// tot_access_cost = 2601526, non_comp_miss_cnt = 34979, comp_miss_cnt = 1696275
// ewma_window = 200
// spec accs cost = 1013516, num of spec hits = 5128
// num of ads per DS=[57465, 57644, 57709].  avg update interval = 43.4 req

F1.C4K.bpe14.2500Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 207.59 | bw = 86.34 | hit_ratio = 0.31, 
// tot_access_cost = 5163954, non_comp_miss_cnt = 16412, comp_miss_cnt = 1696275
// ewma_window = 200
// spec accs cost = 3582630, num of spec hits = 28940
// num of ads per DS=[56646, 56922, 57220].  avg update interval = 43.9 req

F2.C4K.bpe14.10000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 145.73 | bw = 36.74 | hit_ratio = 0.52, 
// tot_access_cost = 31885193, non_comp_miss_cnt = 147351, comp_miss_cnt = 4604026
// ewma_window = 200
// spec accs cost = 21988422, num of spec hits = 480391
// num of ads per DS=[3783, 3439, 3947].  avg update interval = 2686.0 req

F2.C4K.bpe14.10000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.40 | bw = 41.41 | hit_ratio = 0.5, 
// tot_access_cost = 13888025, non_comp_miss_cnt = 398335, comp_miss_cnt = 4604026
// ewma_window = 200
// spec accs cost = 3520504, num of spec hits = 56917
// num of ads per DS=[3919, 3700, 156787].  avg update interval = 182.5 req

IBM1.C4K.bpe14.948Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 150.98 | bw = 60.81 | hit_ratio = 0.51, 
// tot_access_cost = 5183339, non_comp_miss_cnt = 3351, comp_miss_cnt = 456478
// ewma_window = 200
// spec accs cost = 4894754, num of spec hits = 354594
// num of ads per DS=[15087, 15139, 15175].  avg update interval = 62.6 req

IBM1.C4K.bpe14.948Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 20.95 | bw = 70.49 | hit_ratio = 0.4, 
// tot_access_cost = 2925951, non_comp_miss_cnt = 107901, comp_miss_cnt = 456478
// ewma_window = 200
// spec accs cost = 2637433, num of spec hits = 246497
// num of ads per DS=[15185, 15263, 25485].  avg update interval = 50.8 req

IBM7.C4K.bpe14.4006Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 49.24 | bw = 19.35 | hit_ratio = 0.85, 
// tot_access_cost = 13175292, non_comp_miss_cnt = 2269, comp_miss_cnt = 611301
// ewma_window = 200
// spec accs cost = 7123029, num of spec hits = 410863
// num of ads per DS=[20282, 20349, 20358].  avg update interval = 197.1 req

IBM7.C4K.bpe14.4006Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.18 | bw = 20.68 | hit_ratio = 0.84, 
// tot_access_cost = 9052437, non_comp_miss_cnt = 45382, comp_miss_cnt = 611301
// ewma_window = 200
// spec accs cost = 2577644, num of spec hits = 195415
// num of ads per DS=[20585, 21969, 22748].  avg update interval = 184.0 req

Twitter17.C4K.bpe14.14000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 74.22 | bw = 28.14 | hit_ratio = 0.76, 
// tot_access_cost = 36845600, non_comp_miss_cnt = 13954, comp_miss_cnt = 3326741
// ewma_window = 200
// spec accs cost = 15428044, num of spec hits = 166927
// num of ads per DS=[2820, 2838, 112091].  avg update interval = 356.7 req

Twitter17.C4K.bpe14.14000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.38 | bw = 28.33 | hit_ratio = 0.75, 
// tot_access_cost = 26484282, non_comp_miss_cnt = 167708, comp_miss_cnt = 3326741
// ewma_window = 200
// spec accs cost = 5218306, num of spec hits = 17432
// num of ads per DS=[2929, 112723, 2838].  avg update interval = 354.5 req

Twitter45.C4K.bpe14.2000Kreq.3DSs.Kloc1.M300.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 271.73 | bw = 54.40 | hit_ratio = 0.098, 
// tot_access_cost = 2088696, non_comp_miss_cnt = 23496, comp_miss_cnt = 1781101
// ewma_window = 200
// spec accs cost = 1671551, num of spec hits = 4618
// num of ads per DS=[1380, 1394, 1389].  avg update interval = 1441.3 req

Twitter45.C4K.bpe14.2000Kreq.3DSs.Kloc1.M30.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 27.63 | bw = 53.96 | hit_ratio = 0.096, 
// tot_access_cost = 1000445, non_comp_miss_cnt = 27495, comp_miss_cnt = 1781101
// ewma_window = 200
// spec accs cost = 583881, num of spec hits = 1096
// num of ads per DS=[1382, 1396, 1901].  avg update interval = 1282.3 req

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

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.19 | bw = 14.02 | hit_ratio = 0.9, 
// tot_access_cost = 13479184, non_comp_miss_cnt = 13610, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 3162303, num of spec hits = 234425
// num of ads per DS=[15114, 15158, 18334].  avg update interval = 370.3 req

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.19 | bw = 14.02 | hit_ratio = 0.9, 
// tot_access_cost = 13479184, non_comp_miss_cnt = 13610, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 3162303, num of spec hits = 234425
// num of ads per DS=[15114, 15158, 18334].  avg update interval = 370.3 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 6.98 | bw = 24.72 | hit_ratio = 0.84, 
// tot_access_cost = 8159560, non_comp_miss_cnt = 66064, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 1568203, num of spec hits = 55509
// num of ads per DS=[15127, 18376, 19881].  avg update interval = 224.8 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 6.98 | bw = 24.72 | hit_ratio = 0.84, 
// tot_access_cost = 8159560, non_comp_miss_cnt = 66064, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 1568203, num of spec hits = 55509
// num of ads per DS=[15127, 18376, 19881].  avg update interval = 224.8 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.19 | bw = 57.95 | hit_ratio = 0.5, 
// tot_access_cost = 3194424, non_comp_miss_cnt = 158796, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 657341, num of spec hits = 8598
// num of ads per DS=[6437, 6436, 14431].  avg update interval = 274.7 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.19 | bw = 57.95 | hit_ratio = 0.5, 
// tot_access_cost = 3194424, non_comp_miss_cnt = 158796, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 657341, num of spec hits = 8598
// num of ads per DS=[6437, 6436, 14431].  avg update interval = 274.7 req

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 31.39 | bw = 13.29 | hit_ratio = 0.9, 
// tot_access_cost = 14944724, non_comp_miss_cnt = 2676, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 4815577, num of spec hits = 327293
// num of ads per DS=[15005, 15043, 15131].  avg update interval = 398.4 req

F2.C64K.bpe14.10000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 4.69 | bw = 13.80 | hit_ratio = 0.92, 
// tot_access_cost = 21542572, non_comp_miss_cnt = 61876, comp_miss_cnt = 783777
// ewma_window = 1280
// spec accs cost = 3162221, num of spec hits = 9788
// num of ads per DS=[23553, 24852, 24828].  avg update interval = 409.7 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 48.30 | bw = 21.00 | hit_ratio = 0.85, 
// tot_access_cost = 10695648, non_comp_miss_cnt = 15700, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 4151084, num of spec hits = 138798
// num of ads per DS=[15573, 15218, 14858].  avg update interval = 262.9 req

IBM1.C64K.bpe14.948Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 21.07 | bw = 74.45 | hit_ratio = 0.4, 
// tot_access_cost = 3000032, non_comp_miss_cnt = 109243, comp_miss_cnt = 456478
// ewma_window = 1280
// spec accs cost = 2792661, num of spec hits = 294239
// num of ads per DS=[11475, 11528, 25439].  avg update interval = 58.7 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 141.37 | bw = 59.08 | hit_ratio = 0.54, 
// tot_access_cost = 5222376, non_comp_miss_cnt = 76630, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 2729663, num of spec hits = 111674
// num of ads per DS=[9654, 9655, 9655].  avg update interval = 258.9 req

IBM7.C64K.bpe14.4006Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.42 | bw = 22.52 | hit_ratio = 0.83, 
// tot_access_cost = 9200379, non_comp_miss_cnt = 73075, comp_miss_cnt = 611301
// ewma_window = 1280
// spec accs cost = 3638749, num of spec hits = 760501
// num of ads per DS=[16685, 16968, 22728].  avg update interval = 213.2 req

F2.C64K.bpe14.10000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 27.29 | bw = 12.53 | hit_ratio = 0.92, 
// tot_access_cost = 23240730, non_comp_miss_cnt = 48480, comp_miss_cnt = 783777
// ewma_window = 1280
// spec accs cost = 5143777, num of spec hits = 164962
// num of ads per DS=[22282, 17879, 17159].  avg update interval = 523.4 req

IBM1.C64K.bpe14.948Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 150.75 | bw = 66.04 | hit_ratio = 0.52, 
// tot_access_cost = 5438720, non_comp_miss_cnt = 1764, comp_miss_cnt = 456478
// ewma_window = 1280
// spec accs cost = 5295511, num of spec hits = 425062
// num of ads per DS=[11502, 11536, 11548].  avg update interval = 82.2 req

Twitter17.C64K.bpe14.14000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.77 | bw = 7.03 | hit_ratio = 0.95, 
// tot_access_cost = 31943065, non_comp_miss_cnt = 54120, comp_miss_cnt = 639610
// ewma_window = 1280
// spec accs cost = 5263078, num of spec hits = 62996
// num of ads per DS=[9634, 11653, 12816].  avg update interval = 1231.6 req

Twitter45.C64K.bpe14.2000Kreq.3DSs.Kloc1.M30.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 25.56 | bw = 70.21 | hit_ratio = 0.16, 
// tot_access_cost = 993990, non_comp_miss_cnt = 68003, comp_miss_cnt = 1602943
// ewma_window = 1280
// spec accs cost = 302238, num of spec hits = 686
// num of ads per DS=[6437, 6440, 6439].  avg update interval = 310.6 req

IBM7.C64K.bpe14.4006Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 50.15 | bw = 21.08 | hit_ratio = 0.85, 
// tot_access_cost = 15986290, non_comp_miss_cnt = 5146, comp_miss_cnt = 611301
// ewma_window = 1280
// spec accs cost = 11496677, num of spec hits = 1179930
// num of ads per DS=[16287, 16355, 16381].  avg update interval = 245.2 req

Wiki.C16K.bpe14.6000Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 37.52 | bw = 16.15 | hit_ratio = 0.88, 
// tot_access_cost = 13791741, non_comp_miss_cnt = 1566, comp_miss_cnt = 702895
// ewma_window = 320
// spec accs cost = 3518229, num of spec hits = 139244
// num of ads per DS=[20848, 20947, 20862].  avg update interval = 287.3 req

Wiki.C16K.bpe14.6000Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.75 | bw = 16.38 | hit_ratio = 0.88, 
// tot_access_cost = 13148091, non_comp_miss_cnt = 8295, comp_miss_cnt = 702895
// ewma_window = 320
// spec accs cost = 2868207, num of spec hits = 113840
// num of ads per DS=[21512, 20985, 21535].  avg update interval = 281.1 req

Scarab.C16K.bpe14.4000Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 78.56 | bw = 31.67 | hit_ratio = 0.75, 
// tot_access_cost = 9576751, non_comp_miss_cnt = 27085, comp_miss_cnt = 988471
// ewma_window = 320
// spec accs cost = 3574018, num of spec hits = 55539
// num of ads per DS=[29670, 33085, 34032].  avg update interval = 124.0 req

Scarab.C16K.bpe14.4000Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.64 | bw = 33.01 | hit_ratio = 0.74, 
// tot_access_cost = 7184421, non_comp_miss_cnt = 57194, comp_miss_cnt = 988471
// ewma_window = 320
// spec accs cost = 1189952, num of spec hits = 7509
// num of ads per DS=[33673, 34369, 34720].  avg update interval = 116.8 req

Wiki.C4K.bpe14.6000Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.43 | bw = 17.32 | hit_ratio = 0.86, 
// tot_access_cost = 12245658, non_comp_miss_cnt = 18330, comp_miss_cnt = 813235
// ewma_window = 200
// spec accs cost = 2025417, num of spec hits = 3973
// num of ads per DS=[26970, 27844, 27971].  avg update interval = 217.4 req

F1.C16K.bpe14.2500Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 20.01 | bw = 75.19 | hit_ratio = 0.37, 
// tot_access_cost = 2529473, non_comp_miss_cnt = 85967, comp_miss_cnt = 1497381
// ewma_window = 320
// spec accs cost = 663538, num of spec hits = 13292
// num of ads per DS=[47612, 12694, 48654].  avg update interval = 68.8 req

F1.C16K.bpe14.2500Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 184.31 | bw = 77.77 | hit_ratio = 0.39, 
// tot_access_cost = 3685277, non_comp_miss_cnt = 26213, comp_miss_cnt = 1497381
// ewma_window = 320
// spec accs cost = 1700965, num of spec hits = 29520
// num of ads per DS=[47969, 47930, 47985].  avg update interval = 52.1 req

Twitter17.C64K.bpe14.14000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 16.33 | bw = 6.39 | hit_ratio = 0.95, 
// tot_access_cost = 34225608, non_comp_miss_cnt = 8272, comp_miss_cnt = 639610
// ewma_window = 1280
// spec accs cost = 7604639, num of spec hits = 136243
// num of ads per DS=[9634, 9634, 9634].  avg update interval = 1453.2 req

Scarab.C4K.bpe14.4000Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.81 | bw = 46.56 | hit_ratio = 0.55, 
// tot_access_cost = 5375993, non_comp_miss_cnt = 173629, comp_miss_cnt = 1614728
// ewma_window = 200
// spec accs cost = 806367, num of spec hits = 4305
// num of ads per DS=[2854, 55504, 56082].  avg update interval = 104.9 req

Twitter45.C64K.bpe14.2000Kreq.3DSs.Kloc1.M300.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 250.30 | bw = 69.55 | hit_ratio = 0.17, 
// tot_access_cost = 1604646, non_comp_miss_cnt = 60356, comp_miss_cnt = 1602943
// ewma_window = 1280
// spec accs cost = 917749, num of spec hits = 10229
// num of ads per DS=[6437, 6439, 6438].  avg update interval = 310.7 req

F1.C4K.bpe14.2500Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.72 | bw = 86.28 | hit_ratio = 0.31, 
// tot_access_cost = 1926391, non_comp_miss_cnt = 40724, comp_miss_cnt = 1696275
// ewma_window = 200
// spec accs cost = 350242, num of spec hits = 895
// num of ads per DS=[57679, 57838, 57869].  avg update interval = 43.3 req

Wiki.C16K.bpe14.6000Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.30 | bw = 16.87 | hit_ratio = 0.88, 
// tot_access_cost = 12479201, non_comp_miss_cnt = 29008, comp_miss_cnt = 702895
// ewma_window = 320
// spec accs cost = 2066263, num of spec hits = 22889
// num of ads per DS=[23273, 22619, 23884].  avg update interval = 258.0 req

F2.C16K.bpe14.10000Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 72.94 | bw = 22.04 | hit_ratio = 0.77, 
// tot_access_cost = 27624435, non_comp_miss_cnt = 140304, comp_miss_cnt = 2198799
// ewma_window = 320
// spec accs cost = 13043761, num of spec hits = 503753
// num of ads per DS=[6827, 7231, 4699].  avg update interval = 1599.4 req

IBM1.C16K.bpe14.948Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 152.49 | bw = 63.23 | hit_ratio = 0.51, 
// tot_access_cost = 5137449, non_comp_miss_cnt = 8266, comp_miss_cnt = 456478
// ewma_window = 320
// spec accs cost = 4880565, num of spec hits = 367573
// num of ads per DS=[13439, 13526, 11648].  avg update interval = 73.7 req

F2.C16K.bpe14.10000Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.03 | bw = 25.84 | hit_ratio = 0.76, 
// tot_access_cost = 18844145, non_comp_miss_cnt = 181925, comp_miss_cnt = 2198799
// ewma_window = 320
// spec accs cost = 3276601, num of spec hits = 69338
// num of ads per DS=[5860, 72724, 74705].  avg update interval = 195.7 req

Wiki.C64K.bpe14.6000Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.16 | bw = 14.88 | hit_ratio = 0.9, 
// tot_access_cost = 12808628, non_comp_miss_cnt = 37782, comp_miss_cnt = 575239
// ewma_window = 1280
// spec accs cost = 2297724, num of spec hits = 108515
// num of ads per DS=[15127, 18598, 18610].  avg update interval = 343.9 req

IBM1.C16K.bpe14.948Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 21.32 | bw = 69.09 | hit_ratio = 0.38, 
// tot_access_cost = 2643185, non_comp_miss_cnt = 128978, comp_miss_cnt = 456478
// ewma_window = 320
// spec accs cost = 2418206, num of spec hits = 271311
// num of ads per DS=[3277, 3285, 26690].  avg update interval = 85.5 req

Scarab.C16K.bpe14.4000Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 4.37 | bw = 34.29 | hit_ratio = 0.74, 
// tot_access_cost = 6873980, non_comp_miss_cnt = 70478, comp_miss_cnt = 988471
// ewma_window = 320
// spec accs cost = 958119, num of spec hits = 942
// num of ads per DS=[34765, 34766, 35409].  avg update interval = 114.4 req

IBM7.C16K.bpe14.4006Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 49.67 | bw = 21.49 | hit_ratio = 0.85, 
// tot_access_cost = 13512175, non_comp_miss_cnt = 6958, comp_miss_cnt = 611301
// ewma_window = 320
// spec accs cost = 7859719, num of spec hits = 619340
// num of ads per DS=[18132, 18185, 18711].  avg update interval = 218.4 req

IBM7.C16K.bpe14.4006Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.16 | bw = 21.50 | hit_ratio = 0.83, 
// tot_access_cost = 8702634, non_comp_miss_cnt = 54478, comp_miss_cnt = 611301
// ewma_window = 320
// spec accs cost = 2256448, num of spec hits = 252003
// num of ads per DS=[18282, 21853, 22778].  avg update interval = 191.0 req

F2.C4K.bpe14.10000Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.95 | bw = 57.62 | hit_ratio = 0.53, 
// tot_access_cost = 12858414, non_comp_miss_cnt = 58171, comp_miss_cnt = 4604026
// ewma_window = 200
// spec accs cost = 1966410, num of spec hits = 861
// num of ads per DS=[156751, 151385, 157611].  avg update interval = 64.4 req

F1.C16K.bpe14.2500Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 7.53 | bw = 64.25 | hit_ratio = 0.33, 
// tot_access_cost = 1956508, non_comp_miss_cnt = 188608, comp_miss_cnt = 1497381
// ewma_window = 320
// spec accs cost = 305382, num of spec hits = 933
// num of ads per DS=[12696, 12694, 12695].  avg update interval = 196.9 req

IBM1.C4K.bpe14.948Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 8.45 | bw = 80.30 | hit_ratio = 0.27, 
// tot_access_cost = 1115365, non_comp_miss_cnt = 233435, comp_miss_cnt = 456478
// ewma_window = 200
// spec accs cost = 825092, num of spec hits = 117192
// num of ads per DS=[15190, 26740, 26710].  avg update interval = 41.4 req

Scarab.C64K.bpe14.4000Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.62 | bw = 26.25 | hit_ratio = 0.83, 
// tot_access_cost = 7758876, non_comp_miss_cnt = 77814, comp_miss_cnt = 592611
// ewma_window = 1280
// spec accs cost = 1126271, num of spec hits = 12275
// num of ads per DS=[18329, 20461, 20586].  avg update interval = 202.1 req

IBM7.C4K.bpe14.4006Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.71 | bw = 21.43 | hit_ratio = 0.83, 
// tot_access_cost = 8040887, non_comp_miss_cnt = 71046, comp_miss_cnt = 611301
// ewma_window = 200
// spec accs cost = 1453955, num of spec hits = 78759
// num of ads per DS=[21709, 22935, 23321].  avg update interval = 176.8 req

F1.C64K.bpe14.2500Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 6.20 | bw = 52.57 | hit_ratio = 0.5, 
// tot_access_cost = 2991297, non_comp_miss_cnt = 166777, comp_miss_cnt = 1084006
// ewma_window = 1280
// spec accs cost = 457644, num of spec hits = 2101
// num of ads per DS=[6436, 6436, 6437].  avg update interval = 388.4 req

Twitter17.C16K.bpe14.14000Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 35.10 | bw = 14.92 | hit_ratio = 0.89, 
// tot_access_cost = 38640511, non_comp_miss_cnt = 1816, comp_miss_cnt = 1507468
// ewma_window = 320
// spec accs cost = 13798801, num of spec hits = 191428
// num of ads per DS=[2911, 2912, 2910].  avg update interval = 4809.3 req

Twitter45.C16K.bpe14.2000Kreq.3DSs.Kloc1.M300.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 260.88 | bw = 74.67 | hit_ratio = 0.13, 
// tot_access_cost = 1231916, non_comp_miss_cnt = 36666, comp_miss_cnt = 1698457
// ewma_window = 320
// spec accs cost = 676622, num of spec hits = 2574
// num of ads per DS=[1803, 1794, 1793].  avg update interval = 1113.2 req

F2.C16K.bpe14.10000Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 4.24 | bw = 27.44 | hit_ratio = 0.76, 
// tot_access_cost = 18017600, non_comp_miss_cnt = 243331, comp_miss_cnt = 2198799
// ewma_window = 320
// spec accs cost = 2549391, num of spec hits = 3041
// num of ads per DS=[7682, 73772, 75605].  avg update interval = 191.0 req

Twitter17.C16K.bpe14.14000Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 5.62 | bw = 15.60 | hit_ratio = 0.88, 
// tot_access_cost = 29648408, non_comp_miss_cnt = 127077, comp_miss_cnt = 1507468
// ewma_window = 320
// spec accs cost = 4730454, num of spec hits = 11083
// num of ads per DS=[2940, 51298, 3497].  avg update interval = 727.5 req

IBM1.C16K.bpe14.948Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 8.49 | bw = 83.88 | hit_ratio = 0.27, 
// tot_access_cost = 1081548, non_comp_miss_cnt = 239785, comp_miss_cnt = 456478
// ewma_window = 320
// spec accs cost = 814220, num of spec hits = 134726
// num of ads per DS=[3286, 26641, 26681].  avg update interval = 50.2 req

Twitter45.C16K.bpe14.2000Kreq.3DSs.Kloc1.M30.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 26.50 | bw = 74.90 | hit_ratio = 0.13, 
// tot_access_cost = 865568, non_comp_miss_cnt = 39120, comp_miss_cnt = 1698457
// ewma_window = 320
// spec accs cost = 310939, num of spec hits = 543
// num of ads per DS=[1805, 1796, 1791].  avg update interval = 1112.8 req

Twitter17.C4K.bpe14.14000Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 4.30 | bw = 27.65 | hit_ratio = 0.75, 
// tot_access_cost = 25118942, non_comp_miss_cnt = 185922, comp_miss_cnt = 3326741
// ewma_window = 200
// spec accs cost = 3862413, num of spec hits = 1025
// num of ads per DS=[112152, 2846, 2841].  avg update interval = 356.4 req

IBM7.C16K.bpe14.4006Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.71 | bw = 21.97 | hit_ratio = 0.83, 
// tot_access_cost = 7928267, non_comp_miss_cnt = 81070, comp_miss_cnt = 611301
// ewma_window = 320
// spec accs cost = 1349254, num of spec hits = 84792
// num of ads per DS=[20929, 23085, 23232].  avg update interval = 178.7 req

Twitter45.C4K.bpe14.2000Kreq.3DSs.Kloc1.M10.B0.U400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.33 | bw = 54.53 | hit_ratio = 0.095, 
// tot_access_cost = 563769, non_comp_miss_cnt = 27950, comp_miss_cnt = 1781101
// ewma_window = 200
// spec accs cost = 146632, num of spec hits = 158
// num of ads per DS=[1383, 1398, 1386].  avg update interval = 1439.9 req

F2.C64K.bpe14.10000Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 2.99 | bw = 13.22 | hit_ratio = 0.91, 
// tot_access_cost = 21341356, non_comp_miss_cnt = 67685, comp_miss_cnt = 783777
// ewma_window = 1280
// spec accs cost = 2973334, num of spec hits = 2268
// num of ads per DS=[24956, 26123, 26438].  avg update interval = 387.0 req

IBM1.C64K.bpe14.948Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 8.61 | bw = 87.64 | hit_ratio = 0.24, 
// tot_access_cost = 927327, non_comp_miss_cnt = 266727, comp_miss_cnt = 456478
// ewma_window = 1280
// spec accs cost = 663176, num of spec hits = 100296
// num of ads per DS=[12808, 26396, 26434].  avg update interval = 43.3 req

Twitter17.C16K.bpe14.14000Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.28 | bw = 12.92 | hit_ratio = 0.88, 
// tot_access_cost = 29262488, non_comp_miss_cnt = 159380, comp_miss_cnt = 1507468
// ewma_window = 320
// spec accs cost = 4375823, num of spec hits = 1184
// num of ads per DS=[3423, 51800, 3425].  avg update interval = 716.1 req

Twitter45.C16K.bpe14.2000Kreq.3DSs.Kloc1.M10.B0.U1600.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 9.04 | bw = 74.90 | hit_ratio = 0.13, 
// tot_access_cost = 688355, non_comp_miss_cnt = 39747, comp_miss_cnt = 1698457
// ewma_window = 320
// spec accs cost = 134212, num of spec hits = 88
// num of ads per DS=[1806, 1793, 1793].  avg update interval = 1112.8 req

IBM7.C64K.bpe14.4006Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 3.74 | bw = 23.01 | hit_ratio = 0.82, 
// tot_access_cost = 7944969, non_comp_miss_cnt = 93909, comp_miss_cnt = 611301
// ewma_window = 1280
// spec accs cost = 1718141, num of spec hits = 396960
// num of ads per DS=[16871, 22852, 22865].  avg update interval = 192.0 req

Twitter17.C64K.bpe14.14000Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 2.76 | bw = 7.48 | hit_ratio = 0.95, 
// tot_access_cost = 31371461, non_comp_miss_cnt = 80726, comp_miss_cnt = 639610
// ewma_window = 1280
// spec accs cost = 4681804, num of spec hits = 16974
// num of ads per DS=[11653, 12816, 12816].  avg update interval = 1126.5 req

Twitter45.C64K.bpe14.2000Kreq.3DSs.Kloc1.M10.B0.U6400.SALSA_DEP4.mr0th0.88.mr1th0.01.uIntFact2.0.minFU10.alpha00.5.alpha10.25.per_param10.scaleF1.1.scaleD1.1 | service_cost = 8.78 | bw = 70.68 | hit_ratio = 0.16, 
// tot_access_cost = 850247, non_comp_miss_cnt = 67844, comp_miss_cnt = 1602943
// ewma_window = 1280
// spec accs cost = 157239, num of spec hits = 179
// num of ads per DS=[6437, 6441, 6439].  avg update interval = 310.6 req
