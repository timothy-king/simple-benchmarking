#!/usr/bin/python

import MySQLdb as mdb
import sys
import os
import string
import benchmarking_utilities as bu

def selectAllResult(cur, xjob, yjob, xfield, yfield) :

    if (xfield == 'run_time') :
        cur.execute("""SELECT JobResults.problem_id, JobResults.run_time \
                       FROM JobResults where job_id=%s and result!=\"unknown\" and result != \"error\" order by problem_id;""", (xjob))
    elif (xfield == 'memory') :
        cur.execute("SELECT JobResults.problem_id, JobResults.memory \
                     FROM JobResults where job_id=%s and result!=\"unknown\" and result != \"error\" order by problem_id;", (xjob))
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
        cur.execute("SELECT run_time FROM JobResults WHERE job_id=%s AND problem_id=%s AND result!=\"unknown\" AND result!=\"error\";", (job, problem_id))
    elif (field == 'memory'): 
        cur.execute("SELECT memory FROM JobResults WHERE job_id=%s AND problem_id=%s AND result!=\"unknown\" AND result!=\"error\";", (job, problem_id))
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
def parseFamily1(path) :
    tokens = path.split('/')
    index = None
    for i, token in enumerate(tokens) :
        if (token.startswith('smtlib')) :
            index = i

    index = index + 2
    family = tokens[index]
    return family 

# We infer family from file name, <family>.<benchmarkname>.smt2*
def parseFamily2(path) :
    tokens = path.split('/')
    path = tokens[-1]      # path now is name of file
    tokens = path.split('.')
    if len(tokens) <= 2: # there was perhaps no family name in benchmark
	raise
    family = tokens[0]
    return family

# Try to parse family
def parseFamily(path) :
    try:
        return parseFamily1(path)
    except:
	return parseFamily2(path)

def insertInToFamilyMap(familyMap, key, path, val1, val2) :
    if key in familyMap :
        aux = familyMap[key]
        aux.append((path, val1, val2))
        familyMap[key] = aux
    else :
        familyMap[key] = [(path, val1, val2)]
        
def groupByFamilies(results) :
    familyMap = {}
    for result in results :
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        family = parseFamily(path)
        insertInToFamilyMap(familyMap, family, path, xvalue, yvalue)

    return familyMap

# trying to make things more modular

def setupPdfPlot(output, pdf_output) :
    output.write("set terminal pdf size 6, 4.5\n")
    output.write("set output \"" + pdf_output + "\"\n")

def setupCanvasPlot(output, name) :
    output.write("set terminal canvas size 800, 600 name \"" + name + "\"\n")
    
def setupPlot(output, xlabel, ylabel, title) :
    output.write("set autoscale\n")
    output.write("set title \"" + title + "\"\n")
    output.write("set xlabel \"" + xlabel + "\"\n")
    output.write("set ylabel \"" + ylabel + "\"\n")
    output.write("set xtic auto\n")
    output.write("set ytic auto\n")
    output.write("set key outside autotitle columnheader\n")

def setupCactusPlot(output) :
    output.write("set logscale y\n")
    
def getSortedResults(cur, job_id) :
    cur.execute("SELECT run_time FROM JobResults WHERE job_id = %s AND result != \"unknown\" AND result != \"error\" ORDER BY run_time; ", (job_id))
    res = cur.fetchall()
    assert (res != None)
    return res; 

def dumpCactusToFile(data_file, title, data) :
    data_file.write(title + " " + title + "\n")
    sum = 0
    for i in range(len(data)):
        sum = sum + data[i][0]
        xval = i
        yval = sum 
        data_file.write(str(xval) + " " + str(yval) + "\n")
    data_file.write("\n\n")

def dumpFamilyToFile(data_file, family, family_results) :
    data_file.write(family + " " + family + " " + family + "\n")
    for result in family_results :
        path = result[0]
        xval = result[1]
        yval = result[2]
        data_file.write(path + " " + str(xval) + " " + str(yval) + "\n")
    data_file.write("\n\n")
    
def startPlot(output) :
    output.write("plot ")
    
def plotSeparator(output) :
    output.write(", "); 

def plotDiagonal(output) :
    output.write("x with lines linecolor rgb \"gray\"")
    
def plotOneCactus(output, data_file_name, index, col1, col2) :
    file_str = "\"< cat " + data_file_name + "\" "
    index_str = "index " +  str(index) + " "
    columns_str = "using " + str(col1) + ":" + str(col2) + " "
    configuration_str = " with linespoints pt " + str(index) + " pointsize 0.5 linecolor " + str(index + 1)
    output.write(file_str + index_str + columns_str + configuration_str)

def plotOneScatter(output, data_file_name, index, col1, col2) :
    file_str = "\"< cat " + data_file_name + "\" "
    index_str = "index " +  str(index) + " "
    columns_str = "using " + str(col1) + ":" + str(col2) + " "
    configuration_str = " with points pt "+ str(index + 1)+" pointsize 1 linecolor " + str(index + 1)
    output.write(file_str + index_str + columns_str + configuration_str)
    
def getRunTimes(cur, xjob, yjob) :
    cur.execute("select Problems.path, Aruntime, Bruntime from (select A.problem_id, A.run_time as Aruntime, B.run_time as Bruntime from ( select * from JobResults where job_id=%s) as A join (select * from JobResults where job_id=%s) as B on A.problem_id = B.problem_id) as C join Problems on Problems.id = C.problem_id;", (xjob, yjob))
    res = cur.fetchall()
    assert (res != None)
    return res; 

def dumpJavaScriptArray(output, family_results) :
    for result in family_results:
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        output.write("benchmark_paths.push(\"" + path + "\"); ");
        output.write("result_x_values.push(" + str(xvalue) + "); ");
        output.write("result_y_values.push(" + str(yvalue) + "); ");

def declareJavaScriptArrays(output) :
    output.write("var benchmark_paths = new Array(); \n")
    output.write("var result_x_values = new Array(); \n")
    output.write("var result_y_values = new Array(); \n")
