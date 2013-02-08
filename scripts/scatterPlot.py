#!/usr/bin/env python

import MySQLdb as mdb
import sys
import subprocess
import argparse
import string
import benchmarking_utilities as bu
import plot_utilities as util

(server, user, password, database) = bu.loadConfiguration()

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

def generateScatterBaseName(xjob, yjob, xfield, yfield) :
    return "scatter_" + str(xjob) + "_" + xfield + "_vs_" + str(yjob) + "_" +yfield
    
con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    
    plot_xlabel = util.getJobName(cur, xjob)
    plot_ylabel = util.getJobName(cur, yjob)
    plot_title = plot_xlabel + " vs " + plot_ylabel
    
    base_name = path + generateScatterBaseName(xjob, yjob, xfield, yfield)

    gnuplot_file_name = base_name + ".gnuplot"
    gnuplot_file = open(gnuplot_file_name, 'w')

    data_file_name = base_name + ".dat"
    data_file = open(data_file_name, 'w')
    
    pdf_file_name = base_name + ".pdf"

    util.setupPlot(gnuplot_file, plot_xlabel, plot_ylabel, plot_title)
    util.setupPdfPlot(gnuplot_file, pdf_file_name)

    util.startPlot(gnuplot_file)

    results = util.selectAllResult(cur, xjob, yjob, xfield, yfield)
    families = util.groupByFamilies(results)

    for family in families:
        family_results = families[family]
        util.dumpFamilyToFile(data_file, family, family_results)

    for i in range(len(families)):
        util.plotOneScatter(gnuplot_file, data_file_name, i, 2, 3)
        util.plotSeparator(gnuplot_file)

    util.plotDiagonal(gnuplot_file)
    data_file.close()    
    gnuplot_file.close()

con.close()
