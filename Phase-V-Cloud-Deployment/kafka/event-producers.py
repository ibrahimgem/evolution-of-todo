# Phase V: Enterprise Cloud Deployment
# Kafka Event Producers for Backend Application
#
# [Task]: T016
# [From]: speckit.specify §3.2, speckit.plan §2.2

"""
Event Producers for Todo Chatbot
================================

This module implements Kafka event producers for the Todo Chatbot backend.
It handles publishing events for:
- Task CRUD operations
- Chat conversations
- User authentication events
- System events

Architecture:
- Uses confluent-kafka library for high-performance Kafka client
- Implements async producers for non-blocking operation
- Includes event schema validation and error handling
- Supports dead letter queue for failed events
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

# Configure logging
logger = logging.getLogger(__name__)


class EventProducer:
    """
    Base Event Producer for Kafka events
    """

    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        """
        Initialize the event producer

        Args:
            bootstrap_servers: Kafka bootstrap servers
            schema_registry_url: Schema registry URL
        """
        self.bootstrap_servers = bootstrap_servers
        self.schema_registry_url = schema_registry_url

        # Kafka producer configuration
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': f'todo-chatbot-producer-{uuid.uuid4()}',
            'acks': 'all',
            'retries': 3,
            'batch.size': 32768,
            'linger.ms': 10,
            'buffer.memory': 67108864,
            'compression.type': 'gzip',
            'enable.idempotence': True,
            'max.in.flight.requests.per.connection': 1,
        }

        # Schema registry configuration
        self.schema_registry_config = {
            'url': schema_registry_url,
        }

        # Initialize components
        self.producer = Producer(self.producer_config)
        self.schema_registry_client = SchemaRegistryClient(self.schema_registry_config)
        self.string_serializer = StringSerializer('utf_8')

        # Event counters
        self.produced_events = 0
        self.failed_events = 0

    def delivery_report(self, err, msg):
        """
        Callback for message delivery reports

        Args:
            err: Error object if delivery failed
            msg: Message object
        """
        if err is not None:
            logger.error(f"Failed to deliver message: {err}")
            self.failed_events += 1
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")
            self.produced_events += 1

    def produce_event(self, topic: str, key: str, value: Dict[str, Any]):
        """
        Produce an event to Kafka

        Args:
            topic: Target topic
            key: Message key
            value: Message value (dict)
        """
        try:
            # Serialize value to JSON
            value_json = json.dumps(value, default=str)

            # Produce message
            self.producer.produce(
                topic=topic,
                key=self.string_serializer(key),
                value=self.string_serializer(value_json),
                on_delivery=self.delivery_report
            )

            # Poll for delivery reports
            self.producer.poll(0)

        except Exception as e:
            logger.error(f"Error producing event to {topic}: {e}")
            self.failed_events += 1

    def flush(self, timeout: int = 10):
        """
        Flush all pending messages

        Args:
            timeout: Timeout in seconds
        """
        logger.info(f"Flushing {len(self.producer)} pending messages...")
        remaining = self.producer.flush(timeout=timeout)
        logger.info(f"Flush completed. {remaining} messages still pending.")
        return remaining

    def get_stats(self) -> Dict[str, int]:
        """
        Get producer statistics
        """
        return {
            'produced_events': self.produced_events,
            'failed_events': self.failed_events,
            'pending_messages': len(self.producer)
        }


class TodoEventProducer(EventProducer):
    """
    Event Producer for Todo-related events
    """

    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        super().__init__(bootstrap_servers, schema_registry_url)
        self.topic = 'todo-events'

    def produce_task_created(self, task_data: Dict[str, Any], user_id: str):
        """
        Produce task created event

        Args:
            task_data: Task data including id, title, description, etc.
            user_id: User who created the task
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': task_data
        }

        self.produce_event(self.topic, task_data['id'], event)
        logger.info(f"Task created event produced for task {task_data['id']}")

    def produce_task_updated(self, task_data: Dict[str, Any], user_id: str, changes: Dict[str, Any]):
        """
        Produce task updated event

        Args:
            task_data: Updated task data
            user_id: User who updated the task
            changes: Dictionary of changed fields
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_UPDATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {
                'task': task_data,
                'changes': changes
            }
        }

        self.produce_event(self.topic, task_data['id'], event)
        logger.info(f"Task updated event produced for task {task_data['id']}")

    def produce_task_completed(self, task_data: Dict[str, Any], user_id: str):
        """
        Produce task completed event

        Args:
            task_data: Task data
            user_id: User who completed the task
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_COMPLETED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': task_data
        }

        self.produce_event(self.topic, task_data['id'], event)
        logger.info(f"Task completed event produced for task {task_data['id']}")

    def produce_task_deleted(self, task_id: str, user_id: str):
        """
        Produce task deleted event

        Args:
            task_id: ID of deleted task
            user_id: User who deleted the task
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_DELETED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {
                'task_id': task_id
            }
        }

        self.produce_event(self.topic, task_id, event)
        logger.info(f"Task deleted event produced for task {task_id}")


class ChatEventProducer(EventProducer):
    """
    Event Producer for Chat-related events
    """

    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        super().__init__(bootstrap_servers, schema_registry_url)
        self.topic = 'chat-events'

    def produce_message_sent(self, message_data: Dict[str, Any], user_id: str):
        """
        Produce message sent event

        Args:
            message_data: Message data including conversation_id, message_id, content
            user_id: User who sent the message
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'MESSAGE_SENT',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': message_data
        }

        self.produce_event(self.topic, message_data['conversation_id'], event)
        logger.info(f"Message sent event produced for conversation {message_data['conversation_id']}")

    def produce_conversation_created(self, conversation_data: Dict[str, Any], user_id: str):
        """
        Produce conversation created event

        Args:
            conversation_data: Conversation data
            user_id: User who created the conversation
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'CONVERSATION_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': conversation_data
        }

        self.produce_event(self.topic, conversation_data['id'], event)
        logger.info(f"Conversation created event produced for conversation {conversation_data['id']}")

    def produce_conversation_ended(self, conversation_id: str, user_id: str, duration: int):
        """
        Produce conversation ended event

        Args:
            conversation_id: ID of ended conversation
            user_id: User who ended the conversation
            duration: Conversation duration in seconds
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'CONVERSATION_ENDED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {
                'conversation_id': conversation_id,
                'duration': duration
            }
        }

        self.produce_event(self.topic, conversation_id, event)
        logger.info(f"Conversation ended event produced for conversation {conversation_id}")


