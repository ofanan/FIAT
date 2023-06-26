#!/bin/bash

#PBS -q WD
#PBS -k eod
#PBS -e log.err
#PBS -o log.out

###Always load modules first
module load python/3/3.9.6 gcc hdf5/serial

cd $PBS_O_WORKDIR

python3 ./runner.py
