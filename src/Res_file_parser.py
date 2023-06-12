import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import MyConfig
from printf import printf 
from _ast import If

"""
This class parses ".res" file generated by python_simulator, and produces .tikz .data files, to show the result as a plot (graph) / histogram (bars) / table.
"""
# Indices of the fields in a standard settings string, that details the parameters of an experiment.
trace_idx               = 0
cache_size_idx          = 1
bpe_idx                 = 2
num_of_req_idx          = 3
num_of_DSs_idx          = 4
kloc_idx                = 5
missp_idx               = 6
bw_idx                  = 7
uInterval_idx           = 8
alg_idx                 = 9 # the cache selection and advertisement alg', e.g.: Opt, FNAA, SALSA
mr0th_idx               = 10 # mr0 th for SALSA's advertisement decision
mr1th_idx               = 12 # mr0 th for SALSA's advertisement decision
uInterval_factor_idx    = 14 # mr0 th for SALSA's advertisement decision
min_num_of_fields       = alg_idx + 1

BAR_WIDTH = 0.25
MARKER_SIZE             = 16
MARKER_SIZE_SMALL       = 1
LINE_WIDTH              = 3 
LINE_WIDTH_SMALL        = 1 
FONT_SIZE               = 20
FONT_SIZE_SMALL         = 5
LEGEND_FONT_SIZE        = 16
LEGEND_FONT_SIZE_SMALL  = 5 

