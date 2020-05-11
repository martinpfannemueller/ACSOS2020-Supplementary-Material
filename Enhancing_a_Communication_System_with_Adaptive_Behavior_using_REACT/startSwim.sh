#!/bin/bash

cd /headless/seams-swim/swim/simulations/swim && ../../src/swim swim.ini -u Cmdenv -c sim -n ..:../../src/:../../../queueinglib:../../src -lqueueinglib -s --cmdenv-redirect-output=true -r 0
