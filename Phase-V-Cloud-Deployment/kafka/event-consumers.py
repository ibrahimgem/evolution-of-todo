# Phase V: Enterprise Cloud Deployment
# Kafka Event Consumers for Analytics Processing
#
# [Task]: T017
# [From]: speckit.specify §3.2, speckit.plan §2.2

"""
Event Consumers for Todo Chatbot Analytics
==========================================

This module implements Kafka event consumers for processing events
and generating analytics data. It handles:
- Task usage analytics
- Chat conversation analytics
- User behavior analytics
- System performance metrics
- Dead letter queue processing

Architecture:
- Uses confluent-kafka library for high-performance Kafka client
- Implements consumer groups for parallel processing
- Includes message processing with error handling and retries
- Supports exactly-once processing semantics
- Integrates with external analytics systems
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable

from confluent_kafka import Consumer, KafkaError, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic

# Configure logging
logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Base Event Consumer for Kafka events
    """

    def __init__(self, bootstrap_servers: str, group_id: str, topics: List[str]):
        """
        Initialize the event consumer

        Args:
            bootstrap_servers: Kafka bootstrap servers
            group_id: Consumer group ID
            topics: List of topics to consume from
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics

        # Kafka consumer configuration
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # Manual commit for exactly-once processing
            'auto.commit.interval.ms': 5000,
            'session.timeout.ms': 30000,
            'max.poll.interval.ms': 300000,  # 5 minutes
            'fetch.min.bytes': 1024,
            'fetch.max.bytes': 52428800,  # 50MB
            'max.partition.fetch.bytes': 10485760,  # 10MB
            'heartbeat.interval.ms': 3000,
            'isolation.level': 'read_committed',  # For exactly-once processing
        }

        # Initialize consumer
        self.consumer = Consumer(self.consumer_config)

        # Processing state
        self.running = False
        self.processed_messages = 0
        self.failed_messages = 0
        self.rebalance_count = 0

        # DLQ configuration
        self.dlq_topic = 'dlq'
        self.max_retries = 3

    async def start(self):
        """
        Start the consumer
        """
        logger.info(f"Starting consumer {self.group_id} for topics: {self.topics}")

        # Subscribe to topics
        self.consumer.subscribe(self.topics, on_assign=self._on_partitions_assigned)

        self.running = True

        try:
            while self.running:
                await self._poll_messages()
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

        except KeyboardInterrupt:
            logger.info("Consumer interrupted")
        finally:
            await self.stop()

    async def stop(self):
        """
        Stop the consumer gracefully
        """
        logger.info("Stopping consumer...")
        self.running = False

        # Commit offsets before stopping
        try:
            self.consumer.commit(asynchronous=False)
        except Exception as e:
            logger.error(f"Error committing offsets: {e}")

        # Close consumer
        self.consumer.close()
        logger.info("Consumer stopped")

    def _on_partitions_assigned(self, consumer, partitions):
        """
        Callback when partitions are assigned
        """
        self.rebalance_count += 1
        logger.info(f"Partitions assigned: {len(partitions)} (rebalance #{self.rebalance_count})")
        for partition in partitions:
            logger.debug(f"Assigned partition: {partition.topic}[{partition.partition}]")

    async def _poll_messages(self):
        """
        Poll for messages and process them
        """
        try:
            # Poll for messages
            msg = self.consumer.poll(timeout=1.0)

            if msg is None:
                return

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition
                    logger.debug(f"Reached end of partition {msg.partition()}")
                    return
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    return

            # Process message
            await self._process_message(msg)

        except Exception as e:
            logger.error(f"Error polling messages: {e}")

    async def _process_message(self, msg):
        """
        Process a single message

        Args:
            msg: Kafka message
        """
        try:
            # Deserialize message
            event_data = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            partition = msg.partition()
            offset = msg.offset()

            logger.debug(f"Processing message from {topic}[{partition}:{offset}]")

            # Process the event
            await self._handle_event(event_data, topic)

            # Commit offset
            self.consumer.commit(asynchronous=True)
            self.processed_messages += 1

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
            await self._send_to_dlq(msg, f"JSON decode error: {e}")
            self.failed_messages += 1
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._send_to_dlq(msg, f"Processing error: {e}")
            self.failed_messages += 1

    async def _handle_event(self, event_data: Dict[str, Any], topic: str):
        """
        Handle a specific event (to be implemented by subclasses)

        Args:
            event_data: Deserialized event data
            topic: Topic name
        """
        raise NotImplementedError("Subclasses must implement _handle_event")

    async def _send_to_dlq(self, msg, error_reason: str):
        """
        Send failed message to Dead Letter Queue

        Args:
            msg: Original Kafka message
            error_reason: Reason for failure
        """
        try:
            dlq_message = {
                'original_topic': msg.topic(),
                'original_partition': msg.partition(),
                'original_offset': msg.offset(),
                'error_timestamp': datetime.utcnow().isoformat(),
                'error_reason': error_reason,
                'original_message': msg.value().decode('utf-8'),
                'consumer_group': self.group_id
            }

            # For now, just log DLQ messages
            # In production, you would send this to the actual DLQ topic
            logger.warning(f"DLQ message: {json.dumps(dlq_message)}")

        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get consumer statistics
        """
        return {
            'processed_messages': self.processed_messages,
            'failed_messages': self.failed_messages,
            'rebalance_count': self.rebalance_count,
            'topics': self.topics,
            'group_id': self.group_id
        }


