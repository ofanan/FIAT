#!/bin/bash

PBS -q WD

###Always load modules first
module load python/3/3.9.6 gcc hdf5/serial

cd $PBS_O_WORKDIR

python3 ./runner.py
