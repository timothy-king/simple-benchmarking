#!/usr/bin/env python

import MySQLdb as mdb
import sys
import os
import argparse
import subprocess
import re
import time
import benchmarking_utilities as bu

(server, user, password, database) = bu.loadConfiguration()

def getQueueSize(cur):
    cur.execute("""SELECT COUNT(*) from Queue;""")
    return cur.fetchone()[0]

def printQueueSize(cur):
    out = ""
    out += "Queue has "+ str(getQueueSize(cur))+ " total elements\n"
    out += "-----------\n"
    cur.execute("""SELECT distinct(job_id) from Queue;""")
    job_ids = cur.fetchall()
    for (job_id) in job_ids:
        cur.execute("""SELECT count(*) from Queue where job_id = %s;""",
                    (job_id))
        count = cur.fetchall()[0][0]
        out += "Job "+ str(job_id[0]) +" has "+ str(count)+"\n"
    return out

def queueSize():
    con = mdb.connect(server, user, password, database);
    with con:
        cur = con.cursor()
        prevQueueSize = getQueueSize(cur)
        out = printQueueSize(cur)
    con.close()
    return prevQueueSize, out


prevQueueSize, out = queueSize()
print out
while prevQueueSize > 0:
    time.sleep(40)
    curSize, out = queueSize()
    if prevQueueSize != curSize:
        print
        print
        print out
    else:
        print "#",
    sys.stdout.flush()
    prevQueueSize = curSize

