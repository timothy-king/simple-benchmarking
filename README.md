A simple MySQL based benchmarking setup and scripts.

A) Setup:
1) Install and configure mysql, python, php, apache, mysql+php+apache and gnuplot 4.6 or higher.
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

B) Add jobs:
  # cd scripts
  # ./add-job.sh -b <binary-path> -p <problem-set> -a <args> -t <time-limit> -m <memory-limit> -n <job-name> -d <job-description> [-c running cvc4 (used for stats)]
  See example-add-job.sh for an example.

C) Runners
  # cd scripts
  # ./runner.py <job id>

D) Analyze
1) Grab statistics in CSV (can be manipulated with R)
  # cd scripts
  # ./dumpCSV.py <Job number> [statistics file]
2) Visualize using the web interface (coming)

E) Misc. Database Management
1) Reset the mysql queue using ./resetQueue.py
2) Delete a job using ./deleteJob.py <job id>

