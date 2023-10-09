import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from sql import crud, schemas
import json

async def on_message(message):
    async with message.process():
        data = json.loads(message.body)
        await crud.create_payment(get_db, data)

async def subscribe():
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
    queue_name = "order.create"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)

    # Bind the queue to the exchange
    routing_key = "order.create"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)

    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_message(message)
