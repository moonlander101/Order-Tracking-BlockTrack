from confluent_kafka import Producer, KafkaException
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

try:
    kafka_producer = Producer({
        'bootstrap.servers': settings.KAFKA_BROKER_URL,
        'security.protocol': 'PLAINTEXT',
        'acks': 'all',
        'retries': 5
    })
    logger.info("Kafka producer initialized successfully")
except KafkaException as e:
    kafka_producer = None
    logger.error(f"Failed to initialize Kafka producer: {str(e)}")

def send_to_kafka(topic, data):
    if not kafka_producer:
        logger.warning("Kafka producer not available, skipping message")
        return False

    try:
        kafka_producer.produce(topic, value=json.dumps(data).encode('utf-8'), callback=delivery_report)
        kafka_producer.flush()
        return True
    except KafkaException as e:
        logger.error(f"Failed to send message to Kafka: {str(e)}")
        return False