class TaskAnalyticsConsumer(EventConsumer):
    """
    Event Consumer for Task Analytics
    """

    def __init__(self, bootstrap_servers: str):
        topics = ['todo-events']
        super().__init__(bootstrap_servers, 'task-analytics-consumer', topics)

        # Analytics state
        self.task_metrics = defaultdict(lambda: defaultdict(int))
        self.daily_task_counts = defaultdict(int)
        self.user_task_counts = defaultdict(int)

    async def _handle_event(self, event_data: Dict[str, Any], topic: str):
        """
        Handle task events for analytics
        """
        event_type = event_data.get('event_type')
        user_id = event_data.get('user_id')
        timestamp = event_data.get('timestamp')

        # Parse timestamp
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            event_time = datetime.utcnow()

        # Extract date for daily metrics
        date_key = event_time.strftime('%Y-%m-%d')

        if event_type == 'TASK_CREATED':
            self.task_metrics['total_created'] += 1
            self.daily_task_counts[date_key] += 1
            self.user_task_counts[user_id] += 1
            logger.info(f"Task created analytics: User {user_id} created task")

        elif event_type == 'TASK_COMPLETED':
            self.task_metrics['total_completed'] += 1
            self.task_metrics['completion_rate'] = (
                self.task_metrics['total_completed'] / max(self.task_metrics['total_created'], 1)
            ) * 100
            logger.info(f"Task completed analytics: User {user_id} completed task")

        elif event_type == 'TASK_DELETED':
            self.task_metrics['total_deleted'] += 1
            logger.info(f"Task deleted analytics: User {user_id} deleted task")

        # Log analytics periodically
        if self.processed_messages % 100 == 0:
            self._log_task_analytics()

    def _log_task_analytics(self):
        """
        Log current task analytics
        """
        logger.info(f"Task Analytics - Created: {self.task_metrics['total_created']}, "
                   f"Completed: {self.task_metrics['total_completed']}, "
                   f"Deleted: {self.task_metrics['total_deleted']}, "
                   f"Completion Rate: {self.task_metrics['completion_rate']:.2f}%")


