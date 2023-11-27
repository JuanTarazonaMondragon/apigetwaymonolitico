docker-compose kill

docker rmi -f macc-aas-client
docker rmi -f macc-aas-delivery
docker rmi -f macc-aas-machine
docker rmi -f macc-aas-order
docker rmi -f macc-aas-payment
docker rmi -f macc-aas-rabbitmq
docker rmi -f macc-aas-logs

docker build -t macc-aas-logs ./logsws
docker build -t macc-aas-client ./clientws
docker build -t macc-aas-delivery ./deliveryws
docker build -t macc-aas-machine ./machinews
docker build -t macc-aas-order ./orderws
docker build -t macc-aas-payment ./paymentws
docker build -t macc-aas-rabbitmq ./rabbitmq

docker-compose up -d
