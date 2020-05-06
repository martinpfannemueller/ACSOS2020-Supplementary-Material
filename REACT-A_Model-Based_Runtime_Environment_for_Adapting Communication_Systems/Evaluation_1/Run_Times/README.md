# Evaluation 1 - Run Times

This folder contains the raw results of the run time evaluation in the `Results` folder. Additionally, it contains the shell scripts for executing the evaluation, the `configs` folder with the configuration files, the AOS as well as the TSS for the SWIM case, and the Python-based interfaces including the generated IDL bindings in the folder `swim-interface`. You need to use Python 3 for this evaluation. Ubuntu typically still uses Python 2 when running `python` and `pip`. In this case you need to use the commands `python3` and `pip3`.

## Reproducing the results

### Setup

1. For building the ZeroC Ice Python package dependency you need gcc and some development headers. On Ubuntu you need to run `sudo apt-get install build-essential libssl-dev libbz2-dev`
1. Install ZeroC Ice and Zeroconf Python dependencies: `pip install -r swim-interface/requirements.txt`
2. Clone Rainbow: `git clone https://github.com/cmu-able/rainbow.git`
3. Replace `gabrielmoreno/swim:1.0` with `gabrielmoreno/swim:1.0.1` as this contains a fixed version of SWIM in `deployments/rainbow-example/Dockerfile`
4. Run `docker build -t rainbow-build .` inside the `rainbow` folder
5. Run `docker build -t cmuable/rainbow-example -f deployments/rainbow-example/Dockerfile .` inside the `rainbow` folder
6. Make sure that all shell scripts are executable: `chmod +x *.sh`

### Executing

You will get folders named 1-10 from each run as you find them inside the `Results` folder. Additionally, you will get log files named `runRainbow.log`, `SWIM.py.log`, `runSWIM.sh.log`, and `REACT.log`. `runRainbow.log` and `REACT.log` have been used for evaluating the run times.

#### Rainbow

Execute `runRainbow.sh > runRainbow.log`

#### REACT

1. In a first shell: `docker run --rm -it --name react --volume ${PWD}/configs:/usr/src/configs --network="host" wi2bc11.bwl.uni-mannheim.de:18443/react`
2. In a second shell: `python swim-interface/SWIM.py > SWIM.py.log` (this should be Python 3)
3. In a third shell: `./runSWIM.sh > runSWIM.sh.log`
4. When you are finished, fetch the REACT log from Docker by executing `docker logs react > REACT.log`