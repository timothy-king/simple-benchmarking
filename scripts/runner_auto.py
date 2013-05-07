#!/usr/bin/env python

import MySQLdb as mdb
import sys
import os
import argparse
import subprocess
import benchmarking_utilities as bu
import time

start_time = time.time()

os.chdir(sys.path[0])     # change to directory where script is...

(server, user, password, database) = bu.loadConfiguration()
log_path = bu.loadLogPath()

parser = argparse.ArgumentParser(description='Run a job.')
parser.add_argument('-a', '--auto', action="store_true",
		    help='automatically find a job and run on it')
parser.add_argument('-t', '--walltime', type=int, required=True,
		    help='how many seconds should the runner take maximum')
args = parser.parse_args()

auto = args.auto
runner_time_limit = args.walltime



# Grab globals for job
def getJob():
    con = mdb.connect(server, user, password, database);
    with con:
        cur = con.cursor()
        cur.execute("""SELECT job_id FROM Queue WHERE runner_pid IS NULL ORDER BY RAND() LIMIT 1""")
        res = cur.fetchall()

    if len(res) == 0:
        return None

    assert len(res) == 1

    (job_id, ) = res[0]
    return job_id

if auto == True:

    lastSuccess = True
    while lastSuccess:
        job_id = getJob()
        if job_id == None:
            break

        elapsed_time = time.time() - start_time
        remaining_time = int(runner_time_limit - elapsed_time)

        if remaining_time <= 0:
            sys.exit(1)

        ret_value = subprocess.call(['./runner.py', '-t', str(remaining_time), str(job_id) ])
        lastSuccess = (ret_value == 0)
    else:
        print("Exiting with return value %d." % ret_value)
        sys.exit(ret_value)

else:
    print "Run with -a or --auto option"
