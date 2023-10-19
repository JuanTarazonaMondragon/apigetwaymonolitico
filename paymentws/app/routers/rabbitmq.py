import aio_pika
import json
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud

async def on_message(message):
    async with message.process():
        payment = json.loads(message.body)
        db = SessionLocal() # Esto es una puta guarrada, idea de Andoni, hay que preguntar si es legal o no. Ojo, pero al menos funciona, GRANDE ANDONI!
        try:
            db_payment = await crud.create_payment(db, payment)
            # Crear evento con payment de ID order correcto
            payment_status = True
        except Exception as exc:  # @ToDo: To broad exception
            # Crear evento con payment de ID order incorrecto
            payment_status = False
        await db.close()
        data = {
            "id_order": payment['id_order'],
            "payment_status": payment_status
        }
        message_body = json.dumps(data)
        routing_key = "order.pay"
        await publish(message_body, routing_key)

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

async def publish(message_body, routing_key):
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
    # Publish the message to the exchange
    await exchange.publish(
        aio_pika.Message(
            body=message_body.encode(),
            content_type="text/plain"
        ),
        routing_key=routing_key)
