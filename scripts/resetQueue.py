#!/usr/bin/env python

import MySQLdb as mdb
import sys
import os
import argparse
import subprocess
import re
import benchmarking_utilities as bu

(server, user, password, database) = bu.loadConfiguration()

con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    cur.execute("""UPDATE Queue set runner_pid=NULL;""")
    print "Reset", cur.rowcount, "rows"
con.close()
