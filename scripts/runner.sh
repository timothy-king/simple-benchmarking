#!/bin/bash

LOG_PATH=`cat ../config/logpath`
USER=`cat ../config/user`
PASSWORD=`cat ../config/password`
RUN_LIM="../runlim-sigxcpu/runlim"

JOB_ID=$1

echo "Running job $JOB_ID"

# Getting Job information
JOB_INFO=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   SELECT time_limit, memory_limit, binary_path, z3, cvc4, arguments FROM Jobs WHERE Jobs.id=$JOB_ID;
EOF`

JOB_INFO=($JOB_INFO)
TIME_LIMIT=${JOB_INFO[6]}
MEM_LIMIT=${JOB_INFO[7]}
BINARY=${JOB_INFO[8]}
Z3=${JOB_INFO[9]}
CVC4=${JOB_INFO[10]}
ARGS=${JOB_INFO[11]}

echo "With time_limit=$TIME_LIMIT, mem_limit=$MEM_LIMIT, args=$ARGS, binary=$BINARY, cvc4=$CVC4 and z3=$Z3"

# Getting problem paths
PROBLEMS=`mysql -h localhost -u $USER -p$PASSWORD <<EOF
   use benchmarking;
   select Problems.id, Problems.path FROM Problems INNER JOIN Queue ON Problems.id=Queue.problem_id WHERE Queue.job_id=$JOB_ID;
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
    #runlim log
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
    if [[ "$CVC4" == "1" ]]; then
	echo `./collectStatsCvc4.py $JOB_RESULT_ID $ERR_LOG $USER $PASSWORD`
    fi

    if [[ "$Z3" == "1" ]]; then
	# z3 prints statistics to regular output 
	echo `./collectStatsZ3.py $JOB_RESULT_ID $OUT_LOG $USER $PASSWORD`
    fi
    
    # remove problem from Queue
    `mysql -h localhost -u $USER -p$PASSWORD <<EOF
     use benchmarking;
     DELETE FROM Queue WHERE problem_id=$PROBLEM_ID AND job_id=$JOB_ID;
EOF`

done

