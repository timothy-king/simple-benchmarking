#!/usr/bin/python

import MySQLdb as mdb
import sys
import string
import datetime

USER_FILE="../config/user"
PASSWORD_FILE="../config/password"


def echoFile(fileName):
    try:
        f = open(fileName, 'r');
        contents = f.read()
        return contents.strip()
    except IOError:
        sys.exit("Could not open " + fileName+". Make sure this exists and is readable.")

def writeDelimLn(out, l):
    out.write(string.join(l ,DELIM));
    out.write('\n');

server='localhost'
user=echoFile(USER_FILE)
password=echoFile(PASSWORD_FILE)
table="benchmarking"


def printJob(j):
    job_id = j[0]
    name = j[1]
    description = j[2]
    time_limit = j[3]
    memory_limit = j[4]
    problem_set_id = j[5]
    arguments = j[6]
    timestamp = j[7]
    print job_id, name, ";", description
    print "  ", arguments
    print "  ", timestamp.isoformat(), problem_set_id, time_limit, problem_set_id

def getResultID(cur, job_id, problem_id):
    cur.execute("""select id from JobResults
                   where job_id=%s and problem_id=%s;""",
                (job_id, problem_id))
    res = cur.fetchall()
    assert len(res) == 1, "No JobResult for this job id and problem id"
    assert len(res[0]) == 1
    return res[0][0]

def confirm(cur, job_id, problem_id, job_result_id):
    cur.execute('SELECT * from Jobs where Jobs.id = %s;', job_id)
    jobs = cur.fetchall()
    assert(len(jobs)==1)
    assert(jobs[0][0] == job_id)
    printJob(jobs[0])

    cur.execute('SELECT path from Problems where id = %s;', problem_id)
    problem_path = (cur.fetchall())[0][0]
    print "Problem:", problem_path
    print "job_result_id:", job_result_id
    cand_id = input("Reenter job_result_id to confirm:")
    return cand_id == job_result_id

def deleteJobResult(cur, jrid):
    print "\t","deleting job result id", jrid,
    cur.execute('DELETE FROM ResultStats WHERE ResultStats.job_result_id = %s;', jrid)
    cur.execute('DELETE FROM JobResults WHERE JobResults.id = %s;', jrid)
    print "done"

def addBackToQueue(cur, job_id, problem_id):
    cur.execute("insert into Queue Values (default, %s, %s, default);",
                (job_id, problem_id))
    print cur.fetchall()

job_id=int(sys.argv[1])
problem_id=int(sys.argv[2])

con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    job_result_id = getResultID(cur, job_id, problem_id)
    if(confirm(cur, job_id, problem_id, job_result_id)):
        deleteJobResult(cur, job_result_id)
        addBackToQueue(cur, job_id, problem_id)
    else:
        print "Confirmation failed skipping", job_result_id

con.close()
