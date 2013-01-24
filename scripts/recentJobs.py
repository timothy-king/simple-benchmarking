#!/usr/bin/python

import MySQLdb as mdb
import sys
import string
import datetime
import argparse


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
    print "  ", timestamp.isoformat(), problem_set_id,
    print time_limit, memory_limit

def daysBeforeString(day_count):
    today = datetime.date.today()
    day_count = datetime.timedelta(days=day_count)
    yesterday = today - day_count
    return yesterday.strftime("%Y-%m-%d")

def hoursBeforeString(h_count):
    today = datetime.date.today()
    hour_count = datetime.timedelta(hours=h_count)
    diff = today - hour_count
    return diff.strftime("%Y-%m-%d %H:%M")

def selectJobsBefore(s):
    cur.execute('SELECT * from Jobs where Jobs.timestamp >= %s;', s)
    return cur.fetchall()

def selectKMostRecent(k):
    cur.execute('SELECT * from Jobs order by Jobs.timestamp DESC limit %s;', k)
    return cur.fetchall()

parser = argparse.ArgumentParser(description='Summarize recent benchmarking jobs.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-l', '--list',type=int,metavar='N',
                   help='number of recent jobs', default=0)
group.add_argument('-d', '--days',type=int,metavar='D',
                   help='number of days', default=1)
group.add_argument('-H', '--hours',type=int,metavar='H',
                   help='hours since time', default=0)
group.add_argument('-s', '--since',type=str,metavar='TIME',
                   help='search since time', default="")
args = parser.parse_args()

listN = args.list
hoursH = args.hours
daysD = args.days
sinceTime = args.since


con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    jobs = None
    if listN > 0 :
        jobs = selectKMostRecent(listN)
    else:
        if len(sinceTime) > 0:
            prev = sinceTime
        elif hoursH > 0:
            prev = hoursBeforeString(hoursH)
        else:
            prev = daysBeforeString(daysD)
        jobs = selectJobsBefore(prev)
    for j in jobs:
        printJob(j)

con.close()
