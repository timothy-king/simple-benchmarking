#!/usr/bin/python

import MySQLdb as mdb
import sys
import subprocess
import argparse
import string
import benchmarking_utilities as bu
import plot_utilities as pu

(server, user, password, table) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Generates a scatter plot comparing two jobs.')
parser.add_argument('-xj', '--xjob',type=int,
                    help='the job to be plotted on the x axis', required=True)
parser.add_argument('-yj', '--yjob',type=int,
                    help='the job to be plotted on the y axis', required=True)
parser.add_argument('-xf', '--xfield', type=str,
                    help='the value for x job; can either be a statistic or run_time/memory.', required=True)
parser.add_argument('-yf', '--yfield', type=str,
                    help='the value for y job; can either be a statistic or run_time/memory.', required=True)
parser.add_argument('-l', '--logarithmic', help='use if you want a logarithmic scale',
                   action="store_true")
parser.add_argument('-p', '--path', type=str,
                    help='the path where the files will be dumped; defaults to current directory')

args = parser.parse_args()
xjob=args.xjob
yjob=args.yjob
xfield=args.xfield
yfield=args.yfield
path = "" if args.path== None else args.path
path = pu.convertToRelativePath(path)
logarithmic_scale = args.logarithmic

def setupGnuPlot(outfile, title, xlabel, ylabel) :
    script = open(outfile + ".gnuplot", 'w+')

    script.write("set autoscale\n")
    if (logarithmic_scale) :
        script.write("set logscale xy\n")
        
    script.write("set title \"" + title + "\"\n")
    script.write("set xlabel \"" + xlabel + "\"\n")
    script.write("set ylabel \"" + ylabel + "\"\n")
    script.write("set xtic auto\n")
    script.write("set ytic auto\n")
    script.write("set terminal pdf size 6, 4.5 \n")
    script.write("set key outside\n")
    script.write("set output \"" + plot_output + "\"\n")
    script.write("set size 1, 1\n")
    
con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()
    
    xjob_name = pu.getJobName(cur, xjob)
    yjob_name = pu.getJobName(cur, yjob)
    outfile = path + str(xjob) + '-' + xfield + '_vs_' + str(yjob) + '-' + yfield;
    plot_title = xjob_name + " vs " + yjob_name
    plot_xlabel = xfield + "(" + xjob_name + ")" 
    plot_ylabel = yfield + "(" + yjob_name + ")" 
    plot_output = outfile + ".pdf"
    print outfile
    results = pu.selectAllResult(cur, xjob, yjob, xfield, yfield)
    families = pu.groupByFamilies(results)
    setupGnuPlot(outfile, plot_title, plot_xlabel, plot_ylabel)
    pu.generatePlots(outfile, families)
    exit_status = subprocess.call(["gnuplot",  outfile + ".gnuplot"])
    if exit_status != 0 :
        print "Error in generating plot."
    else :
        print "Plot generated: " + plot_output
con.close()
