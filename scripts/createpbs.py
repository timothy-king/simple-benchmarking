#!/usr/bin/env python

import sys

job_id = sys.argv[1]
f = open(sys.argv[2], 'w')

f.write("#!/bin/bash\n")
f.write("#PBS -q s48\n")
f.write("#PBS -l nodes=1:ppn=12,walltime=04:00:00\n")
f.write("#PBS -N job_" + job_id + ".A\n")
f.write("#PBS -M kshitij@nyu.edu\n")
f.write("#PBS -m abe\n")
f.write("#PBS -e localhost:/scratch/kb1289/${PBS_JOBNAME}.err\n")
f.write("#PBS -o localhost:/scratch/kb1289/${PBS_JOBNAME}.out\n")
f.write("\n")
f.write(". /home/kb1289/.bash.d/modules\n")
f.write("\n")
f.write("cd /scratch/kb1289/test/simple-benchmarking/scripts\n")
f.write("\n")
f.write("for i in 1 2 3 4 5 6 7 8 9 10 11; do\n")
f.write("  ./runner.py " + job_id + " &\n")
f.write("  sleep 1\n")
f.write("done\n")
f.write("\n")
f.write("wait\n")
