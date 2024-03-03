#!/bin/bash

#PBS -q WD
#PBS -k eod
#PBS -e log.err
#PBS -o log.out
#PBS -l ncpus=36

### #PBS -l walltime=240:00:00

###Always load modules first
module load python/3/3.9.6 gcc hdf5/serial

cd $PBS_O_WORKDIR

python3 ./runner.py
