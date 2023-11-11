import aio_pika
import json
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud

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
    global exchange_event_name
    exchange_event_name = 'events'
    global exchange_event
    exchange_event = await channel.declare_exchange(name=exchange_event_name, type='topic', durable=True)
    
    global exchange_command_name
    exchange_command_name = 'commands'
    global exchange_command
    exchange_command = await channel.declare_exchange(name=exchange_command_name, type='topic', durable=True)
    
    global exchange_response_name
    exchange_response_name = 'responses'
    global exchange_response
    exchange_response = await channel.declare_exchange(name=exchange_response_name, type='topic', durable=True)


async def on_message_payment_check(message):
    async with message.process():
        payment = json.loads(message.body)
        db = SessionLocal()
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
            "status": payment_status
        }
        message_body = json.dumps(data)
        routing_key = "payment.checked"
        await publish_response(message_body, routing_key)


async def subscribe_payment_check():
    # Create queue
    queue_name = "payment.check"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "payment.check"
    await queue.bind(exchange=exchange_command_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_message_payment_check(message)


async def publish_event(message_body, routing_key):
    # Publish the message to the exchange
    await exchange_event.publish(
        aio_pika.Message(
            body=message_body.encode(),
            content_type="text/plain"
        ),
        routing_key=routing_key)


async def publish_response(message_body, routing_key):
    # Publish the message to the exchange
    await exchange_response.publish(
        aio_pika.Message(
            body=message_body.encode(),
            content_type="text/plain"
        ),
        routing_key=routing_key)
