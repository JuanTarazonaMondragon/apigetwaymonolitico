import asyncio
import aio_pika
import json
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud, models


async def on_log_message(message):
    async with message.process():
        routing_key = message.routing_key
        data = message.body
        log = models.Log(
            routing_key=routing_key,
            data=data
        )
        db = SessionLocal() # Esto es una puta guarrada, idea de Andoni, hay que preguntar si es legal o no. Ojo, pero al menos funciona, GRANDE ANDONI!
        await crud.create_log(db, log)
        await db.close()


async def subscribe_logs():
    # Define your RabbitMQ server connection parameters directly as keyword arguments
    connection = await aio_pika.connect_robust(
        host='rabbitmq',
        port=5672,
        virtualhost='/',
        login='user',
        password='user'
    )
    # Create a channel
    channel = await connection.channel()
    # Declare the exchange
    exchange_name = 'events'
    exchange = await channel.declare_exchange(name=exchange_name, type='topic', durable=True)
    # Create a random queue with an auto-generated name
    queue_name = "logs"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "#"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_log_message(message)


