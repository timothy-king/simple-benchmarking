#!/usr/bin/python

import MySQLdb as mdb
import sys


result_id = int(sys.argv[1])
stat_file = sys.argv[2]


def isStatisticLine(line) :
    index = line.find(',')
    if (index < 0) :
        return False
    line_arr= line.split(",")
    if (len(line_arr) != 2) :
        return False
    return True

skipExactMatches = frozenset(["CVC4 suffered a segfault.\n",
                              "CVC4 interrupted by timeout.\n"])

skipPrefixes = ["Offending address is "]

def skipError(line):
    if line in skipExactMatches:
        return True
    if (any (line.startswith(x) for x in skipPrefixes)):
        return True
    print line
    return False

con = mdb.connect('localhost', 'taking', 'cluster', 'smt_cluster');
with con:
    cur = con.cursor()
     # read statistics 
    f = open(stat_file, 'r')
    for line in f:
        if (not isStatisticLine(line)) :
            if(skipError(line)):
                continue
            sys.exit(line)
            #sys.exit("Not a valid statistic. \n") 
        line_arr= line.split(",")
        stat_name=line_arr[0]
        stat_value=line_arr[1]

        cur.execute("INSERT IGNORE INTO Stats VALUES(default, %s)", (stat_name))
        # get statistic id
        cur.execute("SELECT id FROM Stats WHERE name=%s", (stat_name))
        stat_id=int(cur.fetchone()[0])
        cur.execute("INSERT INTO ResultStats VALUES(default, %s, %s, %s)", (result_id, stat_id, stat_value))
        
con.close()
