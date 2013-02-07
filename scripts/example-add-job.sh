#./add-job.py -b /scratch/kb1289/cvc4-28c9e17 -p 1 -t 300 -m 2000 -n QFLRA -d testing -c -a --stats
./add-job.py --binary /scratch/kb1289/cvc4-28c9e17 --cvc4 \
             --problemset 1 --time 300 --memory 2000 \
             --name QFLRA --description testing \
             --arguments --stats
