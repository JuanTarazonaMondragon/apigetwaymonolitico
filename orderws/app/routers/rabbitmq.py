import aio_pika

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
