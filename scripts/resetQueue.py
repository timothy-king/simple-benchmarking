#!/usr/bin/python

import MySQLdb as mdb
import sys
import os
import argparse
import subprocess
import re

USER_FILE="../config/user"
PASSWORD_FILE="../config/password"
LOG_PATH_FILE="../config/logpath"

RUN_LIM="../runlim-sigxcpu/runlim"

def echoFile(fileName):
    try:
        f = open(fileName, 'r');
        contents = f.read()
        return contents.strip()
    except IOError:
        sys.exit("Could not open " + fileName+". Make sure this exists and is readable.")

server='localhost'
user=echoFile(USER_FILE)
password=echoFile(PASSWORD_FILE)
log_path=echoFile(LOG_PATH_FILE)
table="benchmarking"

con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    cur.execute("""UPDATE Queue set runner_pid=NULL;""")
    print "Reset", cur.rowcount, "rows"
con.close()
