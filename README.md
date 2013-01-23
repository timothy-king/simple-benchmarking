A simple MySQL based benchmarking setup and scripts.

A) Setup:
1) Install and configure mysql, python, php, apache, and mysql+php+apache.
2) mysql -uuser -ppass < benchmarking_structure.sql
3) Populate table with benchmarks directory (recursive).
  # cd scripts
  # add-benchmarks.sh $DIRECTORY $LOGIC
4) Create problem set (pure sql atm sorry)
5) Create one line text files in config/{logpath,password,user} containing path for logs, mysql password and mysql user. 
6) Compile runlim
  # cd runlim-sigxcpu
  # ./configure
  # make

B) Run jobs:
  # cd scripts
  # ./run-job.sh -b <binary-path> -p <problem-set> -a <args> -t <time-limit> -m <memory-limit> -n <job-name> -d <job-description> [-c running cvc4 (used for stats)]
  See example-run-job.sh for an example.

C) Analyze
1) Grab statistics in CSV (can be manipulated with R)
  # cd scripts
  # ./dumpCSV.py <Job number> [statistics file]
2) Visualize using the web interface (coming)