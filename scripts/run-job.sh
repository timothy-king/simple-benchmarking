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
   insert into Jobs VALUES(default, "$JOB_NAME", "$JOB_DESCRIPTION", $TIME_LIMIT, $MEM_LIMIT, $PROBLEM_SET, "$ARGS", default, "$BINARY", $Z3, $CVC4);
EOF`

# Getting job number
JOB_ID_STRING=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   select MAX(id) from Jobs; 
EOF`

JOB_ID_STRING=($JOB_ID_STRING)
JOB_ID=${JOB_ID_STRING[1]}

echo "Adding to queue job $JOB_ID"

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
    
    # store job result
   `mysql -u $USER -p$PASSWORD -h localhost <<EOF
   use benchmarking;
   insert into Queue VALUES(default, $JOB_ID, $PROBLEM_ID, default);
EOF`
done

# starting the runner
echo "Starting runner for job $JOB_ID..."
./runner.sh $JOB_ID
