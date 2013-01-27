#!/usr/bin/python

import MySQLdb as mdb
import sys
import datetime
import argparse
import benchmarking_utilities as bu

parser = argparse.ArgumentParser(description='Renames a job in the database.')
parser.add_argument('jobid',type=int,
                   help='id of the job to rename', default=0)
parser.add_argument('-d', '--description',type=str,
                   help='change the description of the job', default="")
parser.add_argument('-n', '--name',type=str,
                   help='set the name of the job', default="")
parser.add_argument('-b', '--binary',type=str,
                   help='set the binary_path of the job', default="")
args = parser.parse_args()

job_id = args.jobid
description = args.description
name = args.name
binary_path = args.binary

(server, user, password, table) = bu.loadConfiguration()

def setDescription(cur, job_id, description):
    cur.execute("""UPDATE Jobs
                   SET description=%s
                   WHERE Jobs.id = %s;""",
                (description, job_id))

def setName(cur, job_id, name):
    cur.execute("""UPDATE Jobs
                   SET name=%s
                   WHERE Jobs.id = %s;""",
                (name, job_id))

def setBinaryPath(cur, job_id, name):
    cur.execute("""UPDATE Jobs
                   SET binary_path=%s
                   WHERE Jobs.id = %s;""",
                (name, job_id))

con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    if description == "" and name == "" and binary_path == "":
        print "Must enter either a name or a description"
    elif(bu.confirmJob(cur, job_id)):
        if description != "":
            setDescription(cur, job_id, description)
        if name != "":
            setName(cur, job_id, name)
        if binary_path != "":
            setBinaryPath(cur, job_id, binary_path)
        print "Now: ",
        bu.printJobWithId(cur, job_id)
    else:
        print "Confirmation failed skipping", job_id

con.close()
