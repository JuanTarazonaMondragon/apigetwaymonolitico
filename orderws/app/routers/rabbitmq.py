import aio_pika
import json
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud
from sql import models, schemas

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

async def on_pay_message(message):
    async with message.process():
        payment = json.loads(message.body)
        db = SessionLocal()
        if(payment['payment_status']):
            status= models.Order.STATUS_PAYED
            db_order = await crud.change_order_status(db, payment['id_order'], status)

            for i in range (0,db_order.number_of_pieces):
                piece = schemas.PieceBase(
                    status_piece=models.Piece.STATUS_QUEUED,
                    id_order=db_order.id_order
                    # no se si hay que meter manufacturing date
                )
                await crud.create_piece(db, piece)
            await db.close()
            data = {
                "id_order": db_order.id_order
            }
            message_body = json.dumps(data)
            routing_key = "order.producing"
            await publish(message_body, routing_key)
        else:
            status = models.Order.STATUS_CANCELED
            db_order = await crud.change_order_status(db, payment['id_order'], status)

async def subscribe_payments():
    # Create a queue
    queue_name = "order.payed"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "order.payed"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_pay_message(message)


async def on_piece_message(message):
    async with message.process():
        piece_recieve = json.loads(message.body)
        db = SessionLocal()
        db_piece = await crud.change_piece_status(db, piece_recieve['id_piece'], models.Piece.STATUS_PRODUCED)
        db_pieces = await crud.get_order_pieces(db, piece_recieve['id_order'])
        order_finished = True
        for piece in db_pieces:
            if piece.status_piece == models.Piece.STATUS_QUEUED:
                order_finished = False
                break
        if order_finished:
            db_order = await crud.change_order_status(db, piece_recieve['id_order'], models.Order.STATUS_PRODUCED)
            data = {
                "id_order": piece_recieve['id_order']
            }
            message_body = json.dumps(data)
            routing_key = "order.produced"
            await publish(message_body, routing_key)
        await db.close()


async def subscribe_pieces():
    # Create a queue
    queue_name = "piece.produced"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "piece.produced"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_piece_message(message)


async def on_delivered_message(message):
    async with message.process():
        delivery = json.loads(message.body)
        db = SessionLocal()
        db_piece = await crud.change_order_status(db, delivery['id_order'], models.Order.STATUS_DELIVERED)
        await db.close()


async def subscribe_delivered():
    # Create a queue
    queue_name = "order.delivered"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "order.delivered"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_delivered_message(message)


async def on_delivering_message(message):
    async with message.process():
        delivery = json.loads(message.body)
        db = SessionLocal()
        db_piece = await crud.change_order_status(db, delivery['id_order'], models.Order.STATUS_DELIVERING)
        await db.close()


async def subscribe_delivering():
    # Create a queue
    queue_name = "order.delivering"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)
    # Bind the queue to the exchange
    routing_key = "order.delivering"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)
    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_delivering_message(message)


async def publish(message_body, routing_key):
    # Publish the message to the exchange
    await exchange.publish(
        aio_pika.Message(
            body=message_body.encode(),
            content_type="text/plain"
        ),
        routing_key=routing_key)
