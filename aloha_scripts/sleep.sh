#!/bin/bash
source activate aloha

python sleep.py left &
python sleep.py right &

exit 1