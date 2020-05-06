# Host3: Planner and Knowledge

Host3 runs the planner and knowledge components of REACT. The `configs` folder contains the configuration files and the AOS and TSS for the SDN handover use case.

This command can start REACT using the config files: `docker run --rm -it --volume ${PWD}/configs:/usr/src/configs --network="host" wi2bc11.bwl.uni-mannheim.de:18443/react`