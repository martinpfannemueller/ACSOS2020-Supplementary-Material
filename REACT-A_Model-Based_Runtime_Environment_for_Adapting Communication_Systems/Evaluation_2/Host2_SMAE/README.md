# Host2: Sensor, Monitor, Analyzer, and Executor

Host2 runs the sensor, monitor, analyzer, and executor components of REACT. The `configs` folder contains the configuration files.

This command can start REACT using the config files: `docker run --rm -it --volume ${PWD}/configs:/usr/src/configs --network="host" wi2bc11.bwl.uni-mannheim.de:18443/react`