#!/bin/bash

# usage string
USAGE="Usage: $0 -d <benchmarks-dir> -l <logic>"

# parsing options
while getopts "d:l:" opt; do
    case $opt in
	d)
	    if [ ! -d "$OPTARG" ]; then
		echo "$OPTARG is not a valid directory" >&2
		echo $USAGE
		exit 1

	    else
		BENCHMARKS_DIR=$OPTARG
	    fi
	    ;;
	l)
	    LOGIC=$OPTARG
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    ;;
    esac
done

##############
### MySql ###

BENCHMARKS=`find $BENCHMARKS_DIR -name '*.smt2'`
#echo $BENCHMARKS

for FILE in $BENCHMARKS; do
    STATUS=`grep status $FILE`
    if [[ $STATUS = "(set-info :status unsat)" ]]
    then
	STATUS="unsat"
    elif [[ $STATUS = "(set-info :status sat)" ]]
    then
	STATUS="sat"
    else
	STATUS="unknown"
    fi
    echo "file is $FILE with status: $STATUS and logic $LOGIC"
    # inserting into sql database
    SQL_OUT=`mysql -h localhost -u root -pcluster <<EOF
    use smt_cluster;
    insert into Problems VALUES(default, '$FILE', '$STATUS', '$LOGIC');
EOF`
done


