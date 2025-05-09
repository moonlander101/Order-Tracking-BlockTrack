from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
import json

logger = logging.getLogger(__name__)

try:
    kafka_producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5,
        acks='all'  # Wait for all replicas to acknowledge
    )
    logger.info("Kafka producer initialized successfully")
except KafkaError as e:
    kafka_producer = None
    logger.error(f"Failed to initialize Kafka producer: {str(e)}")

def send_to_kafka(topic, data):
    """Helper function to send messages to Kafka with error handling"""
    if not kafka_producer:
        logger.warning("Kafka producer not available, skipping message")
        return False
    
    try:
        future = kafka_producer.send(topic, data)
        # Wait for the message to be delivered
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
        return True
    except KafkaError as e:
        logger.error(f"Failed to send message to Kafka: {str(e)}")
        return False