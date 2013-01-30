#!/usr/bin/python

import MySQLdb as mdb
import sys
import datetime
import argparse
import benchmarking_utilities as bu

parser = argparse.ArgumentParser(description='Summarize recent benchmarking jobs.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-n', type=int,metavar='N',
                   help='number of recent jobs', default=None)
group.add_argument('-d', '--days',type=int,metavar='D',
                   help='number of days', default=None)
group.add_argument('-H', '--hours',type=int,metavar='H',
                   help='hours since time', default=None)
group.add_argument('-s', '--since',type=str,metavar='TIME',
                   help='search since time', default=None)
group.add_argument('-l', '--list', nargs='+', type=int, default=None)
args = parser.parse_args()

recentN = args.n
hoursH = args.hours
daysD = args.days
sinceTime = args.since
listed = args.list

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
    prev = None
    if recentN != None:
        print "Selecting", recentN, "most recent jobs"
        jobs = selectKMostRecent(recentN)
    elif hoursH != None:
        prev = hoursBeforeString(hoursH)
    elif daysD != None:
        prev = daysBeforeString(daysD)
    elif sinceTime != None:
        prev = sinceTime
    elif listed != None:
        jobs = [bu.selectJob(cur,jid) for jid in listed]

    if prev != None:
        print "Selecting jobs before:", prev
        jobs = selectJobsBefore(prev)

    for j in jobs:
        bu.printJob(j)

con.close()
