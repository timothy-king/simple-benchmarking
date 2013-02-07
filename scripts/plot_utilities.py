#!/usr/bin/python

import MySQLdb as mdb
import sys
import os
import string
import benchmarking_utilities as bu

def selectAllResult(cur, xjob, yjob, xfield, yfield) :

    if (xfield == 'run_time') :
        cur.execute("""SELECT JobResults.problem_id, JobResults.run_time \
                       FROM JobResults where job_id=%s order by problem_id;""", (xjob))
    elif (xfield == 'memory') :
        cur.execute("SELECT JobResults.problem_id, JobResults.memory \
                     FROM JobResults where job_id=%s order by problem_id;", (xjob))
    else :
        xfield_id = getStatId(cur, xfield) 
        cur.execute("SELECT JobResults.problem_id, stat_value FROM ResultStats INNER JOIN JobResults ON ResultStats.job_result_id=JobResults.id WHERE JobResults.job_id=%s AND ResultStats.stat_id=%s;", (xjob, xfield_id))

    xproblems = cur.fetchall()
    assert (xproblems!= None)
    
    results = []
    for xrow in xproblems:
        problem_id = xrow[0]
        xresult = str(xrow[1]).rstrip()
        # it should work if one of the jobs has missing data
        yresult = selectMatchingResult(cur, yjob, problem_id, yfield)
        if (yresult != None) :
            yresult = str(yresult).rstrip()
            problem_path = getProblemPath(cur, problem_id)
            results.append((problem_path, xresult, yresult))
    return results

def selectMatchingResult(cur, job, problem_id, field):
    if (field == 'run_time'): 
        cur.execute("SELECT run_time FROM JobResults WHERE job_id=%s AND problem_id=%s;", (job, problem_id))
    elif (field == 'memory'): 
        cur.execute("SELECT memory FROM JobResults WHERE job_id=%s AND problem_id=%s;", (job, problem_id))
    else :
        stat_id = getStatId(cur, field)
        result_id = getResultId(cur, job, problem_id)
        cur.execute("SELECT stat_value FROM ResultStats WHERE job_result_id=%s and stat_id=%s;", (result_id, stat_id))
        
    res = cur.fetchone()
    if (res == None) :
        return None
    return res[0]

def getResultId(cur, job_id, problem_id) :
    cur.execute("SELECT id FROM JobResults WHERE job_id=%s AND problem_id=%s; ", (job_id, problem_id))
    res = cur.fetchone()
    assert (res!= None)
    return res[0]

def getStatId(cur, stat_name) :
    cur.execute("SELECT id FROM Stats WHERE name=%s;", (stat_name))
    res = cur.fetchone()
    assert (res!= None)
    stat_id = res[0]
    return stat_id
    
def getProblemPath(cur, problem_id) :
    cur.execute("SELECT path FROM Problems WHERE id=%s; ", (problem_id))
    res = cur.fetchone()
    assert (res != None)
    return res[0]

def getJobName(cur, job_id) :
    cur.execute("select name from Jobs where id=%s;", (job_id))
    res = cur.fetchone()
    assert res != None
    return res[0]


# We assume that the path is of the form */smtlib*/<logic>/family/*
def parseFamily(path) :
    tokens = path.split('/')
    index = None
    for i, token in enumerate(tokens) :
        if (token.startswith('smtlib')) :
            index = i

    index = index + 2
    family = tokens[index]
    return family 

def insertInToFamilyMap(familyMap, key, path, val1, val2) :
    if key in familyMap :
        aux = familyMap[key]
        aux.append((path, val1, val2))
        familyMap[key] = aux
    else :
        familyMap[key] = [(path, val1, val2)]
        
def groupByFamilies(results) :
    # create one .dat file for each family
    familyMap = {}
    for result in results :
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        family = parseFamily(path)
        insertInToFamilyMap(familyMap, family, path, xvalue, yvalue)

    return familyMap

def dumpDatFile(filename, family, family_results) :
    outfile_name=filename +'-' +family + '.dat'
    outfile = open(outfile_name, 'w')
    outfile.write(";; " + family + "\n")

    for result in family_results:
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        outfile.write(path + " " +str(xvalue) + " " + str(yvalue) + "\n") 
    outfile.close()
    return outfile_name

def gnuPlot(script_file, dat_file, color, family) :
    script_file.write("\"" + dat_file + "\" using 2:3 with p pt 9 pointsize 1 linecolor " + str(color) + " title \"" + family + "\", ")

def generatePlots(outfile, families) :
    script = open(outfile + ".gnuplot", 'a')
    script.write("plot ")
    color = 0
    for family in families:
        family_results = families[family]
        color = color + 1
        dat_file = dumpDatFile(outfile, family, family_results)
        gnuPlot(script, dat_file, color, family)

    script.write("x with line linecolor rgb \"gray\" \n")

def convertToRelativePath(absolute_path) :
    current_path = os.getcwd()
    levels = len(current_path.split('/'))
    relative_path = ""
    for i in range(levels - 1) :
       relative_path = relative_path + "../"
    relative_path = relative_path + absolute_path
    return relative_path
