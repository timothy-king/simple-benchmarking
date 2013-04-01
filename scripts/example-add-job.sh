#./add-job.py -b /scratch/kb1289/cvc4-28c9e17 -p 1 -t 300 -m 2000 -n QFLRA -d testing -c -a --stats
./add-job.py --binary /scratch/kb1289/cvc4eagereager --cvc4 \
             --problemset 3 --time 300 --memory 1800 \
             --name QF_LRA --description testing --manual-start \
             --arguments --stats --decision=justification-stoponly
