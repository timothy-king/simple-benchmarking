#!/usr/bin/env python

import MySQLdb as mdb
import sys
import argparse
import string
import benchmarking_utilities as bu

DELIM=','
NAString='NA'


(server, user, password, database) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Creates a problem set consisting of the benchmarks in the input file.')
parser.add_argument('-p','--problemset',type=int,default=None,
                    help='Problem set we are adding benchmarks to.')
parser.add_argument('-f','--file',type=str,default=None,
                    help='file containing the benchmark paths to add')
args = parser.parse_args()
bench_file=args.file
problem_set= args.problemset

def selectBenchmarksFromFile(cur, file):
    infile = open(file, 'r')
    bench_names = [bench_path.strip() for bench_path in infile]
    infile.close()

    #collect the id of the benchmarks
    bench_ids = []
    bench_paths = []
    for path in bench_names:
        print path

        cur.execute("SELECT id, path FROM Problems WHERE path like %s;", ('%'+path+'%'))
        result=cur.fetchone()
        bench_ids.append(result[0])
        bench_paths.append(result[1])
        
    return bench_ids, bench_paths

def addBenchmarksToProblemSet(cur, pb_set, bench_ids, bench_paths):
    for i in range(len(bench_ids)):
        bench_id = bench_ids[i]
        bench_path = bench_paths[i]
        print "Adding to problem set ", pb_set, " benchmark ", bench_path
        cur.execute("INSERT INTO ProblemSetToProblem VALUES(DEFAULT, %s, %s);", (pb_set, bench_id))

con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()

    #select benchmarks
    benchmark_ids, benchmark_paths = None, None
    benchmark_ids, benchmark_paths = selectBenchmarksFromFile(cur, bench_file)
    assert benchmark_ids != None
    assert benchmark_paths != None
    addBenchmarksToProblemSet(cur, problem_set, benchmark_ids, benchmark_paths); 
con.close()
