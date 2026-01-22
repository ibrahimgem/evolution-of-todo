# Phase V: Enterprise Cloud Deployment
# Dapr Integration for Event Consumers
#
# [Task]: T029
# [From]: speckit.specify §3.3, speckit.plan §2.3

"""
Dapr Event Consumers for Todo Chatbot
=====================================

This module provides Dapr-integrated event consumers that use Dapr's
pub/sub subscription API. Benefits:
- Declarative subscription management via YAML
- Automatic handling of consumer groups and partitioning
- Built-in dead letter queue support
- Distributed tracing and metrics
- Graceful shutdown and rebalancing
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)


class DaprSubscription:
    """
    Dapr subscription configuration
    """

    def __init__(
        self,
        pubsub: str,
        topic: str,
        route: str,
        metadata: Optional[Dict[str, str]] = None,
        dead_letter_topic: Optional[str] = None
    ):
        """
        Initialize subscription

        Args:
            pubsub: Name of the pub/sub component
            topic: Topic to subscribe to
            route: HTTP route for event delivery
            metadata: Optional subscription metadata
            dead_letter_topic: Topic for failed messages
        """
        self.pubsub = pubsub
        self.topic = topic
        self.route = route
        self.metadata = metadata or {}
        self.dead_letter_topic = dead_letter_topic

    def to_dict(self) -> Dict[str, Any]:
        """Convert to subscription specification"""
        result = {
            "pubsubName": self.pubsub,
            "topic": self.topic,
            "route": self.route,
            "metadata": self.metadata
        }
        if self.dead_letter_topic:
            result["deadLetterTopic"] = self.dead_letter_topic
        return result


class DaprEventConsumer:
    """
    Base Dapr Event Consumer
    """

    def __init__(self, app_port: int = 3000, dapr_port: int = 3500):
        """
        Initialize consumer

        Args:
            app_port: Application HTTP port
            dapr_port: Dapr sidecar HTTP port
        """
        self.app_port = app_port
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0"
        self.subscriptions: List[DaprSubscription] = []
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.session: Optional[aiohttp.ClientSession] = None

    def add_subscription(self, subscription: DaprSubscription):
        """
        Add a subscription

        Args:
            subscription: Subscription configuration
        """
        self.subscriptions.append(subscription)
        logger.info(f"Added subscription: {subscription.pubsub}/{subscription.topic}")

    def register_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], Any]
    ):
        """
        Register an event handler

        Args:
            event_type: Event type to handle
            handler: Async handler function
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    async def start(self):
        """Start the consumer"""
        self.running = True
        self.session = aiohttp.ClientSession()
        logger.info("Dapr event consumer started")

    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Dapr event consumer stopped")

    async def health_check(self) -> bool:
        """
        Health check endpoint for Dapr

        Returns:
            True if healthy
        """
        try:
            async with self.session.get(f"http://localhost:{self.app_port}/healthz") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Publish an event (for dead letter queue)

        Args:
            pubsub_name: Name of the pub/sub component
            topic: Topic name
            data: Event data

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/publish/{pubsub_name}/{topic}"
            payload = {
                "data": data,
                "dataType": "json",
                "contentType": "application/json"
            }

            async with self.session.post(url, json=payload) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    async def handle_event(
        self,
        event_data: Dict[str, Any],
        pubsub: str,
        topic: str
    ) -> bool:
        """
        Handle an incoming event

        Args:
            event_data: Event data from Dapr
            pubsub: Pubsub component name
            topic: Topic name

        Returns:
            True if handled successfully
        """
        try:
            # Extract event payload
            payload = event_data.get('data', event_data)
            event_type = payload.get('event_type', 'UNKNOWN')

            logger.debug(f"Received event: {event_type} from {pubsub}/{topic}")

            # Find and call handler
            handler = self.handlers.get(event_type)
            if handler:
                await handler(payload)
                return True
            else:
                logger.warning(f"No handler for event type: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Error handling event: {e}")
            return False


