#!/bin/bash

for i in {1..30}
do
    echo "Run $i"
    sudo python handover.py -e True -r $i -o False -m 20 --controller-ip "10.0.1.3" -s True
    sleep 5
    sudo mn -c
    sleep 5
done
