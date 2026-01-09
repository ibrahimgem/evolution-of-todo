# Phase V: Enterprise Cloud Deployment
# Dapr Integration for Event Producers
#
# [Task]: T028
# [From]: speckit.specify §3.3, speckit.plan §2.3

"""
Dapr Event Producers for Todo Chatbot
=====================================

This module provides Dapr-integrated event producers that use Dapr's
pub/sub building block instead of direct Kafka connections. Benefits:
- Application-level decoupling from message broker
- Automatic retry and dead letter queue handling
- Consistent API across different pub/sub systems
- Built-in observability and metrics
- Load balancing and consumer group management
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)


class DaprClient:
    """
    Async HTTP client for Dapr API
    """

    def __init__(self, dapr_port: int = 3500, app_id: str = None):
        """
        Initialize Dapr client

        Args:
            dapr_port: Dapr sidecar HTTP port (default: 3500)
            app_id: Application ID for service invocation
        """
        self.dapr_port = dapr_port
        self.app_id = app_id
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any],
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a topic using Dapr pub/sub

        Args:
            pubsub_name: Name of the pub/sub component
            topic: Topic name to publish to
            data: Event data (dict, will be JSON serialized)
            content_type: Content type of the data
            metadata: Optional metadata for the event

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/publish/{pubsub_name}/{topic}"

            payload = {
                "data": data,
                "dataType": "json",
                "contentType": content_type
            }

            if metadata:
                payload["metadata"] = metadata

            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Published event to {pubsub_name}/{topic}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Failed to publish event: {response.status} - {error}")
                    return False

        except Exception as e:
            logger.error(f"Error publishing event to {pubsub_name}/{topic}: {e}")
            return False

    async def invoke_method(
        self,
        app_id: str,
        method_name: str,
        data: Optional[Dict[str, Any]] = None,
        http_verb: str = "POST"
    ) -> Dict[str, Any]:
        """
        Invoke a method on another Dapr-enabled service

        Args:
            app_id: Target application ID
            method_name: Method name to invoke
            data: Optional data to send
            http_verb: HTTP verb (GET, POST, PUT, DELETE)

        Returns:
            Response data as dict
        """
        try:
            url = f"{self.base_url}/invoke/{app_id}/method/{method_name}"

            headers = {"Content-Type": "application/json"}

            async with self.session.request(http_verb, url, json=data, headers=headers) as response:
                if response.status in [200, 204]:
                    text = await response.text()
                    if text:
                        return json.loads(text)
                    return {}
                else:
                    error = await response.text()
                    logger.error(f"Failed to invoke method: {response.status} - {error}")
                    return {"error": error, "status": response.status}

        except Exception as e:
            logger.error(f"Error invoking method {app_id}/{method_name}: {e}")
            return {"error": str(e)}

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get state from a state store

        Args:
            store_name: Name of the state store component
            key: State key

        Returns:
            State value or None if not found
        """
        try:
            url = f"{self.base_url}/state/{store_name}/{key}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error = await response.text()
                    logger.error(f"Failed to get state: {response.status} - {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting state from {store_name}/{key}: {e}")
            return None

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Save state to a state store

        Args:
            store_name: Name of the state store component
            key: State key
            value: State value
            metadata: Optional metadata

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/state/{store_name}"

            state = [
                {
                    "key": key,
                    "value": value,
                    "metadata": metadata or {}
                }
            ]

            async with self.session.post(url, json=state) as response:
                if response.status == 204:
                    logger.info(f"Saved state to {store_name}/{key}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Failed to save state: {response.status} - {error}")
                    return False

        except Exception as e:
            logger.error(f"Error saving state to {store_name}/{key}: {e}")
            return False

    async def get_secret(self, secret_store: str, key: str) -> Optional[Dict[str, str]]:
        """
        Get a secret from a secret store

        Args:
            secret_store: Name of the secret store component
            key: Secret key

        Returns:
            Secret value or None if not found
        """
        try:
            url = f"{self.base_url}/secrets/{secret_store}/{key}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Failed to get secret: {response.status} - {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting secret from {secret_store}/{key}: {e}")
            return None


