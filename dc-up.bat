docker-compose kill

docker rmi -f macc-microservicios-client
docker rmi -f macc-microservicios-delivery
docker rmi -f macc-microservicios-machine
docker rmi -f macc-microservicios-order
docker rmi -f macc-microservicios-payment
docker rmi -f macc-microservicios-rabbitmq
docker rmi -f macc-microservicios-logs

docker build -t macc-microservicios-logs ./logs
docker build -t macc-microservicios-client ./clientws
docker build -t macc-microservicios-delivery ./deliveryws
docker build -t macc-microservicios-machine ./machinews
docker build -t macc-microservicios-order ./orderws
docker build -t macc-microservicios-payment ./paymentws
docker build -t macc-microservicios-rabbitmq ./rabbitmq

docker-compose up -d