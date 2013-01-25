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

def confirm(cur, job_id):
    cur.execute('SELECT * from Jobs where Jobs.id = %s;', job_id)
    jobs = cur.fetchall()
    assert(len(jobs)==1)
    assert(jobs[0][0] == job_id)
    printJob(jobs[0])
    cand_id = input("Reenter id to confirm:")
    return cand_id == jobs[0][0]

def jobResultIds(cur, job_id):
    cur.execute('SELECT JobResults.id from JobResults where JobResults.job_id = %s;', job_id)
    jobsQueury = cur.fetchall()
    return [j[0] for j in jobsQueury]


def deleteJobResult(cur, jrid):
    print "\t","deleting job result id", jrid,
    cur.execute('DELETE FROM ResultStats WHERE ResultStats.job_result_id = %s;', jrid)
    cur.execute('DELETE FROM JobResults WHERE JobResults.id = %s;', jrid)
    print "done"

def deleteJob(cur, job_id):
    print "deleting job id", job_id
    jrids = jobResultIds(cur, job_id)
    for jrid in jrids:
        deleteJobResult(cur, jrid)
    cur.execute('DELETE FROM Jobs WHERE Jobs.id = %s;', job_id)
    deleteQueue(cur, job_id)
    print "deleting job id", job_id, "done"

def deleteQueue(cur, job_id):
    cur.execute('DELETE FROM Queue WHERE Queue.job_id = %s;', job_id)
    print "deleting from Queue done"
    

job_id=int(sys.argv[1])


con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    if(confirm(cur, job_id)):
        deleteJob(cur, job_id)
    else:
        print "Confirmation failed skipping", job_id

con.close()