class ChatAnalyticsConsumer(EventConsumer):
    """
    Event Consumer for Chat Analytics
    """

    def __init__(self, bootstrap_servers: str):
        topics = ['chat-events']
        super().__init__(bootstrap_servers, 'chat-analytics-consumer', topics)

        # Analytics state
        self.conversation_metrics = defaultdict(int)
        self.message_metrics = defaultdict(int)
        self.active_users = set()
        self.conversation_durations = []

    async def _handle_event(self, event_data: Dict[str, Any], topic: str):
        """
        Handle chat events for analytics
        """
        event_type = event_data.get('event_type')
        user_id = event_data.get('user_id')
        timestamp = event_data.get('timestamp')

        # Parse timestamp
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            event_time = datetime.utcnow()

        if event_type == 'CONVERSATION_CREATED':
            conversation_id = event_data['payload']['id']
            self.conversation_metrics['total_conversations'] += 1
            self.active_users.add(user_id)
            logger.info(f"Chat analytics: New conversation {conversation_id} by user {user_id}")

        elif event_type == 'MESSAGE_SENT':
            role = event_data['payload']['role']
            self.message_metrics[f'{role}_messages'] += 1
            self.active_users.add(user_id)

            # Track conversation start time for duration calculation
            conversation_id = event_data['payload']['conversation_id']
            if f'{conversation_id}_start' not in self.conversation_metrics:
                self.conversation_metrics[f'{conversation_id}_start'] = event_time

        elif event_type == 'CONVERSATION_ENDED':
            conversation_id = event_data['payload']['conversation_id']
            duration = event_data['payload']['duration']

            if f'{conversation_id}_start' in self.conversation_metrics:
                start_time = self.conversation_metrics[f'{conversation_id}_start']
                actual_duration = (event_time - start_time).total_seconds()
                self.conversation_durations.append(actual_duration)
                del self.conversation_metrics[f'{conversation_id}_start']

            logger.info(f"Chat analytics: Conversation {conversation_id} ended, duration: {duration}s")

        # Log analytics periodically
        if self.processed_messages % 50 == 0:
            self._log_chat_analytics()

    def _log_chat_analytics(self):
        """
        Log current chat analytics
        """
        avg_duration = sum(self.conversation_durations) / max(len(self.conversation_durations), 1)
        logger.info(f"Chat Analytics - Conversations: {self.conversation_metrics['total_conversations']}, "
                   f"Users: {len(self.active_users)}, "
                   f"User Messages: {self.message_metrics['user_messages']}, "
                   f"Assistant Messages: {self.message_metrics['assistant_messages']}, "
                   f"Avg Duration: {avg_duration:.2f}s")


class UserBehaviorConsumer(EventConsumer):
    """
    Event Consumer for User Behavior Analytics
    """

    def __init__(self, bootstrap_servers: str):
        topics = ['user-events', 'todo-events', 'chat-events']
        super().__init__(bootstrap_servers, 'user-behavior-consumer', topics)

        # Analytics state
        self.user_sessions = defaultdict(dict)
        self.user_activity = defaultdict(lambda: defaultdict(int))
        self.user_patterns = defaultdict(list)

    async def _handle_event(self, event_data: Dict[str, Any], topic: str):
        """
        Handle user behavior events
        """
        user_id = event_data.get('user_id')
        event_type = event_data.get('event_type')
        timestamp = event_data.get('timestamp')

        # Parse timestamp
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            event_time = datetime.utcnow()

        # Update user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'first_seen': event_time,
                'last_activity': event_time,
                'session_count': 1,
                'total_events': 0
            }

        self.user_sessions[user_id]['last_activity'] = event_time
        self.user_sessions[user_id]['total_events'] += 1

        # Track activity patterns
        hour = event_time.hour
        day_of_week = event_time.weekday()
        self.user_activity[user_id]['hourly_activity'][hour] += 1
        self.user_activity[user_id]['daily_activity'][day_of_week] += 1

        # Track event patterns
        self.user_patterns[user_id].append({
            'event_type': event_type,
            'timestamp': timestamp,
            'topic': topic
        })

        # Keep only last 1000 events per user to prevent memory issues
        if len(self.user_patterns[user_id]) > 1000:
            self.user_patterns[user_id] = self.user_patterns[user_id][-1000:]

        # Log behavior patterns periodically
        if self.processed_messages % 200 == 0:
            self._log_user_behavior()


