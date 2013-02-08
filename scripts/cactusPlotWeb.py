#!/usr/bin/python
import cStringIO
import MySQLdb as mdb
import argparse
import string
import plot_utilities as util
import benchmarking_utilities as bu

(server, user, password, table) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Generates a cactus plot comparing several jobs.')
parser.add_argument('-j', '--jobids',type=int, nargs='+',
                    help='the ids of jobs to compare', required=True)
parser.add_argument('-f', '--file', type=str,
                    help='the file where to dump the .dat file.', required=True)

args = parser.parse_args()
job_ids=args.jobids
data_file_name = args.file

    
con = mdb.connect(server, user, password, table);

with con:
    cur = con.cursor()
    plot_xlabel = "benchmarks solved"
    plot_ylabel = "cummulative time"

    gnuplot_command = cStringIO.StringIO()

    data_file = open(data_file_name, 'w')
    util.setupPlot(gnuplot_command, plot_xlabel, plot_ylabel, "")
    util.setupCanvasPlot(gnuplot_command, "gnuplot_canvas")
    util.setupCactusPlot(gnuplot_command)

    util.startPlot(gnuplot_command)
    
    for i in range(len(job_ids)) :
        job_id = job_ids[i]
        result_i = util.getSortedResults(cur, job_id)
        util.dumpCactusToFile(data_file, util.getJobName(cur, job_id), result_i)

    for i in range(len(job_ids)) :
        util.plotOneCactus(gnuplot_command, data_file_name, i, 1, 2)
        if ( i < len(job_ids) - 1) :
            util.plotSeparator(gnuplot_command)

    data_file.close()
    val =  gnuplot_command.getvalue()
    print val
                       
con.close()
