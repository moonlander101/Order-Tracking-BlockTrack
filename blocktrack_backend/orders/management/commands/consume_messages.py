import json
from django.conf import settings
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaException
from orders.utils import update_order_status

class Command(BaseCommand):
    help = 'Consume messages from Kafka'
    def handle(self, *args, **kwargs):
        conf = {
            'bootstrap.servers': settings.KAFKA_BROKER_URL,
            'group.id': "order_consumer_group",
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(**conf)
        consumer.subscribe(['shipment.status.updated'])
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
                data = msg.value().decode('utf-8')
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    self.stdout.write(self.style.ERROR(f'Not a valid json message: {data}'))
                    continue


                order_id = data.get('order_id')
                timestamp = data.get('timestamp')
                status = data.get('status')

                if (not order_id or not timestamp or not status):
                    self.stdout.write(self.style.ERROR(f'Invalid Data: {data}'))
                    continue

                update_order_status(order_id, status, timestamp)
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()