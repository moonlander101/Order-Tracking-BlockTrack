from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException

class Command(BaseCommand):
    help = 'Consume messages from Kafka'
    def handle(self, *args, **kwargs):
        conf = {
            'bootstrap.servers': "localhost:9092",
            'group.id': "order_consumer_group",
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(**conf)
        consumer.subscribe(['orders.delivered'])
        try:
            self.stdout.write(self.style.SUCCESS('Starting consumer...'))
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code():
                        continue
                    else:
                        raise KafkaException(msg.error())
                print('Received message: {}'.format(msg.value().decode('utf-8')))
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()