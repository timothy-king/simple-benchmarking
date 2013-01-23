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

con = mdb.connect(server, user, password, table);
with con:
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    yesterday = today - one_day
    yesterdayStr = yesterday.strftime("%Y-%m-%d")

    cur = con.cursor()
    cur.execute('SELECT * from Jobs where Jobs.timestamp >= %s;', yesterdayStr)
    jobs = cur.fetchall()
    for j in jobs:
        printJob(j)

con.close()