class DaprEventProducer:
    """
    Base Dapr Event Producer
    """

    def __init__(self, dapr_port: int = 3500, pubsub_name: str = "pubsub-kafka"):
        """
        Initialize Dapr event producer

        Args:
            dapr_port: Dapr sidecar HTTP port
            pubsub_name: Name of the pub/sub component
        """
        self.dapr_port = dapr_port
        self.pubsub_name = pubsub_name
        self.client: Optional[DaprClient] = None

    async def start(self):
        """Start the producer"""
        self.client = DaprClient(dapr_port=self.dapr_port)
        await self.client.__aenter__()
        logger.info(f"Dapr event producer started (pubsub: {self.pubsub_name})")

    async def stop(self):
        """Stop the producer"""
        if self.client:
            await self.client.__aexit__(None, None, None)
        logger.info("Dapr event producer stopped")

    async def publish_event(
        self,
        topic: str,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event using Dapr

        Args:
            topic: Topic name
            event_data: Event data
            metadata: Optional metadata

        Returns:
            True if successful
        """
        if not self.client:
            logger.error("Producer not started")
            return False

        return await self.client.publish_event(
            pubsub_name=self.pubsub_name,
            topic=topic,
            data=event_data,
            metadata=metadata
        )


class DaprTodoEventProducer(DaprEventProducer):
    """
    Dapr Event Producer for Todo-related events
    """

    def __init__(self, dapr_port: int = 3500, pubsub_name: str = "pubsub-kafka"):
        super().__init__(dapr_port, pubsub_name)
        self.topic = "todo-events"

    async def produce_task_created(self, task_data: Dict[str, Any], user_id: str):
        """
        Publish task created event

        Args:
            task_data: Task data
            user_id: User who created the task
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': task_data
        }

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'TASK_CREATED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Task created event published for task {task_data['id']}")
        return success

    async def produce_task_updated(self, task_data: Dict[str, Any], user_id: str, changes: Dict[str, Any]):
        """
        Publish task updated event

        Args:
            task_data: Updated task data
            user_id: User who updated the task
            changes: Dictionary of changes
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

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'TASK_UPDATED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Task updated event published for task {task_data['id']}")
        return success

    async def produce_task_completed(self, task_data: Dict[str, Any], user_id: str):
        """
        Publish task completed event

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

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'TASK_COMPLETED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Task completed event published for task {task_data['id']}")
        return success

    async def produce_task_deleted(self, task_id: str, user_id: str):
        """
        Publish task deleted event

        Args:
            task_id: ID of deleted task
            user_id: User who deleted the task
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'TASK_DELETED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {'task_id': task_id}
        }

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'TASK_DELETED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Task deleted event published for task {task_id}")
        return success


class DaprChatEventProducer(DaprEventProducer):
    """
    Dapr Event Producer for Chat-related events
    """

    def __init__(self, dapr_port: int = 3500, pubsub_name: str = "pubsub-kafka"):
        super().__init__(dapr_port, pubsub_name)
        self.topic = "chat-events"

    async def produce_message_sent(self, message_data: Dict[str, Any], user_id: str):
        """
        Publish message sent event

        Args:
            message_data: Message data
            user_id: User who sent the message
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'MESSAGE_SENT',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': message_data
        }

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'MESSAGE_SENT'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Message sent event published for conversation {message_data['conversation_id']}")
        return success

    async def produce_conversation_created(self, conversation_data: Dict[str, Any], user_id: str):
        """
        Publish conversation created event

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

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'CONVERSATION_CREATED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"Conversation created event published for conversation {conversation_data['id']}")
        return success


class DaprUserEventProducer(DaprEventProducer):
    """
    Dapr Event Producer for User-related events
    """

    def __init__(self, dapr_port: int = 3500, pubsub_name: str = "pubsub-kafka"):
        super().__init__(dapr_port, pubsub_name)
        self.topic = "user-events"

    async def produce_user_created(self, user_data: Dict[str, Any]):
        """
        Publish user created event

        Args:
            user_data: User data
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'USER_CREATED',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_data['id'],
            'payload': user_data
        }

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'USER_CREATED'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"User created event published for user {user_data['id']}")
        return success

    async def produce_user_login(self, user_id: str, login_method: str, ip_address: Optional[str] = None):
        """
        Publish user login event

        Args:
            user_id: User ID
            login_method: Login method
            ip_address: User IP address
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'USER_LOGIN',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'payload': {
                'login_method': login_method,
                'ip_address': ip_address
            }
        }

        metadata = {
            'correlation-id': str(uuid.uuid4()),
            'event-type': 'USER_LOGIN'
        }

        success = await self.publish_event(self.topic, event, metadata)
        if success:
            logger.info(f"User login event published for user {user_id}")
        return success


# Factory function
def create_dapr_producers(
    dapr_port: int = 3500,
    pubsub_name: str = "pubsub-kafka"
) -> Dict[str, DaprEventProducer]:
    """
    Create all Dapr event producers

    Args:
        dapr_port: Dapr sidecar HTTP port
        pubsub_name: Name of the pub/sub component

    Returns:
        Dictionary of producers
    """
    return {
        'todo': DaprTodoEventProducer(dapr_port, pubsub_name),
        'chat': DaprChatEventProducer(dapr_port, pubsub_name),
        'user': DaprUserEventProducer(dapr_port, pubsub_name)
    }


# Example usage
async def example_usage():
    """Example of using Dapr event producers"""

    # Create producers
    producers = create_dapr_producers(
        dapr_port=3500,
        pubsub_name="pubsub-kafka"
    )

    # Start all producers
    for producer in producers.values():
        await producer.start()

    try:
        # Publish a task created event
        task_data = {
            'id': str(uuid.uuid4()),
            'title': 'Test Task',
            'description': 'This is a test task',
            'completed': False
        }

        await producers['todo'].produce_task_created(task_data, 'user-123')

        # Publish a message sent event
        message_data = {
            'conversation_id': str(uuid.uuid4()),
            'message_id': str(uuid.uuid4()),
            'role': 'user',
            'content': 'Hello, world!'
        }

        await producers['chat'].produce_message_sent(message_data, 'user-123')

    finally:
        # Stop all producers
        for producer in producers.values():
            await producer.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())
