#!/usr/bin/python

import MySQLdb as mdb
import sys
import datetime
import argparse
import benchmarking_utilities as bu

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

(server, user, password, table) = bu.loadConfiguration()

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

con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    jobs = None
    if listN > 0 :
        print "Selecting", listN, "most recent jobs"
        jobs = selectKMostRecent(listN)
    else:
        if len(sinceTime) > 0:
            prev = sinceTime
        elif hoursH > 0:
            prev = hoursBeforeString(hoursH)
        else:
            prev = daysBeforeString(daysD)
        print "Selecting jobs before:", prev
        jobs = selectJobsBefore(prev)
    for j in jobs:
        bu.printJob(j)

con.close()
