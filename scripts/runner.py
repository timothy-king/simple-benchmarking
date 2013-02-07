#!/usr/bin/env python

import MySQLdb as mdb
import sys
import os
import argparse
import subprocess
import re
import benchmarking_utilities as bu
import platform, hashlib

RUN_LIM="../runlim-sigxcpu/runlim"

(server, user, password, database) = bu.loadConfiguration()
log_path = bu.loadLogPath()

parser = argparse.ArgumentParser(description='Run a job.')
parser.add_argument('JobID', type=int, help='id of the job you want to work on')
parser.add_argument('-v', '--verbosity', type=int,
                    help='how verbose the script should be', default=0)
args = parser.parse_args()

job_id = args.JobID
verbosity = args.verbosity

# PID : combination of both system name and current process ID
pid = os.getpid()
pid += (int(hashlib.md5(platform.node()).hexdigest(), 16) % 10000) * 100000


def storeProblemResult(problem_id, run_time, memory, result, exit_status):
    problem_result_id=None
    con = mdb.connect(server, user, password, database);
    with con:
        cur = con.cursor()
        cur.execute("""insert into JobResults
                    VALUES(default, %s, %s, %s, %s, %s, %s);""",
                    (job_id, problem_id, run_time, memory, result, exit_status))
        cur.execute("""select id from JobResults
                       where job_id=%s and problem_id=%s;""",
                    (job_id, problem_id));
        probResults = cur.fetchall()
        assert len(probResults) == 1, "Failed to store problem result: Problem may already be in the database"
        assert len(probResults[0])== 1
        problem_result_id = probResults[0][0]

        #remove from Queue
        cur.execute("""DELETE FROM Queue
                       WHERE problem_id=%s AND job_id=%s;""",
                    (problem_id, job_id))
        numrows = int(cur.rowcount)
        assert numrows == 1, "Failed to delete job from queue: Concurrency error?"
    con.close()
    assert problem_result_id != None
    return problem_result_id

def collectStats(job_result_id, err_log):
    if cvc4 == 1:
        csCvc4Args = ["./collectStatsCvc4.py",
                      str(job_result_id), err_log, server, user, password, database]
        if verbosity > 0:
            print "collecting cvc4 stats with the command:", ' '.join(csCvc4Args)
        print subprocess.check_output(csCvc4Args)

    if z3 == 1:
        z3Cvc4Args = ["./collectStatsZ3.py",
                      str(job_result_id), err_log, server, user, password, database]
        if verbosity > 0:
            print "collecting z3 stats with the command:", ' '.join(z3Cvc4Args)
        print subprocess.check_output(z3Cvc4Args)

def runProcess(problem_id, problem_path, err_log, out_log, runlim_log):
    err_log_file=open(err_log, 'w')
    out_log_file=open(out_log, 'w')

    run_args = [RUN_LIM, "-t", str(time_limit),
                "-s", str(mem_limit), "-o", runlim_log,
                binary_path]+ args.split() + [problem_path]

    if verbosity > 0:
        print "Running the exact command:", ' '.join(run_args)

    exit_status = subprocess.call(run_args, stdout=out_log_file, stderr=err_log_file)

    runlim_log_file=open(runlim_log,'a')
    print>>runlim_log_file, ("ExitCode="+str(exit_status))

    err_log_file.close()
    out_log_file.close()
    runlim_log_file.close()
    return exit_status

runTimeFA=re.compile("\[runlim\] time\:\s*([^\s]*)\s*seconds")
memoryFA=re.compile("space\:\s*([^\s]*)\s*MB")
def grabTimeAndMemoryFromRunLimLog(runlim_log):
    #grab what we need from runlim_log
    run_time, memory = None, None
    runlim_log_file=open(runlim_log,'r')
    for ln in runlim_log_file:
        m = runTimeFA.search(ln)
        if m != None:
            run_time = float(m.groups()[0])
        m = memoryFA.search(ln)
        if m != None:
            memory = float(m.groups()[0])
    runlim_log_file.close()
    assert run_time != None, "Failed to find runlim's running time"
    assert memory != None, "Failed to find runlim's memory usage"
    return run_time, memory

def grabResultFromOutLog(out_log):
    out_log_file=open(out_log, 'r')
    result = None
    for line in out_log_file:
        result = line
    out_log_file.close()

    if result != None:
        result = result.strip()
        if result == "sat" or result == "unsat":
            return result
    return "unknown"

def grabFromLogs(runlim_log, out_log):
    (run_time, memory) = grabTimeAndMemoryFromRunLimLog(runlim_log)
    result = grabResultFromOutLog(out_log)
    return (run_time, memory, result)

def runProblem(p):
    (problem_id, problem_path) = p
    print "Running", problem_path, "..."

    # error output log
    err_log=bu.genLogPath(log_path, job_id, problem_id, ".err")
    out_log=bu.genLogPath(log_path, job_id, problem_id, ".out")
    runlim_log=bu.genLogPath(log_path, job_id, problem_id, ".rumlim")

    exit_status = runProcess(problem_id, problem_path, err_log, out_log, runlim_log)

    (run_time, memory, result) = grabFromLogs(runlim_log, out_log)

    print "Result", result,
    print "in (", run_time, "seconds,", memory, " MB)"

    job_result_id = storeProblemResult(problem_id, run_time, memory, result, exit_status)
    collectStats(job_result_id, err_log)


def popQueue():
    con = mdb.connect(server, user, password, database);
    emp, problem = None, None
    with con:
        cur = con.cursor()
        cur.execute("""select count(*) from Queue
                       where runner_pid IS NULL and job_id=%s;""",
                    (job_id))
        res = cur.fetchall()
        assert len(res) == 1
        assert len(res[0]) == 1
        qs = res[0][0]
        if qs <= 0:
            emp = True
        else:
            cur.execute("""update Queue set runner_pid=%s
                           where Queue.runner_pid IS NULL and Queue.job_id=%s
                           limit 1;""",
                        (pid, job_id))
            cur.execute("""select Problems.id, Problems.path
                           FROM Problems INNER JOIN Queue ON
                           Problems.id=Queue.problem_id
                           WHERE Queue.job_id=%s and Queue.runner_pid=%s
                           limit 1;""",
                        (job_id, pid))
            problems = cur.fetchall()
            if len(problems) >= 1:
                problem = problems[0]
    con.close()
    return (emp, problem)

# Grab globals for job
print "Running job", job_id, "with process id", pid
(time_limit, mem_limit, binary_path, cvc4, z3, args) = (None, None, None, None, None, None)
con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    cur.execute("""SELECT
                   time_limit, memory_limit, binary_path, cvc4, z3, arguments
                   FROM Jobs WHERE Jobs.id=%s;""",
                (job_id))
    res = cur.fetchall()
    assert len(res) == 1

    (time_limit, mem_limit, binary_path, cvc4, z3, args) = res[0]
    time_limit=int(time_limit)
    mem_limit=int(mem_limit)
con.close()

print "With time_limit=",time_limit, ", mem_limit=",mem_limit,
print ", args=",args,", binary_path=",binary_path,
print ", cvc4=",cvc4,", and z3=",z3

#main loop
while True:
    (emp, problem) = popQueue()
    if emp == True:
        break
    elif problem != None:
        runProblem(problem)
