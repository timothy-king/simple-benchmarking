#!/usr/bin/python

import MySQLdb as mdb
import sys
import os
import argparse
import string
import plot_utilities as pu
import benchmarking_utilities as bu

(server, user, password, table) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Generates a scatter plot comparing two jobs.')
parser.add_argument('-xj', '--xjob',type=int,
                    help='the job to be plotted on the x axis', required=True)
parser.add_argument('-yj', '--yjob',type=int,
                    help='the job to be plotted on the y axis', required=True)
parser.add_argument('-d', '--data',type=str,
                    help='file where to dump the temporary .dat', required=True)
parser.add_argument('-j', '--jsmap',type=str,
                    help='file where to dump java script file storing a map of results', required=True)


args = parser.parse_args()
xjob=args.xjob
yjob=args.yjob
data_file = args.data
js_map_file = args.jsmap
xfield = "run_time"
yfield = "run_time"

def getResults(cur, xjob, yjob) :
    cur.execute("select Problems.path, Aruntime, Bruntime from (select A.problem_id, A.run_time as Aruntime, B.run_time as Bruntime from ( select * from JobResults where job_id=%s) as A join (select * from JobResults where job_id=%s) as B on A.problem_id = B.problem_id) as C join Problems on Problems.id = C.problem_id;", (xjob, yjob))
    res = cur.fetchall()
    assert (res != None)
    return res; 

def dumpResultsToFiles(outfile, jsmap_file, family, family_results) :
    outfile.write(family +" " + family + " " + family+ "\n")
    for result in family_results:
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        outfile.write(result[0] + " " + str(xvalue) + " " + str(yvalue) + "\n")
        jsmap_file.write("benchmark_paths.push(\"" + path + "\"); ");
        jsmap_file.write("result_x_values.push(" + str(xvalue) + "); ");
        jsmap_file.write("result_y_values.push(" + str(yvalue) + "); ");
    outfile.write("\n\n")


def generatePlots(data_name, jsmap_name, families) :
    data_file = open(data_name, 'w')
    jsmap_file = open(jsmap_name, 'w')
    jsmap_file.write("var benchmark_paths = new Array(); \n")
    jsmap_file.write("var result_x_values = new Array(); \n")
    jsmap_file.write("var result_y_values = new Array(); \n")
    sys.stdout.write('plot ')
    i = 0
    for family in families:
        family_results = families[family]
        dumpResultsToFiles(data_file, jsmap_file, family, family_results)
        sys.stdout.write("\"< cat "+data_name+"\" index " + str(i) +" using 2:3 with points pt 9 pointsize 1 linecolor " + str(i) + ", ")
        i = i + 1
    sys.stdout.write("x with line linecolor rgb \"gray\" \n")
    data_file.close()
    jsmap_file.close()

def setupGnuPlot(title, xlabel, ylabel) :
    sys.stdout.write("set autoscale\n")
    sys.stdout.write("set title \"" + title + "\"\n")
    sys.stdout.write("set xlabel \"" + xlabel + "\"\n")
    sys.stdout.write("set ylabel \"" + ylabel + "\"\n")
    sys.stdout.write("set xtic auto\n")
    sys.stdout.write("set ytic auto\n")
    sys.stdout.write("set terminal canvas size 800, 600 name \"gnuplot_canvas\"\n")
    sys.stdout.write("set key outside autotitle columnheader\n")
    
con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    plot_title = pu.getJobName(cur, xjob) + " vs " + pu.getJobName(cur, yjob)
    plot_xlabel = "time " + pu.getJobName(cur, xjob)
    plot_ylabel = "time " + pu.getJobName(cur, yjob)

    results = getResults(cur, xjob, yjob)
    families = pu.groupByFamilies(results)
    setupGnuPlot(plot_title, plot_xlabel, plot_ylabel)
    generatePlots(data_file, js_map_file, families)
con.close()