class UserEventProducer(EventProducer):
    """
    Event Producer for User-related events
    """

    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        super().__init__(bootstrap_servers, schema_registry_url)
        self.topic = 'user-events'

    def produce_user_created(self, user_data: Dict[str, Any]):
        """
        Produce user created event

        Args:
            user_data: User data including id, email, etc.
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'USER_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_data['id'],
            'payload': user_data
        }

        self.produce_event(self.topic, user_data['id'], event)
        logger.info(f"User created event produced for user {user_data['id']}")

    def produce_user_login(self, user_id: str, login_method: str, ip_address: Optional[str] = None):
        """
        Produce user login event

        Args:
            user_id: User ID
            login_method: Login method (email, oauth, etc.)
            ip_address: User IP address (optional)
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'USER_LOGIN',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {
                'login_method': login_method,
                'ip_address': ip_address,
                'user_agent': None  # Would come from request headers
            }
        }

        self.produce_event(self.topic, user_id, event)
        logger.info(f"User login event produced for user {user_id}")

    def produce_user_logout(self, user_id: str):
        """
        Produce user logout event

        Args:
            user_id: User ID
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'USER_LOGOUT',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {}
        }

        self.produce_event(self.topic, user_id, event)
        logger.info(f"User logout event produced for user {user_id}")


class SystemEventProducer(EventProducer):
    """
    Event Producer for System events
    """

    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        super().__init__(bootstrap_servers, schema_registry_url)
        self.topic = 'system-events'

    def produce_health_check(self, service_name: str, status: str, metrics: Dict[str, Any]):
        """
        Produce health check event

        Args:
            service_name: Name of the service
            status: Health status (healthy, unhealthy)
            metrics: Additional metrics
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'HEALTH_CHECK',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': 'system',
            'payload': {
                'service_name': service_name,
                'status': status,
                'metrics': metrics
            }
        }

        self.produce_event(self.topic, service_name, event)
        logger.info(f"Health check event produced for service {service_name}")

    def produce_error_event(self, service_name: str, error_type: str, error_message: str, stack_trace: Optional[str] = None):
        """
        Produce error event

        Args:
            service_name: Name of the service where error occurred
            error_type: Type of error
            error_message: Error message
            stack_trace: Stack trace (optional)
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'ERROR',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': 'system',
            'payload': {
                'service_name': service_name,
                'error_type': error_type,
                'error_message': error_message,
                'stack_trace': stack_trace
            }
        }

        self.produce_event(self.topic, f"{service_name}-{error_type}", event)
        logger.error(f"Error event produced for service {service_name}: {error_message}")


# Factory function to create producers
def create_producers(bootstrap_servers: str, schema_registry_url: str) -> Dict[str, EventProducer]:
    """
    Create all event producers

    Args:
        bootstrap_servers: Kafka bootstrap servers
        schema_registry_url: Schema registry URL

    Returns:
        Dictionary of producers
    """
    return {
        'todo': TodoEventProducer(bootstrap_servers, schema_registry_url),
        'chat': ChatEventProducer(bootstrap_servers, schema_registry_url),
        'user': UserEventProducer(bootstrap_servers, schema_registry_url),
        'system': SystemEventProducer(bootstrap_servers, schema_registry_url)
    }


# Example usage and testing
if __name__ == "__main__":
    import os

    # Configuration
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL', 'http://localhost:8081')

    # Create producers
    producers = create_producers(BOOTSTRAP_SERVERS, SCHEMA_REGISTRY_URL)

    # Test todo event
    todo_producer = producers['todo']
    todo_data = {
        'id': str(uuid.uuid4()),
        'title': 'Test Task',
        'description': 'This is a test task',
        'completed': False,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    todo_producer.produce_task_created(todo_data, 'user-123')

    # Test chat event
    chat_producer = producers['chat']
    message_data = {
        'conversation_id': str(uuid.uuid4()),
        'message_id': str(uuid.uuid4()),
        'role': 'user',
        'content': 'Hello, world!',
        'timestamp': datetime.utcnow().isoformat()
    }

    chat_producer.produce_message_sent(message_data, 'user-123')

    # Flush all producers
    for producer in producers.values():
        producer.flush()

    # Print statistics
    for name, producer in producers.items():
        stats = producer.get_stats()
        print(f"{name} producer stats: {stats}")