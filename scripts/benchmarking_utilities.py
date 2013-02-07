import sys
import MySQLdb as mdb

USER_FILE="../config/user"
PASSWORD_FILE="../config/password"
HOST_FILE="../config/host"
DATABASE_FILE="../config/database"
LOG_PATH_FILE="../config/logpath"

def echoFile(fileName):
    try:
        f = open(fileName, 'r');
        contents = f.read()
        return contents.strip()
    except IOError:
        sys.exit("Could not open " + fileName+". Make sure this exists and is readable.")

def loadConfiguration():
    server=echoFile(HOST_FILE)
    user=echoFile(USER_FILE)
    password=echoFile(PASSWORD_FILE)
    database=echoFile(DATABASE_FILE)
    return (server, user, password, database)

def loadLogPath():
    return echoFile(LOG_PATH_FILE)

def genLogPath(log_path, job_id, problem_id, ext):
    return log_path+str(job_id)+"/"+str(problem_id)+ext


def printJob(j):
    job_id = j[0]
    name = j[1]
    description = j[2]
    time_limit = j[3]
    memory_limit = j[4]
    problem_set_id = j[5]
    arguments = j[6]
    timestamp = j[7]
    binary_path = j[8]

    print job_id, name, ";", description
    print " ", "Problem set id: ", problem_set_id
    print " ", timestamp.isoformat(), time_limit, memory_limit
    print " ", binary_path, arguments


def selectJob(cur, job_id):
    cur.execute("""SELECT
                id, name, description, time_limit, memory_limit,
                problem_set_id, arguments, timestamp, binary_path, z3, cvc4
                from Jobs where Jobs.id = %s;""", job_id)
    jobs = cur.fetchall()
    assert(len(jobs)==1)
    assert(jobs[0][0] == job_id)
    return jobs[0]

def printJobWithId(cur, job_id):
    printJob(selectJob(cur, job_id))

def confirmJob(cur, job_id):
    job = selectJob(cur, job_id)
    printJob(job)
    cand_id = input("Reenter id to confirm:")
    return cand_id == job[0]

def confirmJobResult(cur, job_id, problem_id, job_result_id):
    job = selectJob(cur, job_id)
    printJob(job)

    problem_path = getProblemPath(cur, problem_id)
    print "Problem:", problem_path
    print "job_result_id:", job_result_id
    cand_id = input("Reenter job_result_id to confirm:")
    return cand_id == job_result_id

def getProblemPath(cur, problem_id):
    cur.execute('SELECT path from Problems where id = %s;', problem_id)
    res = cur.fetchall()
    assert len(res) == 1
    assert len(res[0]) == 1
    return res[0][0]


def deleteJobResult(cur, jrid):
    print "\t","Deleting job result id", jrid
    cur.execute('DELETE FROM ResultStats WHERE ResultStats.job_result_id = %s;', jrid)
    printDeleted(int(cur.rowcount), "ResultStats")
    cur.execute('DELETE FROM JobResults WHERE JobResults.id = %s;', jrid)
    printDeleted(int(cur.rowcount), "JobResults")


def printDeleted(num_rows, table_name):
    print "\t","Deleted", num_rows,"from",table_name

def deleteJobIdFromQueue(cur, job_id):
    cur.execute('DELETE FROM Queue WHERE Queue.job_id = %s;', job_id)
    printDeleted(int(cur.rowcount), "Queue")

def jobResultIds(cur, job_id):
    cur.execute("""SELECT JobResults.id from JobResults
                where JobResults.job_id = %s;""",
                (job_id))
    jobsQueury = cur.fetchall()
    return [j[0] for j in jobsQueury]
