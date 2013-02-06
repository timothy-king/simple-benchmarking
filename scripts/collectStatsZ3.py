#!/usr/bin/env python

import MySQLdb as mdb
import sys


result_id = int(sys.argv[1])
stat_file = sys.argv[2]
server = sys.argv[3]
user = sys.argv[4]
password = sys.argv[5]
database = sys.argv[6]

def isStatisticLine(line) :
    if (not (any (line.startswith(x) for x in ["(:", " :"]))) :
        return False;
    line_arr = filter(None, (line.strip("()\n")).split(" "))
    if (len(line_arr) != 2) :
        return False
    return True

# add known error messages
skipExactMatches = frozenset(["sat\n", "unsat\n", "unknown\n"])

skipPrefixes = ["Offending address is "]

def skipError(line):
    if line in skipExactMatches:
        return True
    if (any (line.startswith(x) for x in skipPrefixes)):
        return True

    return False

con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
     # read statistics
    f = open(stat_file, 'r')
    for line in f:
        if (not isStatisticLine(line)) :
            if(skipError(line)):
                continue
            sys.exit(line)
            
        line_arr= filter(None, (line.strip("()\n")).split(" "))
        stat_name="z3" + line_arr[0]
        stat_value=line_arr[1]

        cur.execute("INSERT IGNORE INTO Stats VALUES(default, %s)", (stat_name))
        # get statistic id
        cur.execute("SELECT id FROM Stats WHERE name=%s", (stat_name))
        stat_id=int(cur.fetchone()[0])
        cur.execute("INSERT INTO ResultStats VALUES(default, %s, %s, %s)", (result_id, stat_id, stat_value))

con.close()
