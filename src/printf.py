"""
An accessory function for format-printing to a file.
"""
from __future__ import print_function

def printf(output_file, str, *args):
    print(str % args, end='', file = output_file, flush = True)

def printar (output_file, ar):
    """
    Format-print the input array ar to a given output file.
    The array is printed without commas or newlined inside, and with a newline in the end.
    E.g.: 
    [1 2 3]
    
    """
    ar=np.array(ar)
    printf (output_file, '{}\n' .format(str(ar).replace('\n', '')))