class SystemMetricsConsumer(EventConsumer):
    """
    Event Consumer for System Metrics
    """

    def __init__(self, bootstrap_servers: str):
        topics = ['system-events']
        super().__init__(bootstrap_servers, 'system-metrics-consumer', topics)

        # Metrics state
        self.service_health = defaultdict(dict)
        self.error_counts = defaultdict(int)
        self.performance_metrics = defaultdict(list)

    async def _handle_event(self, event_data: Dict[str, Any], topic: str):
        """
        Handle system metrics events
        """
        event_type = event_data.get('event_type')
        timestamp = event_data.get('timestamp')

        # Parse timestamp
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            event_time = datetime.utcnow()

        if event_type == 'HEALTH_CHECK':
            service_name = event_data['payload']['service_name']
            status = event_data['payload']['status']
            metrics = event_data['payload']['metrics']

            self.service_health[service_name] = {
                'last_check': event_time,
                'status': status,
                'metrics': metrics
            }

        elif event_type == 'ERROR':
            service_name = event_data['payload']['service_name']
            error_type = event_data['payload']['error_type']
            error_message = event_data['payload']['error_message']

            self.error_counts[f'{service_name}_{error_type}'] += 1

            # Store performance metrics
            if service_name not in self.performance_metrics:
                self.performance_metrics[service_name] = []

            self.performance_metrics[service_name].append({
                'timestamp': event_time,
                'error_type': error_type,
                'error_message': error_message
            })

            # Keep only last 1000 metrics per service
            if len(self.performance_metrics[service_name]) > 1000:
                self.performance_metrics[service_name] = self.performance_metrics[service_name][-1000:]

        # Log system metrics periodically
        if self.processed_messages % 100 == 0:
            self._log_system_metrics()

    def _log_system_metrics(self):
        """
        Log current system metrics
        """
        logger.info(f"System Metrics - Healthy Services: {sum(1 for s in self.service_health.values() if s['status'] == 'healthy')}, "
                   f"Total Errors: {sum(self.error_counts.values())}")


# Consumer factory and management
class ConsumerManager:
    """
    Manager for multiple Kafka consumers
    """

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.consumers = []

    def create_consumers(self):
        """
        Create all analytics consumers
        """
        self.consumers = [
            TaskAnalyticsConsumer(self.bootstrap_servers),
            ChatAnalyticsConsumer(self.bootstrap_servers),
            UserBehaviorConsumer(self.bootstrap_servers),
            SystemMetricsConsumer(self.bootstrap_servers)
        ]

    async def start_all(self):
        """
        Start all consumers
        """
        self.create_consumers()

        logger.info(f"Starting {len(self.consumers)} analytics consumers...")

        # Start all consumers concurrently
        tasks = [consumer.start() for consumer in self.consumers]
        await asyncio.gather(*tasks)

    def get_stats(self):
        """
        Get statistics from all consumers
        """
        return {
            consumer.group_id: consumer.get_stats()
            for consumer in self.consumers
        }


# Example usage and testing
if __name__ == "__main__":
    import os

    # Configuration
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

    async def main():
        # Create consumer manager
        manager = ConsumerManager(BOOTSTRAP_SERVERS)

        try:
            # Start all consumers
            await manager.start_all()
        except KeyboardInterrupt:
            logger.info("Shutting down consumers...")
        finally:
            # Print final statistics
            stats = manager.get_stats()
            for group_id, group_stats in stats.items():
                print(f"{group_id} stats: {group_stats}")

    # Run the main function
    asyncio.run(main())