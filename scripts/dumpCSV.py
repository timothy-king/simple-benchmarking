#!/usr/bin/env python

import MySQLdb as mdb
import sys
import argparse
import string
import benchmarking_utilities as bu

DELIM=','
NAString='NA'


(server, user, password, database) = bu.loadConfiguration()

parser = argparse.ArgumentParser(description='Prints a CSV file for a job.')
parser.add_argument('jobids',type=int,nargs='+',
                    help='list of ids of the jobs to print')
parser.add_argument('-s','--statsfile',type=str,default=None,
                    help='file containing statistics to print')
args = parser.parse_args()
statistics_file=args.statsfile
job_ids= args.jobids

def writeDelimLn(out, l):
    out.write(string.join(l ,DELIM));
    out.write('\n');

def selectAllStats(cur):
    cur.execute("SELECT id,name from Stats;")
    res = cur.fetchall()
    stat_ids = [row[0] for row in res]
    stat_names = [row[1] for row in res]
    return stat_ids, stat_names

def selectStatIdsFromFile(cur, statistics_file):
    infile = open(statistics_file, 'r')
    stat_names = [stat_name.strip() for stat_name in infile]
    infile.close()

    #collect the id of the statistic
    stat_ids = []
    for name in stat_names:
        name = stat_names[i]
        cur.execute("SELECT id FROM Stats WHERE name=%s;", (name))
        result=cur.fetchone()
        stat_ids.append(result[0])
    return stat_ids, stat_names

def CSVHeaders(stat_names):
    STATS_IN_JOB_RESULT=['JobId', 'BenchmarkId', 'RunTime', 'Memory',
                         'Result', 'ExitStatus', 'BenchmarkPath'];
    return STATS_IN_JOB_RESULT + stat_names

def statValuesForCSV(cur, job_number, job_result_id, stat_ids):
    stat_values = []
    # for each problem in this job retrieve the stats
    stat_values.append(str(job_number))

    # first get the runtime information
    cur.execute("""SELECT problem_id, run_time, memory, result, exit_status
                FROM JobResults WHERE id=%s;""",
                (job_result_id))

    runtime_results = cur.fetchall()
    assert len(runtime_results) == 1
    assert len(runtime_results[0]) == 5
    problem_id =runtime_results[0][0]
    runtime_result_strings = [str(runtime_results[0][j]) for j in range(5)]
    runtime_result_strings.append(bu.getProblemPath(cur, problem_id))
    stat_values.extend(runtime_result_strings);

    cur.execute("""SELECT stat_id, stat_value
                FROM ResultStats WHERE job_result_id=%s""",
                (job_result_id))
    current_stats=cur.fetchall()
    # turn statistics for current problem into a map
    stat_map={}
    for i in range(len(current_stats)) :
        stat_map[current_stats[i][0]] = current_stats[i][1].strip()

    for stat_id in stat_ids:
        # reitrieve value of stat for current problem
        if (stat_id in stat_map) :
            stat_value = stat_map[stat_id];
        else :
            stat_value = NAString
        stat_values.append(stat_value)
    return stat_values

def dumpCSVForJob(cur, job_number, stat_ids, stat_names):
    job_result_ids = bu.jobResultIds(cur, job_number)
    stats_for_job_results = []
    for job_result_id in job_result_ids :
        stat_values = statValuesForCSV(cur, job_number, job_result_id, stat_ids)
        stats_for_job_results.append( stat_values)

    #Sort by problem_id
    stats_for_job_results.sort(cmp = lambda x,y:cmp(x[1],y[1]))

    outfile_name=str(job_number) + '.csv'
    outfile = open(outfile_name, 'w')
    writeDelimLn(outfile, CSVHeaders(stat_names));
    for stat_values in stats_for_job_results:
        writeDelimLn(outfile, stat_values)
    outfile.close()


con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()

    #select stats
    stat_ids, stat_names = None, None
    if statistics_file == None:
        stat_ids,stat_names = selectAllStats(cur)
    else :
        stat_ids,stat_names = selectStatsFromFile(cur, statistics_file)
    assert stat_ids != None
    assert stat_names != None

    for job_id in job_ids:
        print "Processing", job_id,
        dumpCSVForJob(cur, job_id, stat_ids, stat_names)
        print "[done]"
con.close()