class DaprTodoAnalyticsConsumer(DaprEventConsumer):
    """
    Dapr Consumer for Todo Analytics
    """

    def __init__(self, app_port: int = 3001, dapr_port: int = 3500):
        super().__init__(app_port, dapr_port)

        # Configure subscriptions
        self.add_subscription(DaprSubscription(
            pubsub="pubsub-kafka",
            topic="todo-events",
            route="/events/todo",
            dead_letter_topic="dlq"
        ))

        # Register event handlers
        self.register_handler("TASK_CREATED", self.handle_task_created)
        self.register_handler("TASK_UPDATED", self.handle_task_updated)
        self.register_handler("TASK_COMPLETED", self.handle_task_completed)
        self.register_handler("TASK_DELETED", self.handle_task_deleted)

        # Analytics state
        self.metrics = {
            'total_created': 0,
            'total_completed': 0,
            'total_deleted': 0,
            'user_task_counts': {}
        }

    async def handle_task_created(self, payload: Dict[str, Any]):
        """Handle task created event"""
        self.metrics['total_created'] += 1

        user_id = payload.get('user_id')
        if user_id:
            self.metrics['user_task_counts'][user_id] = \
                self.metrics['user_task_counts'].get(user_id, 0) + 1

        task_id = payload.get('payload', {}).get('id')
        logger.info(f"Analytics: Task {task_id} created by user {user_id}")

    async def handle_task_updated(self, payload: Dict[str, Any]):
        """Handle task updated event"""
        user_id = payload.get('user_id')
        logger.info(f"Analytics: Task updated by user {user_id}")

    async def handle_task_completed(self, payload: Dict[str, Any]):
        """Handle task completed event"""
        self.metrics['total_completed'] += 1

        user_id = payload.get('user_id')
        task_id = payload.get('payload', {}).get('id')
        logger.info(f"Analytics: Task {task_id} completed by user {user_id}")

    async def handle_task_deleted(self, payload: Dict[str, Any]):
        """Handle task deleted event"""
        self.metrics['total_deleted'] += 1

        user_id = payload.get('user_id')
        task_id = payload.get('payload', {}).get('task_id')
        logger.info(f"Analytics: Task {task_id} deleted by user {user_id}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            **self.metrics,
            'completion_rate': (
                self.metrics['total_completed'] / max(self.metrics['total_created'], 1)
            ) * 100
        }


class DaprChatAnalyticsConsumer(DaprEventConsumer):
    """
    Dapr Consumer for Chat Analytics
    """

    def __init__(self, app_port: int = 3002, dapr_port: int = 3500):
        super().__init__(app_port, dapr_port)

        # Configure subscriptions
        self.add_subscription(DaprSubscription(
            pubsub="pubsub-kafka",
            topic="chat-events",
            route="/events/chat",
            dead_letter_topic="dlq"
        ))

        # Register event handlers
        self.register_handler("MESSAGE_SENT", self.handle_message_sent)
        self.register_handler("CONVERSATION_CREATED", self.handle_conversation_created)
        self.register_handler("CONVERSATION_ENDED", self.handle_conversation_ended)

        # Analytics state
        self.metrics = {
            'total_messages': 0,
            'total_conversations': 0,
            'user_messages': {},
            'assistant_messages': {}
        }

    async def handle_message_sent(self, payload: Dict[str, Any]):
        """Handle message sent event"""
        self.metrics['total_messages'] += 1

        role = payload.get('payload', {}).get('role')
        user_id = payload.get('user_id')

        if role == 'user':
            self.metrics['user_messages'][user_id] = \
                self.metrics['user_messages'].get(user_id, 0) + 1
        elif role == 'assistant':
            self.metrics['assistant_messages'][user_id] = \
                self.metrics['assistant_messages'].get(user_id, 0) + 1

        logger.info(f"Analytics: {role} message from user {user_id}")

    async def handle_conversation_created(self, payload: Dict[str, Any]):
        """Handle conversation created event"""
        self.metrics['total_conversations'] += 1

        user_id = payload.get('user_id')
        conversation_id = payload.get('payload', {}).get('id')
        logger.info(f"Analytics: Conversation {conversation_id} created by user {user_id}")

    async def handle_conversation_ended(self, payload: Dict[str, Any]):
        """Handle conversation ended event"""
        user_id = payload.get('user_id')
        duration = payload.get('payload', {}).get('duration')
        logger.info(f"Analytics: Conversation ended by user {user_id}, duration: {duration}s")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics


