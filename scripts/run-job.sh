#!/bin/bash

# usage string
USAGE="Usage: $0 -b <binary-path> -p <problem-set> -a <args> -t <time-limit> -m <memory-limit> -n <job-name> -d <job-description> [-c collect cvc4 stats] [-z collect z3 stats]"

# default time and memory limit
TIME_LIMIT=100
MEM_LIMIT=1500


LOG_PATH=`cat ../config/logpath`
USER=`cat ../config/user`
PASSWORD=`cat ../config/password`
RUN_LIM="../runlim-sigxcpu/runlim"

CVC4=false
Z3=false

# parsing options
while getopts "zcp:b:a:t:m:d:n:" opt; do
    case $opt in
	c)
	    CVC4=true;
	    ;;
	z)
	    Z3=true;
	    ;;
	b)
	    if [ ! -f "$OPTARG" ]; then
		echo "$OPTARG is not a valid file" >&2
		echo $USAGE
		exit 1

	    else
		BINARY=$OPTARG
	    fi
	    ;;
	a)
	    ARGS=$OPTARG
	    ;;
	t)
	    if [[ $OPTARG != [0-9]* ]]; then
		echo "Time limit $OPTARG should be a numeric value"  >&2
		echo $USAGE
		exit 1

	    else
		TIME_LIMIT=$OPTARG
	    fi
	    ;;
	m)
	    if [[ $OPTARG != [0-9]* ]]; then
		echo "Memory limit $OPTARG should be a numeric value"  >&2
		echo $USAGE
		exit 1

	    else
		MEM_LIMIT=$OPTARG
	    fi
	    ;;
	p)
	    if [[ $OPTARG != [0-9]* ]]; then
		echo "Problem set $OPTARG should be a numeric value"  >&2
		echo $USAGE
		exit 1

	    else
		PROBLEM_SET=$OPTARG
	    fi
	    ;;
	n)
	    JOB_NAME=$OPTARG
	    ;;
	d)
	    JOB_DESCRIPTION=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    ;;
    esac
done

if [[ -z $BINARY ]]; then
    echo "Must provide a binary to run. "
    echo $USAGE
    exit 1
fi

if [[ -z $PROBLEM_SET ]]; then
    echo "Must provide a problem set. "
    echo $USAGE
    exit 1
fi

if [ "$CVC4" == "true" -a "$Z3" == "true" ]; then
    echo "Can only collect statistics for one solver. "
    echo $USAGE
    exit 1
fi

##############
### MySql ###

echo "Logging in to MySql..."

# setting up default job name 
if [[ $JOB_NAME = "" ]]; then
    JOB_NAME=$BINARY
fi

# storing the current job in the database
SQL_OUT=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   insert into Jobs VALUES(default, "$JOB_NAME", "$JOB_DESCRIPTION", $TIME_LIMIT, $MEM_LIMIT, $PROBLEM_SET, "$ARGS", default);
EOF`

# Getting job number
JOB_ID_STRING=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   select MAX(id) from Jobs; 
EOF`

JOB_ID_STRING=($JOB_ID_STRING)
JOB_ID=${JOB_ID_STRING[1]}

echo "Running job $JOB_ID"

# Getting problem paths
PROBLEMS=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   select Problems.id, Problems.path FROM Problems INNER JOIN ProblemSetToProblem ON Problems.id=ProblemSetToProblem.problem_id WHERE ProblemSetToProblem.problem_set_id=$PROBLEM_SET;
EOF`

# setting up directory for outputting logs
if [ ! -d "$LOG_PATH$JOB_ID" ]; then
    mkdir $LOG_PATH$JOB_ID
fi

# temporary file for runlim output
TEMP=runlim_temp

PROBLEM_ARRAY=($PROBLEMS)
for ((i=3; i<${#PROBLEM_ARRAY[@]}; i+=2)); # skipping the first values that are part of the header
do
    PROBLEM_ID=${PROBLEM_ARRAY[`expr $i - 1`]}
    PROBLEM_PATH=${PROBLEM_ARRAY[$i]}
    echo "Running $PROBLEM_PATH..."

    # error output log
    ERR_LOG=$LOG_PATH$JOB_ID/$PROBLEM_ID.err
    # output log 
    OUT_LOG=$LOG_PATH$JOB_ID/$PROBLEM_ID.out
    #runlimp log
    RUNLIM_LOG=$LOG_PATH$JOB_ID/$PROBLEM_ID.runlim

    # running the binary on the benchmark
    $RUN_LIM -t $TIME_LIMIT -s $MEM_LIMIT -o $RUNLIM_LOG $BINARY $ARGS $PROBLEM_PATH 1> $OUT_LOG 2> $ERR_LOG

    echo "ExitCode=$?" >> $RUNLIM_LOG

    # store run times
    RUN_TIME=`grep "\[runlim\] time:" $RUNLIM_LOG | sed 's/.*time:\s*//' | sed 's/\sseconds//' `
    MEMORY=`grep "space:" $RUNLIM_LOG | sed 's/.*space:\s*//' | sed 's/\sMB//'`
    EXIT_STATUS=`grep "ExitCode=" $RUNLIM_LOG | sed 's/ExitCode=//'`
    RESULT=`head -1 $OUT_LOG`
    echo "the result is $RESULT "
    if [[ "$RESULT" != "sat" && "$RESULT" != "unsat" ]]; then
	RESULT="unknown"
    fi

    # store job result
    JOB_RESULT_ID_STR=`mysql -u $USER -p$PASSWORD -h localhost <<EOF
   use benchmarking;
   insert into JobResults VALUES(default, $JOB_ID, $PROBLEM_ID, $RUN_TIME, $MEMORY, "$RESULT", $EXIT_STATUS);
   select MAX(id) from JobResults;
EOF`

    JOB_RESULT_ID_STR=($JOB_RESULT_ID_STR)
    JOB_RESULT_ID=${JOB_RESULT_ID_STR[1]}
    if [[ "$CVC4" == "true" ]]; then
	echo `./collectStatsCvc4.py $JOB_RESULT_ID $ERR_LOG $USER $PASSWORD`
    fi

    if [[ "$Z3" == "true" ]]; then
	# z3 prints statistics to regular output 
	echo `./collectStatsZ3.py $JOB_RESULT_ID $OUT_LOG $USER $PASSWORD`
    fi

    

done

