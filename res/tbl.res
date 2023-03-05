gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNAA | service_cost = 11.755945755945756
// tot_access_cost= 2325834.0, hit_ratio = 0.81, non_comp_miss_cnt = 123885, comp_miss_cnt = 64717
// estimation window = 100, // num of insertions between fpr_fnr estimations = 50
// avg num of fpr_fnr_updates = 1257, fpr_fnr_updates bw = 0.0013

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.Opt | service_cost = 5.116992116992117
// tot_access_cost= 1881137.0, hit_ratio = 0.94, non_comp_miss_cnt = 0, comp_miss_cnt = 64717
// estimation window = 100, 

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M100.B0.U1000.Opt | service_cost = 8.317555317555318
gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M500.B0.U1000.Opt | service_cost = 34.204347
// tot_access_cost= 1845847.0, hit_ratio = 0.94, non_comp_miss_cnt = 0, comp_miss_cnt = 64717
// estimation window = 100, // single client

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HPflat | service_cost = 7.5793375793375795
// tot_access_cost = 3819180.0, hit_ratio = 0.92, non_comp_miss_cnt = 10486, comp_miss_cnt = 64717
// estimation window = 100, // num of insertions between fpr_fnr estimations = 50
// avg num of fpr_fnr_updates = 0, fpr_fnr_updates bw = 0.0000

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HPewma | service_cost = 7.602825602825603
// tot_access_cost = 3870218.0, hit_ratio = 0.93, non_comp_miss_cnt = 9935, comp_miss_cnt = 64717
// estimation window = 100, // num of insertions between fpr_fnr estimations = 50
// avg num of fpr_fnr_updates = 0, fpr_fnr_updates bw = 0.0000

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HEflat | service_cost = 9.165878165878166
// tot_access_cost = 2597619, hit_ratio = 0.87, non_comp_miss_cnt = 66648, comp_miss_cnt = 64717
// estimation window = 100, // num of insertions between fpr_fnr estimations = 50
// avg num of fpr_fnr_updates = 0, fpr_fnr_updates bw = 0.0000
// spec accs cost = 1333302, num of spec hits = 280922

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M100.B0.U1000.FNA.HEewma | service_cost = 27.70889270889271
// tot_access_cost = 1518465, hit_ratio = 0.74, non_comp_miss_cnt = 197187, comp_miss_cnt = 64717
// estimation window = 100, spec accs cost = 46745, num of spec hits = 11751
// num of updates=261

gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HEewma.adF | service_cost = 7.978958978958979
// tot_access_cost = 3592851, hit_ratio = 0.91, non_comp_miss_cnt = 23005, comp_miss_cnt = 64717
// estimation window = 300, // spec accs cost = 2488523, num of spec hits = 379195
// num of ads per DS=[22, 23, 42]
// avg update interval = 34482.724137931036 req

// Trying improved self.mr0_ad_th, self.mr1_ad_th = 0.65, 0.01, and ewma_window_size = DS_size/10 (currently, 1k)
gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HEewma.adH | service_cost = 8.511768511768512
// tot_access_cost = 4195310, hit_ratio = 0.91, non_comp_miss_cnt = 21612, comp_miss_cnt = 64717
// estimation window = 1000, // spec accs cost = 3305925, num of spec hits = 483754
// num of ads per DS=[9, 12, 14]
// avg update interval = 85714.2 req

// Trying improved self.mr0_ad_th, self.mr1_ad_th = 0.7, 0.01, and ewma_window_size = DS_size/5 (currently, 2k)
gradle.C10K.bpe14.1000Kreq.3DSs.Kloc1.M50.B0.U1000.FNA.HEewma.adH | service_cost = 9.675129675129675
// tot_access_cost = 3869920, hit_ratio = 0.88, non_comp_miss_cnt = 51387, comp_miss_cnt = 64717
// estimation window = 2000, // spec accs cost = 2939007, num of spec hits = 428358
// num of ads per DS=[9, 19, 17]
// avg update interval = 66666.6 req


