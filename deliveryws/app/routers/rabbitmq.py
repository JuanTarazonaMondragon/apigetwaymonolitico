import asyncio
import aio_pika
import json
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

async def on_producing_message(message):
    async with message.process():
        delivery = json.loads(message.body)
        db = SessionLocal()
        await crud.create_delivery(db, delivery)
        await db.close()

async def subscribe_producing():
    # Create queue
    queue_name = "order.producing"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "order.producing"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_producing_message(message)

async def on_produced_message(message):
    async with message.process():
        order = json.loads(message.body)
        db = SessionLocal()
        db_delivery = await crud.get_delivery_by_order(db, order['id_order'])
        if db_delivery.status_delivery == models.Delivery.STATUS_CREATED:
            await crud.change_delivery_status(db, db_delivery.id_delivery, models.Delivery.STATUS_PREPARED)
            await db.close()
        elif db_delivery.status_delivery == models.Delivery.STATUS_INFORMED:
            db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery, models.Delivery.STATUS_DELIVERING)
            await db.close()
            asyncio.create_task(send_product(db_delivery))

async def subscribe_produced():
    # Create queue
    queue_name = "order.produced"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "order.produced"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_produced_message(message)

async def publish(message_body, routing_key):
    # Publish the message to the exchange
    await exchange.publish(
        aio_pika.Message(
            body=message_body.encode(),
            content_type="text/plain"
        ),
        routing_key=routing_key)

async def send_product(delivery):
    data = {
        "id_order": delivery.id_order
    }
    message_body = json.dumps(data)
    routing_key = "order.delivering"
    await publish(message_body, routing_key)
    await asyncio.sleep(10)
    db = SessionLocal()
    db_delivery = await crud.get_delivery(db, delivery.id_delivery)
    db_delivery = await crud.change_delivery_status(db, db_delivery.id_delivery, models.Delivery.STATUS_DELIVERED)
    await db.close()
    routing_key = "order.delivered"
    await publish(message_body, routing_key)
