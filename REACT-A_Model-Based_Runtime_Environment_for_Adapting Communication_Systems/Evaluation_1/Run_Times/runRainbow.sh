
docker stop rainbow || true

for i in {1..10}
do
	docker run -d --rm -p 6901:6901 --name rainbow --hostname rainbow-example cmuable/rainbow-example
	
	sleep 10
	
	docker cp startRainbow.sh rainbow:/rainbow
	docker exec -d rainbow bash -c /rainbow/startRainbow.sh
	docker cp startSwim.sh rainbow:/headless
        docker exec -it rainbow bash -c /headless/startSwim.sh
	docker cp plotResults.sh rainbow:/headless
	docker exec -it rainbow bash -c /headless/plotResults.sh

	# Fetch results
	mkdir $i
	docker cp rainbow:/headless/seams-swim/results/Rplots.pdf ./$i/
	docker cp rainbow:/headless/seams-swim/results/plot.pdf ./$i/
	docker cp rainbow:/headless/seams-swim/results/SWIM/sim-0.sca ./$i/
	docker cp rainbow:/headless/seams-swim/results/SWIM/sim-0.vec ./$i/
	docker cp rainbow:/headless/seams-swim/results/SWIM/sim-trace=traces#2fwc#_day53-r0-105m-l70.delta,latency=0-#0.out ./$i/
	docker cp rainbow:/headless/seams-swim/swim/simulations/swim/swim-console.out ./$i/
	docker cp rainbow:/rainbow/logs/rainbow-console.out ./$i/
	
	docker stop rainbow

	sleep 10
done
