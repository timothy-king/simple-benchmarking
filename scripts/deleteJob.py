#!/usr/bin/env python

import MySQLdb as mdb
import sys
import datetime
import benchmarking_utilities as bu

job_id=int(sys.argv[1])
(server, user, password, database) = bu.loadConfiguration()

def deleteJob(cur, job_id):
    print "deleting job id", job_id
    jrids = bu.jobResultIds(cur, job_id)
    for jrid in jrids:
        bu.deleteJobResult(cur, jrid)
    bu.deleteJobIdFromQueue(cur, job_id)
    cur.execute('DELETE FROM Jobs WHERE Jobs.id = %s;', job_id)
    bu.printDeleted(int(cur.rowcount), "Jobs")
    print "deleting job id", job_id, "done"


con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    if(bu.confirmJob(cur, job_id)):
        deleteJob(cur, job_id)
    else:
        print "Confirmation failed skipping", job_id
con.close()