class DaprUserBehaviorConsumer(DaprEventConsumer):
    """
    Dapr Consumer for User Behavior Analytics
    """

    def __init__(self, app_port: int = 3003, dapr_port: int = 3500):
        super().__init__(app_port, dapr_port)

        # Configure subscriptions (multiple topics)
        self.add_subscription(DaprSubscription(
            pubsub="pubsub-kafka",
            topic="user-events",
            route="/events/user",
            dead_letter_topic="dlq"
        ))
        self.add_subscription(DaprSubscription(
            pubsub="pubsub-kafka",
            topic="todo-events",
            route="/events/todo-behavior",
            dead_letter_topic="dlq"
        ))
        self.add_subscription(DaprSubscription(
            pubsub="pubsub-kafka",
            topic="chat-events",
            route="/events/chat-behavior",
            dead_letter_topic="dlq"
        ))

        # Register event handlers
        self.register_handler("USER_CREATED", self.handle_user_created)
        self.register_handler("USER_LOGIN", self.handle_user_login)
        self.register_handler("USER_LOGOUT", self.handle_user_logout)
        self.register_handler("TASK_CREATED", self.track_user_activity)
        self.register_handler("MESSAGE_SENT", self.track_user_activity)

        # Behavior tracking state
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_activity: Dict[str, Dict[str, Any]] = {}

    async def handle_user_created(self, payload: Dict[str, Any]):
        """Handle user created event"""
        user_id = payload.get('user_id')
        self.user_sessions[user_id] = {
            'first_seen': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'login_count': 0,
            'events': 0
        }
        logger.info(f"Behavior: New user {user_id} registered")

    async def handle_user_login(self, payload: Dict[str, Any]):
        """Handle user login event"""
        user_id = payload.get('user_id')

        if user_id in self.user_sessions:
            self.user_sessions[user_id]['login_count'] += 1
            self.user_sessions[user_id]['last_activity'] = datetime.utcnow().isoformat()

        logger.info(f"Behavior: User {user_id} logged in")

    async def handle_user_logout(self, payload: Dict[str, Any]):
        """Handle user logout event"""
        user_id = payload.get('user_id')
        logger.info(f"Behavior: User {user_id} logged out")

    async def track_user_activity(self, payload: Dict[str, Any]):
        """Track user activity"""
        user_id = payload.get('user_id')

        if user_id not in self.user_activity:
            self.user_activity[user_id] = {
                'task_count': 0,
                'message_count': 0,
                'last_activity': datetime.utcnow().isoformat()
            }

        event_type = payload.get('event_type')
        if event_type == 'TASK_CREATED':
            self.user_activity[user_id]['task_count'] += 1
        elif event_type == 'MESSAGE_SENT':
            self.user_activity[user_id]['message_count'] += 1

        self.user_activity[user_id]['last_activity'] = datetime.utcnow().isoformat()

    def get_behavior_metrics(self) -> Dict[str, Any]:
        """Get behavior metrics"""
        return {
            'total_users': len(self.user_sessions),
            'active_users': len(self.user_activity),
            'total_sessions': sum(
                session['login_count'] for session in self.user_sessions.values()
            )
        }


