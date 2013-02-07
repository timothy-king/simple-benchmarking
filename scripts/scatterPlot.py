#!/usr/bin/env python

import MySQLdb as mdb
import sys
import argparse
import string
import benchmarking_utilities as bu


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

args = parser.parse_args()
xjob=args.xjob
yjob=args.yjob
xfield=args.xfield
yfield=args.yfield
logarithmic_scale = args.logarithmic

outfile = str(xjob) + '-' + xfield + '_vs_' + str(yjob) + '-' + yfield;

plot_title = str(xjob) + "vs" + str(yjob)
plot_xlabel = xfield + "(" + str(xjob) + ")" 
plot_ylabel = yfield + "(" + str(yjob) + ")" 
plot_output = outfile + ".pdf"

print "Generating plot for xjob=", xjob, ", yjob=", yjob, ", xfield=", xfield, " and yfield=", yfield 

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

def insertInToFamilyMap(familyMap, key, val1, val2) :
    if key in familyMap :
        aux = familyMap[key]
        aux.append((val1, val2))
        familyMap[key] = aux
    else :
        familyMap[key] = [(val1, val2)]
        
def groupByFamilies(results) :
    # create one .dat file for each family
    familyMap = {}
    for result in results :
        path = result[0]
        xvalue = result[1]
        yvalue = result[2]
        family = parseFamily(path)
        insertInToFamilyMap(familyMap, family, xvalue, yvalue)

    return familyMap

def dumpDatFile(filename, family, family_results) :
    outfile_name=filename +'-' +family + '.dat'
    outfile = open(outfile_name, 'w')
    outfile.write(";; " + family + "\n")

    for result in family_results:
        xvalue = result[0]
        yvalue = result[1]
        outfile.write(str(xvalue) + " " + str(yvalue) + "\n") 
    outfile.close()

    return outfile_name

def getColor(color_number) :
    return "blue"

def setupGnuPlot(script, title, xlabel, ylabel) :
    script.write("set autoscale\n")
    print logarithmic_scale
    if (logarithmic_scale) :
        script.write("set logscale xy\n")
        
    script.write("set title \"" + title + "\"\n")
    script.write("set xlabel \"" + xlabel + "\"\n")
    script.write("set ylabel \"" + ylabel + "\"\n")
    script.write("set xtic auto\n")
    script.write("set ytic auto\n")
    script.write("set terminal pdf size 5, 5 \n")
    script.write("set output \"" + plot_output + "\"\n")
    script.write("set size 1, 1\n")
    
def generatePlots(outfile, families) :

    script = open(outfile + ".gnuplot", 'w')

    setupGnuPlot(script, plot_title, plot_xlabel, plot_ylabel)
    
    color = 0
    script.write("plot ")
    
    for family in families:
        family_results = families[family]
        color = color + 1
        dat_file = dumpDatFile(outfile, family, family_results)
        gnuPlot(script, dat_file, color, family)

    script.write("x with line linecolor rgb \"gray\" \n")

    
    
def gnuPlot(script_file, dat_file, color, family) :
    #plot "./73-run_timevs72-run_time-sage.dat" using 1:2 with p pt 2 pointsize 2 linecolor 5 title 'Hello'
    script_file.write("\"" + dat_file + "\" using 1:2 with p pt 9 pointsize 1 linecolor " + str(color) + " title \"" + family + "\", ")

    
con = mdb.connect(server, user, password, database);
with con:
    cur = con.cursor()
    results = selectAllResult(cur, xjob, yjob, xfield, yfield)
    families = groupByFamilies(results)
    generatePlots(outfile, families)
con.close()
