import aio_pika
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud, models

async def subscribe_channel():
    # Define your RabbitMQ server connection parameters directly as keyword arguments
    connection = await aio_pika.connect_robust(
        host='rabbitmq',
        port=5672,
        virtualhost='/',
        login='user',
        password='user'
    )
    # Create a channel
    global channel
    channel = await connection.channel()
    # Declare the exchange
    global exchange_name
    exchange_name = 'events'
    global exchange
    exchange = await channel.declare_exchange(name=exchange_name, type='topic', durable=True)

async def on_log_message(message):
    async with message.process():
        routing_key = message.routing_key
        data = message.body
        log = models.Log(
            routing_key=routing_key,
            data=data
        )
        db = SessionLocal()
        await crud.create_log(db, log)
        await db.close()

async def subscribe_logs():
    # Create a queue
    queue_name = "logs"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "#"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_log_message(message)
