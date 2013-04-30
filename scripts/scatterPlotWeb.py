#!/usr/bin/env python

import MySQLdb as mdb
import cStringIO
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
parser.add_argument('-d', '--datafile', type=str,
                    help='the temporary file where the data will be dumped', required=True)
parser.add_argument('-f', '--family', type=str,
                    help='select only this family when plotting', required=False) 
parser.add_argument('-j', '--javascript', type=str,
                    help='the temporary javascript file where array for benchmark names will be dumped', required=True)

args = parser.parse_args()
xjob=args.xjob
yjob=args.yjob
input_family = args.family

data_file_name = args.datafile
javascript_file_name = args.javascript

def filterUnknowns(results_and_answers) :
    filtered_results = []
    for result in results_and_answers :
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        res1 = result[3]
        res2 = result[4]
        if (res1 != "unknown" or res2 != "unknown") :
            filtered_results.append((path, xvalue, yvalue))
    return filtered_results
    
con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    
    plot_xlabel = util.getJobName(cur, xjob) + " ("+ str(xjob) + ")"
    plot_ylabel = util.getJobName(cur, yjob) + " ("+ str(yjob) + ")"
    plot_title = plot_xlabel + " vs " + plot_ylabel
    
    data_file = open(data_file_name, 'w')
    javascript_file = open(javascript_file_name, 'w')
    gnuplot_command = cStringIO.StringIO()
    
    util.setupPlot(gnuplot_command, plot_xlabel, plot_ylabel, plot_title)
    util.setupCanvasPlot(gnuplot_command, "gnuplot_canvas")

    util.startPlot(gnuplot_command)

    results_and_answers = util.getRunTimesAndAnswer(cur, xjob, yjob)
    results = filterUnknowns(results_and_answers)
    families = util.groupByFamilies(results)
    if input_family == None or input_family == "":
	run_over_families = families
    else:
	if input_family[0] == '-':
 		input_family = input_family[1:]
		exclude_families = input_family.split(',')
		run_over_families = [item for item in families if item not in exclude_families]
        else:
	        run_over_families = input_family.split(',')
    
    util.declareJavaScriptArrays(javascript_file);
    for family in run_over_families:
        family_results = families[family]
        util.dumpFamilyToFile(data_file, family, family_results)
        util.dumpJavaScriptArray(javascript_file, family_results)
        
    for i in range(len(families)):
        util.plotOneScatter(gnuplot_command, data_file_name, i, 2, 3)
        util.plotSeparator(gnuplot_command)
    util.plotDiagonal(gnuplot_command)
    data_file.close()    
    javascript_file.close()
    print gnuplot_command.getvalue()
    gnuplot_command.close()

con.close()
