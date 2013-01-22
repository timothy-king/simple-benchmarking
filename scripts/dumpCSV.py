#!/usr/bin/python

import MySQLdb as mdb
import sys
import string

USER_FILE="../config/user"
PASSWORD_FILE="../config/password"

DELIM=','
NAString='NA'

def echoFile(fileName):
    try:
        f = open(fileName, 'r');
        contents = f.read()
        return contents.strip()
    except IOError:
        sys.exit("Could not open " + fileName+". Make sure this exists and is readable.")

def writeDelimLn(out, l):
    out.write(string.join(l ,DELIM));
    out.write('\n');

server='localhost'
user=echoFile(USER_FILE)
password=echoFile(PASSWORD_FILE)
table="benchmarking"

job_number=sys.argv[1]

outfile_name=job_number + '.csv'
outfile = open(outfile_name, 'w')

con = mdb.connect(server, user, password, table);
with con:
    cur = con.cursor()

    stat_names=[]
    stat_ids=[]
    if (len(sys.argv) == 2) :
        # use all statistics
        cur.execute("SELECT * from Stats")
        stats = cur.fetchall()
        for stat in stats:
            stat_ids.append(stat[0])
            stat_names.append(stat[1])

    else :
        # read stats from file
        statistics_file = sys.argv[2]

        infile = open(statistics_file, 'r')

        for stat_name in infile:
            stat_names.append(stat_name.strip())

        #collect the id of the statistic
        for i in range(len(stat_names)) :
            cur.execute("SELECT id FROM Stats WHERE name=%s", (stat_names[i]))
            result=cur.fetchone()
            stat_ids.append(result[0])

    headers=['JobId', 'BenchmarkId', 'RunTime', 'Memory', 'Result', 'ExitStatus'] + stat_names
    writeDelimLn(outfile, headers);


    # retrieve stats for jobs we care about
    cur.execute("SELECT id FROM JobResults WHERE job_id=%s", (job_number))
    job_result_ids = cur.fetchall()

    for job_result_id in job_result_ids :
        stat_values = []
        # for each problem in this job retrieve the stats
        stat_values.append(str(job_number))
        #outfile.write(job_number + DELIM);

        # first get the runtime information
        cur.execute("SELECT problem_id, run_time, memory, result, exit_status FROM JobResults WHERE id=%s",
                    (job_result_id[0]))

        runtime_results = cur.fetchall()
        assert len(runtime_results) == 1
        runtime_result_strings = [str(runtime_results[0][j]) for j in range(5)]
        stat_values.extend(runtime_result_strings);

        cur.execute("SELECT stat_id, stat_value FROM ResultStats WHERE job_result_id=%s", (job_result_id[0]))
        current_stats=cur.fetchall()
        # turn statistics for current problem into a map
        stat_map={}
        for i in range(len(current_stats)) :
            stat_map[current_stats[i][0]] = current_stats[i][1].strip()

        for i in range(len(stat_ids)) :
            stat_id = stat_ids[i]
            # reitrieve value of stat for current problem
            if (stat_id in stat_map) :
                stat_value = stat_map[stat_id];
            else :
                stat_value = NAString
            stat_values.append(stat_value)

        writeDelimLn(outfile,stat_values)

outfile.close()
con.close()