# Consumer Factory
class DaprConsumerFactory:
    """
    Factory for creating Dapr consumers
    """

    def __init__(self, dapr_port: int = 3500):
        self.dapr_port = dapr_port
        self.consumers: List[DaprEventConsumer] = []

    def create_todo_consumer(self, app_port: int = 3001) -> DaprTodoAnalyticsConsumer:
        """Create todo analytics consumer"""
        consumer = DaprTodoAnalyticsConsumer(app_port, self.dapr_port)
        self.consumers.append(consumer)
        return consumer

    def create_chat_consumer(self, app_port: int = 3002) -> DaprChatAnalyticsConsumer:
        """Create chat analytics consumer"""
        consumer = DaprChatAnalyticsConsumer(app_port, self.dapr_port)
        self.consumers.append(consumer)
        return consumer

    def create_behavior_consumer(self, app_port: int = 3003) -> DaprUserBehaviorConsumer:
        """Create user behavior consumer"""
        consumer = DaprUserBehaviorConsumer(app_port, self.dapr_port)
        self.consumers.append(consumer)
        return consumer

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all subscriptions for Dapr subscription endpoint"""
        return [sub.to_dict() for sub in self.consumers]

    async def start_all(self):
        """Start all consumers"""
        for consumer in self.consumers:
            await consumer.start()
        logger.info(f"Started {len(self.consumers)} Dapr consumers")

    async def stop_all(self):
        """Stop all consumers"""
        for consumer in self.consumers:
            await consumer.stop()
        logger.info("Stopped all Dapr consumers")


# Subscription Configuration for Dapr
SUBSCRIPTIONS_YAML = """
# Dapr Subscriptions Configuration
# This file should be mounted to /components on the consumer application
apiVersion: dapr.io/v2alpha1
kind: Subscriptions
metadata:
  name: todo-chatbot-subscriptions
  namespace: default
spec:
  subscriptions:
    - pubsubname: pubsub-kafka
      topic: todo-events
      route: /events/todo
      deadLetterTopic: dlq
      metadata:
        consumerID: todo-analytics-consumer
    - pubsubname: pubsub-kafka
      topic: chat-events
      route: /events/chat
      deadLetterTopic: dlq
      metadata:
        consumerID: chat-analytics-consumer
    - pubsubname: pubsub-kafka
      topic: user-events
      route: /events/user
      deadLetterTopic: dlq
      metadata:
        consumerID: user-behavior-consumer
"""

# Write subscriptions YAML
with open('/Users/apple/Data/Certified-Cloud-Applied-Generative-AI-Engineering/Q4-Agentic-AI/ai_driven_development/Hackathons/02-evolution-of-todo/Phase-V-Cloud-Deployment/dapr/subscriptions.yaml', 'w') as f:
    f.write(SUBSCRIPTIONS_YAML)

print("Created subscriptions.yaml for Dapr configuration")


# Example consumer deployment
CONSUMER_DEPLOYMENT_YAML = """
# Dapr Analytics Consumer Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-chatbot-analytics
  namespace: default
  labels:
    app.kubernetes.io/name: todo-chatbot-analytics
    app.kubernetes.io/part-of: todo-chatbot
    app.kubernetes.io/component: analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-chatbot-analytics
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-chatbot-analytics
        app.kubernetes.io/part-of: todo-chatbot
        app.kubernetes.io/component: analytics
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-chatbot-analytics"
        dapr.io/app-port: "3001"
        dapr.io/config: "todo-chatbot-config"
        dapr.io/metrics-port: "9090"
        dapr.io/log-level: "info"
        dapr.io/subscribe-port: "3001"
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      containers:
        - name: analytics
          image: todo-chatbot-analytics:latest
          ports:
            - containerPort: 3001
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
            - name: DAPR_GRPC_PORT
              value: "50001"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
"""

# Write consumer deployment YAML
with open('/Users/apple/Data/Certified-Cloud-Applied-Generative-AI-Engineering/Q4-Agentic-AI/ai_driven_development/Hackathons/02-evolution-of-todo/Phase-V-Cloud-Deployment/dapr/analytics-consumer-deployment.yaml', 'w') as f:
    f.write(CONSUMER_DEPLOYMENT_YAML)

print("Created analytics-consumer-deployment.yaml")


if __name__ == "__main__":
    print("Dapr Event Consumers module created successfully")
    print("\nTo use these consumers:")
    print("1. Create a subscription YAML file")
    print("2. Mount the subscription file to /components")
    print("3. Register event handlers for each event type")
    print("4. Start the consumer and await events")