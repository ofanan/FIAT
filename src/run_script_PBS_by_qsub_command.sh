#!/bin/bash

########################################################################################
# General note:
#
# Servers:
# cn170 nodes have 2 sockets with 18 cores each. total of 36 cores per node.
# cn560 nodes have 4 sockets with 18 cores each. total of 72 cores per node.
# rtx600 nodes have 2 sockets with 20 cores and 8 GPUs each. total of 40 cores per node.
# tesla node has 2 sockets with 20 corse and 8 GPUs each. total of 40 cores per node.
#
# Queues:
# RGB - executes on cn560 nodes. max wall time 24h. max nodes: 10.
# WD - executes on cn170 nodes. max wall time 72h. max nodes: 44.
# rtx - executes on rtx600 nodes. max wall time 24h. max nodes: 3. max gpus: 24.
# tesla executes on tesla node. max wall time 24h. max nodes: 1. max gpus: 8.
#
# Your select + queue querry should match the resourcers or you'll get an error.
#
# Often used PBS commands (outside of the pbs script):
#
# qsub <script> - sumbits the job.
# qstat - list of active jobs
# qdel <job id> - deletes the job from the queue
#######################################################################################

# Uncomment the wanted lines.
# Lines starting with #PBS are actual PBS commands.
# #PBS - valid PBS command.
# ###PBS - commented PBS command.

#PBS -N ofanan_job_name

# cpu parallel select (requires MPI)
###PBS -l select=<x>:ncpus=<y>:mpiprocs=<y>

# gpu parallel select
###PBS -l select=<x>:ncpus=<y>:mpiprocs=<y>:ngpus=<z>


### Queue
#PBS -q WD

### job logs
#PBS -k eod
#PBS -e log.err
#PBS -o log.out

### Mail
###PBS -m eb
###PBS -M <mail>

###Always load modules first
module load python/3/3.9.6 gcc hdf5/serial

cd $PBS_O_WORKDIR

### commands
### mpirun hello

python3 ./runner.py