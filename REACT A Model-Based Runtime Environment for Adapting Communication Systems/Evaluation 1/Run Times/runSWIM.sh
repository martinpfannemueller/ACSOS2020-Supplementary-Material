
docker stop swim || true

for i in {1..10}
do
	docker run -d --rm -p 6901:6901 -p 4242:4242 --name swim --hostname rainbow-example cmuable/rainbow-example

	docker cp startSwim.sh swim:/headless
	docker exec -it swim bash -c /headless/startSwim.sh
	docker cp plotResults.sh swim:/headless
	docker exec -it swim bash -c /headless/plotResults.sh

	# Fetch results
	mkdir $i
	docker cp swim:/headless/seams-swim/results/Rplots.pdf ./$i/
	docker cp swim:/headless/seams-swim/results/plot.pdf ./$i/
	docker cp swim:/headless/seams-swim/results/SWIM/sim-0.sca ./$i/
	docker cp swim:/headless/seams-swim/results/SWIM/sim-0.vec ./$i/
	docker cp swim:/headless/seams-swim/results/SWIM/sim-trace=traces#2fwc#_day53-r0-105m-l70.delta,latency=0-#0.out ./$i/
	docker cp swim:/headless/seams-swim/swim/simulations/swim/swim-console.out ./$i/
	
	docker stop swim

	sleep 10
done

