#!/usr/bin/python

import MySQLdb as mdb
import sys
import string
import datetime
import benchmarking_utilities as bu


job_id=int(sys.argv[1])
problem_id=int(sys.argv[2])
(server, user, password, table) = bu.loadConfiguration()

def getResultID(cur, job_id, problem_id):
    cur.execute("""select id from JobResults
                   where job_id=%s and problem_id=%s;""",
                (job_id, problem_id))
    res = cur.fetchall()
    assert len(res) == 1, "No JobResult for this job id and problem id"
    assert len(res[0]) == 1
    return res[0][0]


def addBackToQueue(cur, job_id, problem_id):
    cur.execute("insert into Queue Values (default, %s, %s, default);",
                (job_id, problem_id))
    print cur.fetchall()


con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    job_result_id = getResultID(cur, job_id, problem_id)
    if(bu.confirmJobResult(cur, job_id, problem_id, job_result_id)):
        bu.deleteJobResult(cur, job_result_id)
        addBackToQueue(cur, job_id, problem_id)
    else:
        print "Confirmation failed skipping", job_result_id

con.close()
