# Microservicios API Gateway

## Ejecutar Microservicios:

En la terminal de Windows, escribir `.\dc-up.bat` para ejecutar los
comandos que se encuentran en el archivo. Esto se encarga de crear
las imagenes de cada microservicio, así como de ejecutar todo el
*docker-compose*.

Haciendolo de esta forma, el comando `docker-compose up -d` no genera
una imagen por cada contenedor, ya que el mismo microservicio estaría
duplicado debido a que se emplean replicas.
En su lugar, primero genera las imagenes y se usan dichas imagenes
para construir los contenedores.

## MIENTRAS QUE NO HAYA REPLICAS ACTIVADAS NO HACE FALTA LO ANTERIOR

## Usuario y Contraseña Administrador:

Username: joxemai
Password: joxemai