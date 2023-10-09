docker-compose kill

docker rmi macc-microservicios-client
docker rmi macc-microservicios-delivery
docker rmi macc-microservicios-machine
docker rmi macc-microservicios-order
docker rmi macc-microservicios-payment
docker rmi macc-microservicios-rabbitmq

docker build -t macc-microservicios-client ./clientws
docker build -t macc-microservicios-delivery ./deliveryws
docker build -t macc-microservicios-machine ./machinews
docker build -t macc-microservicios-order ./orderws
docker build -t macc-microservicios-payment ./paymentws
docker build -t macc-microservicios-rabbitmq ./rabbitmq

docker-compose up -d