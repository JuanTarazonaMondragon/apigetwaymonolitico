import aio_pika
import json
from sql.database import SessionLocal # pylint: disable=import-outside-toplevel
from sql import crud
from sql import models, schemas

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
    queue_name = "order.pay"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)

    # Bind the queue to the exchange
    routing_key = "order.pay"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)

    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_pay_message(message)


async def on_piece_message(message):
    async with message.process():
        piece = json.loads(message.body)
        db = SessionLocal() # Esto es una puta guarrada, idea de Andoni, hay que preguntar si es legal o no. Ojo, pero al menos funciona, GRANDE ANDONI!

        db_piece = await crud.change_piece_status(db, piece['id_piece'], models.Piece.STATUS_PRODUCED)
        db_pieces = await crud.get_order_pieces(db,piece['id_order'])
        order_finished = True
        for piece in db_pieces:
            print("en rabbitmq")
            print(piece.status_piece)
            if piece.status_piece == models.Piece.STATUS_QUEUED:
                order_finished = False
                break
        print(order_finished)
        if order_finished:
            db_order = await crud.change_order_status(db, piece['id_order'], models.Order.STATUS_PRODUCED)
            data = {
                "id_order": piece['id_order']
            }
            message_body = json.dumps(data)
            routing_key = "order.produced"
            await publish(message_body, routing_key)
        await db.close()


async def subscribe_pieces():
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
    queue_name = "piece.produced"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)

    # Bind the queue to the exchange
    routing_key = "piece.produced"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)

    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_piece_message(message)


async def on_delivery_message(message):
    async with message.process():
        delivery = json.loads(message.body)
        db = SessionLocal() # Esto es una puta guarrada, idea de Andoni, hay que preguntar si es legal o no. Ojo, pero al menos funciona, GRANDE ANDONI!
        db_piece = await crud.change_order_status(db, delivery['id_order'], delivery['delivery_status'])

        await db.close()


async def subscribe_delivery():
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
    queue_name = "order.delivery"
    queue = await channel.declare_queue(name=queue_name, exclusive=True)

    # Bind the queue to the exchange
    routing_key = "order.delivery"
    await queue.bind(exchange=exchange_name, routing_key=routing_key)

    # Set up a message consumer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await on_delivery_message(message)


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
        routing_key=routing_key
    )