class Res_file_parser (object):  

    set_plt_params = lambda self, size='large' : matplotlib.rcParams.update({'font.size': FONT_SIZE, 
                                                                             'legend.fontsize': LEGEND_FONT_SIZE,
                                                                             'xtick.labelsize':FONT_SIZE,
                                                                             'ytick.labelsize':FONT_SIZE,
                                                                             'axes.labelsize': FONT_SIZE,
                                                                             'axes.titlesize':FONT_SIZE,}) if (size=='large') else matplotlib.rcParams.update({
                                                                             'font.size': FONT_SIZE_SMALL, 
                                                                             'legend.fontsize': LEGEND_FONT_SIZE_SMALL,
                                                                             'xtick.labelsize':FONT_SIZE_SMALL,
                                                                             'ytick.labelsize':FONT_SIZE_SMALL,
                                                                             'axes.labelsize': FONT_SIZE_SMALL,
                                                                             'axes.titlesize':FONT_SIZE_SMALL,
                                                                             })
    def __init__ (self):
        """
        """
        # List of algorithms' names, used in the plots' legend, for the dist' case
        self.labelOfMode = {}

        self.strOfMode = {'FNAA' : r'HeCS$_{\rm FNA}$',
                          'SALSA' : 'SALSA',
                          'SALSA1' : 'SALSA1',
                          'SALSA2' : 'SALSA2',
                          'SALSA085' : 'SALSA_.85',
                          'SALSA285' : 'SALSA2_.85',
                          # 'SALSA09' : 'SALSA_0.9',
                          # 'SALSA29' : 'SALSA_2.9',
                          'SALSA3'    : 'SALSA3'
                           }
        
        self.strOfTrace = {'F2'     : 'F2',
                          'gradle'  : 'Gradle',
                          'wiki1'   : 'Wiki',
                          'scarab'  : 'Scarab'
                           }
        # The colors used for each alg's plot, in the dist' case
        self.colorOfMode = {'Opt '      : 'green',
                            'FNAA'      : 'blue',
                            'SALSA'     : 'cyan',
                            'SALSA1'    : 'cyan',
                            'SALSA2'    : 'black',
                            'SALSA285'  : 'magenta',
                            'SALSA085'  : 'purple',
                            # 'SALSA29'   : 'red',
                            # 'SALSA09'   : 'purple',
                            'SALSA29'   : 'red',   
                            'SALSA3'    : 'brown',
                            # 'others'    : , 'black','magenta','red', 'brown', yellow
                            }

        # The markers used for each alg', in the dist' case
        self.markerOfMode = {'Opt'      : 'o',
                            'FNAA'      : 'v',
                            'SALSA'     : '^',
                            'SALSA3'    : 's',
                            'Tetra'     : 'p',
                            'Tetra dyn' : 'X',
                            'CEDAR'     : '<',
                            'Morris'    : '>'}
        self.list_of_dicts  = []
        self.add_plot_opt   = '\t\t\\addplot [color = green, mark=+, line width = \\plotLineWidth] coordinates {\n\t\t'
        self.add_plot_str1  = '\t\t\\addplot [color = blue, mark=square, line width = \\plotLineWidth] coordinates {\n\t\t'
        self.add_plot_fno1  = '\t\t\\addplot [color = purple, mark=o, line width = \\plotLineWidth] coordinates {\n\t\t'
        self.add_plot_fna1  = '\t\t\\addplot [color = red, mark=triangle*, line width = \\plotLineWidth] coordinates {\n\t\t'
        self.add_plot_fno2  = '\t\t\\addplot [color = black, mark = square,      mark options = {mark size = 2, fill = black}, line width = \plotLineWidth] coordinates {\n\t\t'
        self.add_plot_fna2  = '\t\t\\addplot [color = blue,  mark = *, mark options = {mark size = 2, fill = blue},  line width = \plotLineWidth] coordinates {\n\t\t'
        self.end_add_plot_str = '\n\t\t};'
        self.add_legend_str = '\n\t\t\\addlegendentry {'
        self.add_plot_str_dict = {'Opt' : self.add_plot_opt, 'FNAA' : self.add_plot_fna2, 'FNOA' : self.add_plot_fno2}
        self.legend_entry_dict = {'Opt' : '\\opt', 
                                  'FNAA' : '\\pgmfna', 
                                  'FNOA' : '\\pgmfno',
                                  'FNOA' : '\\pgmfno'}
        
        self.set_plt_params ()


    def parse_line (self, line):
        splitted_line = line.split ("|")
         
        settings      = splitted_line[0]
        if len (splitted_line)<2:
            MyConfig.error ('format error. splitted_line={}' .format (splitted_line))
        if len (splitted_line[1].split(" = "))<2:
            MyConfig.error ('format error. splitted_line={}' .format (splitted_line))
        serviceCost   = float(splitted_line[1].split(" = ")[1])
        bwCost        = None # default value, to be checked later
        if (len(splitted_line)>2):
            bwCost    = float(splitted_line[2].split(" = ")[1])
        splitted_line = settings.split (".")
        mode          = splitted_line[alg_idx].split(" ")[0]
        self.dict = {
            "trace"         : splitted_line        [trace_idx],
            "cache_size"    : int (splitted_line   [cache_size_idx].split("C")[1].split("K")[0]),   
            "num_of_req"    : int (splitted_line   [num_of_req_idx].split("Kreq")[0]),
            "num_of_DSs"    : int (splitted_line   [num_of_DSs_idx].split("DSs")[0]), 
            "Kloc"          : int (splitted_line   [kloc_idx]      .split("Kloc")[1]),
            "missp"         : int (splitted_line   [missp_idx]     .split("M")[1]),
            'designed_bw'   : int(splitted_line    [bw_idx]        .split('B')[1]), 
            "alg_mode"      : mode,
            'serviceCost'   : serviceCost
            }
        if mode=='Opt': # Opt doesn't have meaningful fields for bpe, uInterval or bw
            return
        
        if len (splitted_line) < min_num_of_fields:
            print ("encountered a format error. Splitted line is is {}" .format (splitted_line))
            return False

        self.dict['bpe'] = int (splitted_line [bpe_idx].split("bpe")[1])
        if (bwCost != None):
            self.dict['bwCost'] = bwCost
            
        uInterval_fld = splitted_line [uInterval_idx].split('U')
        if len(uInterval_fld)<2:
                print ("encountered a format error. Splitted line is is {}" .format (splitted_line))
                return False
        uInterval_str = uInterval_fld[1] 
        uInterval_val = uInterval_str.split('-')
        self.dict['min_uInterval'] = int(uInterval_val[0])
        self.dict['uInterval']     = int(uInterval_val[0]) # for backward compatibility, keep also this field 

        if not(mode.startswith('SALSA')):
            return 
            
        if len(uInterval_val)>1: # a single uInterval val is given
            self.dict['max_uInterval'] = int(uInterval_val[1]) # for backward compatibility, keep also this field

        if len (splitted_line) <= mr0th_idx:
            return # no further data in this .res entry
        self.dict['mr0_th'] = float ('0.' + splitted_line [mr0th_idx+1])
        self.dict['mr1_th'] = float ('0.' + splitted_line [mr1th_idx+1])
        self.dict['uInterval_factor'] = float (splitted_line [uInterval_factor_idx].split("uIntFact")[1])
         
    def print_tbl (self):
        """
        Print table of service costs, normalized w.r.t. to Opt, in tikz format
        """
        self.tbl_output_file    = open ("../res/missp.txt", "w")
        traces = ['wiki1', 'gradle', 'scarab', 'F2']

        printf (self.tbl_output_file, '\tMiss Penalty & Policy ')
        for trace in traces:
            trace_to_print = 'F2' if trace == 'umass' else trace 
            printf (self.tbl_output_file, '& {}' .format (trace_to_print))
        printf (self.tbl_output_file, '\\\\\n\t\\hline\n\t\\hline\n')

        self.gen_filtered_list(self.list_of_dicts, num_of_req = 1000) 
        for missp in [30, 100, 300]:
            printf (self.tbl_output_file, '\t\\multirow{3}{*}{')
            printf (self.tbl_output_file, '{}' .format (missp))
            printf (self.tbl_output_file, '}\n')
            for alg_mode in ['FNA', 'FNAA']:
                if (alg_mode == 'FNA'):
                    printf (self.tbl_output_file, '\t&FNAH' .format(alg_mode))
                if (alg_mode == 'FNAA'):
                    printf (self.tbl_output_file, '\t&FNAA$' .format(alg_mode))
                    
                for trace in traces:
                    opt_cost = self.gen_filtered_list(self.list_of_dicts, 
                                                              trace = trace, cache_size = 10, num_of_DSs = 3, Kloc = 1, 
                                                              missp = missp, alg_mode = 'Opt')[0]['serviceCost']
                    alg_cost = self.gen_filtered_list(self.list_of_dicts, 
                                                              trace = trace, cache_size = 10, bpe = 14, num_of_DSs = 3, Kloc = 1, 
                                                              missp = missp, uInterval = 1000, alg_mode = alg_mode)[0]['serviceCost']
                    printf (self.tbl_output_file, ' & {:.4f}' .format(alg_cost / opt_cost))
                printf (self.tbl_output_file, ' \\\\\n')
            printf (self.tbl_output_file, '\t\\hline\n\n')
                
    def print_bar_k_loc (self):
        """
        Print table of service costs, normalized w.r.t. Opt, in the following format
        # uInterval    FNO_kloc1 FNA_kloc1 FNO_kloc2 FNA_kloc2 FNO_kloc3 FNA_kloc3
        # 256          2.0280    1.7800    2.4294    1.1564    2.4859    1.1039
        # 1024         2.0280    1.7800    2.4294    1.1564    2.4859    1.1039
        """
        self.bar_k_loc_output_file    = open ("../res/k_loc.txt", "w")

        printf (self.bar_k_loc_output_file, 'uInterval\t FNO_kloc1\t FNA_kloc1\t FNO_kloc2\t FNA_kloc2\t FNO_kloc3\t FNA_kloc3\n')
        
        self.gen_filtered_list(self.list_of_dicts, num_of_req = 4300, missp = 1000) 
        for uInterval in [256, 1024]:
            if (uInterval==256):
                printf (self.bar_k_loc_output_file, '{} \t\t' .format (uInterval))
            else:
                printf (self.bar_k_loc_output_file, '{}\t\t' .format (uInterval))
            for Kloc in [1, 2, 3]:
                for alg_mode in ['FNOA', 'FNAA']:
                    opt_cost = self.gen_filtered_list(self.list_of_dicts, 
                            uInterval = 256, num_of_DSs = 8, Kloc = Kloc, alg_mode = 'Opt')
                    if (opt_cost == []):
                        opt_cost = self.gen_filtered_list(self.list_of_dicts, 
                                uInterval = 1024, num_of_DSs = 8, Kloc = Kloc, alg_mode = 'Opt')
                    opt_cost = opt_cost[0]['serviceCost']
                    alg_cost = self.gen_filtered_list(self.list_of_dicts, 
                            uInterval = uInterval, bpe = 14, num_of_DSs = 8, Kloc = Kloc, alg_mode = alg_mode)[0]['serviceCost']
                    printf (self.bar_k_loc_output_file, ' {:.4f}\t\t' .format(alg_cost / opt_cost))
            printf (self.bar_k_loc_output_file, ' \n')

    def print_missp_bars_for_tikz (self):
        """
        Print table of service costs, normalized w.r.t. to Opt, in the format below (assuming the tested miss penalty values are 50, 100, and 500):
        # input     FNO50     FNA50     FNO100    FNA100    FNO500    FNA500
        # wiki      2.0280    1.7800    2.4294    1.1564    2.4859    1.1039
        # gradle    2.5706    2.3600    3.8177    1.3357    4.0305    1.2014
        # scarab    2.5036    2.3053    3.2211    1.1940    3.3310    1.1183
        # F2        2.3688    2.2609    2.9604    1.1507    3.0546    1.0766
        """
        serviceCost_by_missp_output_file = open ("../res/serviceCost_by_missp.txt", "w")
        bwCost_by_missp_output_file      = open ("../res/bwCost_by_missp.txt", "w")
        traces = ['gradle', 'wiki', 'scarab', 'F2']

        modes = ['FNAA', 'SALSA1', 'SALSA2']
        missp_vals = [30, 100, 300]
        for output_file in [serviceCost_by_missp_output_file, bwCost_by_missp_output_file]:
            printf (output_file, 'input \t ')
            for missp_val in missp_vals:
                for mode in modes:
                    printf (output_file, '{}{}\t\t' .format (mode, missp_val))
            printf (output_file, '\n')
        
        for trace in traces:
            trace_to_print = 'F2\t' if trace == 'umass' else trace 
            for output_file in [serviceCost_by_missp_output_file, bwCost_by_missp_output_file]:
                printf (output_file, '{}\t' .format (trace_to_print))
            for missp in missp_vals:
                for alg_mode in modes:
                    point = self.gen_filtered_list(self.list_of_dicts, 
                            trace = trace, cache_size = 10, num_of_DSs = 3, Kloc = 1,missp = missp, alg_mode = 'Opt')
                    if (point==[]):
                        
                        MyConfig.error ('no results for opt for trace={}, missp={}' .format (trace_to_print, missp))
                    opt_serviceCost = point[0]['serviceCost']
                    uInterval = 1000
                    point = self.gen_filtered_list(self.list_of_dicts, 
                            trace = trace, cache_size = 10, bpe = 14, num_of_DSs = 3, Kloc = 1, missp = missp, uInterval=uInterval, 
                            alg_mode = alg_mode)
                    if (point==[]): # no results for this settings 
                        printf (serviceCost_by_missp_output_file, 'N/A\t\t\t')
                        printf (bwCost_by_missp_output_file,      'N/A\t\t\t')
                        continue
                    alg_serviceCost = point[0]['serviceCost']
                    alg_bwCost      = point[0]['bwCost']
                    # alg_hitRatio    = point[0]['hitRatio']
                    printf (serviceCost_by_missp_output_file, ' {:.2f}\t\t' .format(alg_serviceCost / opt_serviceCost))
                    printf (bwCost_by_missp_output_file,      ' {:.2f}\t\t' .format(alg_bwCost))
                    # printf (bwCost_by_missp_output_file, ' {:.4f} \t' .format(alg_bwCost / opt_bwCost))
            for output_file in [serviceCost_by_missp_output_file, bwCost_by_missp_output_file]:
                printf (output_file, ' \n')

    def gen_filtered_list (self, list_to_filter, trace = None, cache_size=None, bpe=None, num_of_DSs=None, Kloc=1, missp=None, uInterval=None, 
                           num_of_req = 0, alg_mode = None):
        """
        filters and takes from all the items in a given list (that was read from the res file) only those with the desired parameters value
        The function filters by some parameter only if this parameter is given an input value > 0.
        E.g.: 
        If bpe == 0, the function discards bpe values, and doesn't filter out entries by their bpe values.
        If bpe == 5, the function returns only entries in which bpe == 5.      
        """
        if (trace!=None):
            list_to_filter = list (filter (lambda item : item['trace'] == trace, list_to_filter))
        if (cache_size!=None):
            list_to_filter = list (filter (lambda item : item['cache_size'] == cache_size, list_to_filter))
        if (bpe!=None):
            list_to_filter = list (filter (lambda item : item['bpe'] == bpe, list_to_filter))
        if (num_of_DSs!=None):
            list_to_filter = list (filter (lambda item : item['num_of_DSs'] == num_of_DSs, list_to_filter))
        if (Kloc!=1):
            list_to_filter = list (filter (lambda item : item['Kloc'] == Kloc, list_to_filter))
        if (missp!=None):
            list_to_filter = list (filter (lambda item : item['missp'] == missp, list_to_filter))
        if (uInterval!=None):
            list_to_filter = list (filter (lambda item : item['uInterval'] == uInterval, list_to_filter))
        if (num_of_req!=None):
            list_to_filter = list (filter (lambda item : item['num_of_req'] == num_of_req, list_to_filter))
        if (alg_mode!=None):
            list_to_filter = list (filter (lambda item : item['alg_mode'] == alg_mode, list_to_filter))    
        return list_to_filter

    def print_single_tikz_plot (self, list_of_dict, key_to_sort, addplot_str = None, add_legend_str = None, legend_entry = None):
        """
        Prints a single plot in a tikz format.
        Inputs:
        The "x" value is the one which the user asks to sort the inputs (e.g., "x" value may be the cache size, uInterval, etc).
        The "y" value is the cost for this "x". 
        list_of_dicts - a list of Python dictionaries. 
        key_to_sort - the function sorts the items by this key, e.g.: cache size, uInterval, etc.
        addplot_str - the "add plot" string to be added before each list of points (defining the plot's width, color, etc.).
        addlegend_str - the "add legend" string to be added after each list of points.
        legend_entry - the entry to be written (e.g., 'Opt', 'Alg', etc).
        """
        if (not (addplot_str == None)):
            printf (self.output_file, addplot_str)
        for dict in sorted (list_of_dict, key = lambda i: i[key_to_sort]):
            printf (self.output_file, '({:.0f}, {:.04f})' .format (dict[key_to_sort], dict['serviceCost']))
        printf (self.output_file, self.end_add_plot_str)
        if (not (add_legend_str == None)): # if the caller requested to print an "add legend" str          
            printf (self.output_file, '\t\t{}{}' .format (self.add_legend_str, legend_entry))    
            printf (self.output_file, '}\n')    
        printf (self.output_file, '\n\n')    
        
        
    def print_cache_size_plot_normalized (self):
        """
        Print a tikz plot of the service cost as a func' of the bpe
        """    
        opt_list     = sorted (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'Opt'), key = lambda i: i['cache_size']) 

        add_legend_str = None
        for uInterval in [256, 1024]:
            if (uInterval == 1024):
                add_legend_str = self.add_legend_str
            printf (self.output_file, '%% uInterval = {}\n' .format (uInterval))
            for alg_mode in ['FNOA', 'FNAA']:
                filtered_list  = self.gen_filtered_list(self.list_of_dicts, num_of_DSs = 3, Kloc = 1, missp = 100, 
                                                        alg_mode = alg_mode, uInterval = uInterval)
                for dict in filtered_list: 
    
                     dict['serviceCost'] /= self.gen_filtered_list (opt_list, cache_size = dict['cache_size'])[0]['serviceCost'] # normalize the cost w.r.t. Opt
     
                self.print_single_tikz_plot (filtered_list, key_to_sort = 'cache_size', addplot_str = self.add_plot_str_dict[alg_mode], 
                                             add_legend_str = add_legend_str,    legend_entry = self.legend_entry_dict[alg_mode]) 

       
    def print_cache_size_plot_abs (self):
        """
        Print a tikz plot of the service cost as a func' of the bpe
        """    
        filtered_list = self.gen_filtered_list (self.list_of_dicts, bpe = 14, missp = 100) # Filter only relevant from the results file  
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'Opt'), 
                                     'cache_size', addplot_str = self.add_plot_opt, 
                                     add_legend_str = self.add_legend_str, legend_entry = 'Opt') 

        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNOA', uInterval = 256), 
                                     'cache_size', addplot_str = self.add_plot_fno2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfno, uInterval = 256') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNAA', uInterval = 256), 
                                     'cache_size', addplot_str = self.add_plot_fna2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfna, uInterval = 256') 

        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNOA', uInterval = 1024), 
                                     'cache_size', addplot_str = self.add_plot_fno2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfno, uInterval = 1024') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNAA', uInterval = 1024), 
                                     'cache_size', addplot_str = self.add_plot_fna2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfna, uInterval = 1024') 
        
    def print_bpe_plot (self):
        """
        Print a tikz plot of the service cost as a func' of the bpe
        """    
        filtered_list = self.gen_filtered_list (self.list_of_dicts, cache_size = 10, missp = 100) # Filter only relevant from the results file  
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'Opt'), 
                                     'bpe', addplot_str = self.add_plot_opt, 
                                     add_legend_str = self.add_legend_str, legend_entry = 'Opt') 
       
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNOA', uInterval = 256), 
                                     'bpe', addplot_str = self.add_plot_fno1, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfno, uInterval = 256') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNAA', uInterval = 256), 
                                     'bpe', addplot_str = self.add_plot_fna1, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfna, uInterval = 256') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNOA', uInterval = 1024), 
                                     'bpe', addplot_str = self.add_plot_fno2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfno, uInterval = 1024') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNAA', uInterval = 1024), 
                                     'bpe', addplot_str = self.add_plot_fna2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfna, uInterval = 1024') 
        
    def print_uInterval_plot (self):
        """
        Print a tikz plot of the service cost as a func' of the update interval.
        The print shows Opt, FNO, and FNA
        """    
        filtered_list = self.gen_filtered_list (self.list_of_dicts, cache_size = 10, missp = 100, bpe = 14) # Filter only relevant from the results file  
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'Opt'), 
                                     'uInterval', addplot_str = self.add_plot_opt, 
                                     add_legend_str = self.add_legend_str, legend_entry = 'Opt') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNOA'), 
                                     'uInterval', addplot_str = self.add_plot_fno2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfno') 
        
        self.print_single_tikz_plot (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'FNAA'), 
                                     'uInterval', addplot_str = self.add_plot_fna2, 
                                     add_legend_str = self.add_legend_str, legend_entry = '\\pgmfna') 
                
    def print_normalized_plot (self, key_to_sort, uInterval = 0, print_add_legend = True):
        """
        Print a tikz plot of the service cost as a func' of the update interval
        The print shows FNO and FNA, both normalized w.r.t. Opt
        """    
        filtered_list = self.gen_filtered_list (self.list_of_dicts, cache_size = 10, missp = 100, bpe = 14, num_of_req = 1000) # Filter only relevant from the results file  
        opt_cost = self.gen_filtered_list(self.list_of_dicts, cache_size = 10, num_of_DSs = 3, Kloc = 1, missp = 100, alg_mode = 'Opt')[0]['serviceCost']

        if (uInterval > 0 ):
            printf (self.output_file, '%% uInterval = {}\n' .format (uInterval))
        for alg_mode in ['FNOA', 'FNAA']:
            
            filtered_list  = self.gen_filtered_list(self.list_of_dicts, uInterval = uInterval, cache_size = 10, num_of_DSs = 3, Kloc = 1, missp = 100, alg_mode = alg_mode)
            add_legend_str = self.add_legend_str if print_add_legend else None
            for dict in filtered_list: 
                dict['serviceCost'] /= opt_cost

            self.print_single_tikz_plot (filtered_list, key_to_sort = key_to_sort, addplot_str = self.add_plot_str_dict[alg_mode], 
                                         add_legend_str = add_legend_str,    legend_entry = self.legend_entry_dict[alg_mode]) 
            
                    
    def parse_file (self, input_file_name):
    
        self.input_file         = open ("../res/" + input_file_name,  "r")
        # self.output_file        = open ("../res/" + input_file_name.split(".")[0] + ".dat", "w")
        lines               = (line.rstrip() for line in self.input_file) # "lines" contains all lines in input file
        lines               = (line for line in lines if line)       # Discard blank lines
        
        for line in lines:
        
            # Discard lines with comments / verbose data
            if (line.split ("//")[0] == ""):
                continue
           
            self.parse_line(line)
            if ( not(self.dict in self.list_of_dicts)):
                self.list_of_dicts.append(self.dict)
                

        cache_size = 10 # cache size to plot, in units of [K] entries        
        uInterval  = 1000
        alg_modes = ['FNAA', 'FNOA']
        self.input_file.close

    def print_num_of_caches_plot_normalized (self):
        """
        Print a tikz plot of the service cost as a func' of the number of DSs, normalized by the cost of Opt
        """    
        opt_list = sorted (self.gen_filtered_list (self.list_of_dicts, alg_mode = 'Opt'), key = lambda i: i['num_of_DSs']) 

        add_legend_str = None
        for uInterval in [256, 1024]:
            if (uInterval == 1024):
                add_legend_str = self.add_legend_str
            printf (self.output_file, '%% uInterval = {}\n' .format (uInterval))
            for alg_mode in ['FNOA', 'FNAA']:
                filtered_list  = self.gen_filtered_list(self.list_of_dicts, Kloc = 1, missp = 100, 
                                                        alg_mode = alg_mode, uInterval = uInterval)
                for dict in filtered_list: 
    
                     dict['serviceCost'] /= self.gen_filtered_list (opt_list, num_of_DSs = dict['num_of_DSs'])[0]['serviceCost'] # normalize the cost w.r.t. Opt
     
                self.print_single_tikz_plot (filtered_list, key_to_sort = 'num_of_DSs', addplot_str = self.add_plot_str_dict[alg_mode], 
                                             add_legend_str = add_legend_str,    legend_entry = self.legend_entry_dict[alg_mode]) 


    def print_num_of_caches_plot_abs (self):
        """
        Print a tikz plot of the service cost as a func' of the number of DSs, absolute values
        """    

        add_legend_str = None
        for uInterval in [256, 1024]:
            if (uInterval == 1024):
                add_legend_str = self.add_legend_str
            printf (self.output_file, '%% uInterval = {}\n' .format (uInterval))
            for alg_mode in ['Opt', 'FNOA', 'FNAA']:
                filtered_list  = self.gen_filtered_list(self.list_of_dicts, Kloc = 1, missp = 100, 
                                                        alg_mode = alg_mode, uInterval = uInterval)
                self.print_single_tikz_plot (filtered_list, key_to_sort = 'num_of_DSs', addplot_str = self.add_plot_str_dict[alg_mode], 
                                             add_legend_str = add_legend_str,    legend_entry = self.legend_entry_dict[alg_mode]) 
       
        
       
    def plot_bars_by_missp_python (self, 
                                   mr0_th           = 0.88, 
                                   mr1_th           = 0.01, 
                                   uInterval        = None,
                                   uInterval_factor = 4, 
                                   bpe              = 14,
                                   traces           = ['wiki1', 'scarab', 'F1', 'P3'],  
                                   modes            = ['FNAA', 'SALSA1', 'SALSA2'], 
                                   cache_size       = 10):
        """
        Generate and save a bar-plot of the service cost and BW for varying modes, traces, and missp values.  
        """

        self.set_plt_params ()

        missp_vals = [10, 30, 100, 300]
        
        fig = plt.subplots(figsize =(12, 8)) # set width of bar 

        if len(traces)==2:
            mid_x_positions = [((len(modes)+1)*x+1)*BAR_WIDTH for x in range(len(traces))]
        else:
            mid_x_positions = [((len(modes)+1)*x+2)*BAR_WIDTH for x in range(len(traces))]
        plt.subplots_adjust(wspace=0.4)
        for missp in missp_vals: #range(len(missp_vals)):
            x_positions     = [((len(modes)+1)*x)*BAR_WIDTH for x in range(len(traces))]
            for mode in modes:
                mode_serviceCost = np.zeros (len(traces)) # default values for generating partial plots, before all experiments are done 
                mode_bwCost      = np.zeros (len(traces)) # default values for generating partial plots, before all experiments are done
                traces_to_print = []
                for traceIdx in range(len(traces)):
                    trace = traces[traceIdx]
                    traces_to_print.append(trace)
                    relevant_points = [item for item in self.list_of_dicts if
                                 item['trace']      == trace        and 
                                 item['cache_size'] == cache_size   and
                                 item['num_of_DSs'] == 3            and
                                 item['missp']      == missp] 
                    opt_point = [item for item in relevant_points if item['alg_mode'] =='Opt'] 
                    if (opt_point==[]):
                        MyConfig.error ('no results Opt {}.C{}K.bpe{} M{}' .format (
                                        trace, cache_size, bpe, missp, mode))
                    opt_serviceCost = opt_point[0]['serviceCost']
                    
                    # remove all points of other mcdes
                    relevant_points = [item for item in relevant_points if item['alg_mode'] == mode and item['bpe'] == bpe]
                    if uInterval!=None:
                        relevant_points = [item for item in relevant_points if item['min_uInterval'] == uInterval] 
                    if (relevant_points==[]): # no results for this settings  
                        continue
                    if mode.startswith('SALSA'):
                        relevant_points = [item for item in relevant_points if
                                           item['mr0_th'] == mr0_th and
                                           item['mr1_th'] == mr1_th and
                                           item['uInterval_factor']==uInterval_factor]     
                    point = relevant_points[0]
                    mode_serviceCost[traceIdx] = point['serviceCost'] / opt_serviceCost
                    mode_bwCost     [traceIdx] = point['bwCost']

                plt.subplot (1, 2, 1)
                plt.bar(x_positions, mode_serviceCost, color=self.colorOfMode[mode], width=BAR_WIDTH, label=self.strOfMode[mode]) 
                plt.ylabel('Normalized Service Cost', fontsize = FONT_SIZE)
                plt.xticks (mid_x_positions, traces_to_print)
                plt.legend ()
                plt.subplot (1, 2, 2)
                plt.bar(x_positions, mode_bwCost, color=self.colorOfMode[mode], width=BAR_WIDTH, label=self.strOfMode[mode]) 
                plt.ylabel('Bandwidth [bits/req.]', fontsize = FONT_SIZE)
                x_positions = [x_positions[i] + BAR_WIDTH for i in range(len(x_positions))]
                plt.xticks (mid_x_positions, traces_to_print)
                plt.legend ()
            plt.savefig ('../res/C_{}K_M{}.pdf' .format (cache_size, missp), bbox_inches='tight', dpi=100)
            plt.clf ()
            
    def plot_mr0 (self, input_file_name):
        """
        generate a plot, showing the mr0 as a func' of time (manifested by # of requests).
        Input: input_file_name - a file containing the 'mr0' values, in one line, comma-separated.
        output: input_file_name.jpg = plot of the mr0 as a func' of time.
        
        """
        for line in open ('../res/{}' .format (input_file_name),  "r"):
            splitted_line = line.split (',')
            mr0 = [float (splitted_line[i]) for i  in range(len(splitted_line)) if splitted_line[i]!='']
            mr0 = mr0[:31]
        # print (f'mr0 len={len(mr0)}')
        plt.xlim (0, 160*(len(mr0)-1))
        plt.ylim (0.8, 1.02)
        plt.plot ([160*i for i in range(len(mr0))], mr0, markersize=MARKER_SIZE, linewidth=LINE_WIDTH, color='blue')
        plt.xlabel ('Insertion Count')
        plt.ylabel (r'$\nu$')
        plt.savefig (f'../res/{input_file_name}.pdf', bbox_inches='tight', dpi=100)
        
                    
my_Res_file_parser = Res_file_parser ()
my_Res_file_parser.plot_mr0(input_file_name='P3_C16K_U1600_mr0_by_staleness_0.res')
# for res_file in ['salsa.res', 'opt.res']:  #
#     my_Res_file_parser.parse_file (res_file)
# for cache_size in [4]: #[4, 16, 64]:
#     my_Res_file_parser.plot_bars_by_missp_python (cache_size=cache_size)

