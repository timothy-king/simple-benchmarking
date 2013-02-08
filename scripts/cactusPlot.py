#!/usr/bin/python

import MySQLdb as mdb
import sys
import os
import argparse
import string
import plot_utilities as util
import benchmarking_utilities as bu

(server, user, password, table) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Generates a cactus plot comparing several jobs.')
parser.add_argument('-j', '--jobids',type=int, nargs='+',
                    help='the ids of jobs to compare', required=True)
parser.add_argument('-p', '--path', type=str,
                    help='the path where the files will be dumped; defaults to current directory')

args = parser.parse_args()
job_ids=args.jobids
path = "" if ( args.path== None) else args.path

def generateCactusBaseName(job_ids) :
    name = "cactus";
    for job_id in job_ids :
        name += "_" + str(job_id)
    return name

   
    
con = mdb.connect(server, user, password, table);

with con:
    cur = con.cursor()
    plot_xlabel = "benchmarks solved"
    plot_ylabel = "cummulative time"

    base_name = path + generateCactusBaseName(job_ids)

    gnuplot_file_name = base_name + ".gnuplot"
    gnuplot_file = open(gnuplot_file_name, 'w')

    data_file_name = base_name + ".dat"
    data_file = open(data_file_name, 'w')
    
    pdf_file_name = base_name + ".pdf"

    util.setupPlot(gnuplot_file, plot_xlabel, plot_ylabel, "")
    util.setupPdfPlot(gnuplot_file, pdf_file_name)
    util.setupCactusPlot(gnuplot_file)

    util.startPlot(gnuplot_file)
    
    for i in range(len(job_ids)) :
        job_id = job_ids[i]
        result_i = util.getSortedResults(cur, job_id)
        util.dumpCactusToFile(data_file, util.getJobName(cur, job_id), result_i)

    for i in range(len(job_ids)) :
        util.plotOneCactus(gnuplot_file, data_file_name, i, 1, 2)
        if ( i < len(job_ids) - 1) :
            util.plotSeparator(gnuplot_file)

    data_file.close()    
    gnuplot_file.close()
                       
con.close()
