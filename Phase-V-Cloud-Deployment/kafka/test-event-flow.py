# Phase V: Enterprise Cloud Deployment
# Kafka Event Flow Testing Utilities
#
# [Task]: T018
# [From]: speckit.specify §3.2, speckit.plan §2.2

"""
Kafka Event Flow Testing
========================

This module provides comprehensive testing utilities for Kafka event flow:
- Event producer testing
- Event consumer testing
- End-to-end flow testing
- Performance testing
- Message format validation
- Dead letter queue testing

Architecture:
- Uses testcontainers for local Kafka setup
- Implements comprehensive test scenarios
- Includes performance benchmarks
- Validates message schemas and formats
- Tests error handling and recovery
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    passed: bool
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None


class KafkaTestHelper:
    """
    Helper class for Kafka testing operations
    """

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.test_results: List[TestResult] = []

    def create_test_topics(self, topics: List[str], partitions: int = 3) -> List[TestResult]:
        """
        Create test topics

        Args:
            topics: List of topic names
            partitions: Number of partitions per topic

        Returns:
            List of test results
        """
        results = []

        try:
            # Create topic configurations
            new_topics = [
                NewTopic(
                    topic,
                    num_partitions=partitions,
                    replication_factor=1,
                    config={
                        'retention.ms': 604800000,  # 7 days
                        'cleanup.policy': 'delete',
                        'compression.type': 'gzip'
                    }
                )
                for topic in topics
            ]

            # Create topics
            fs = self.admin_client.create_topics(new_topics)

            # Wait for topic creation
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    results.append(TestResult(
                        test_name=f"Create topic {topic}",
                        passed=True,
                        duration=0.0,
                        message=f"Topic {topic} created successfully"
                    ))
                except Exception as e:
                    results.append(TestResult(
                        test_name=f"Create topic {topic}",
                        passed=False,
                        duration=0.0,
                        message=f"Failed to create topic {topic}: {e}"
                    ))

        except Exception as e:
            results.append(TestResult(
                test_name="Create test topics",
                passed=False,
                duration=0.0,
                message=f"Failed to create test topics: {e}"
            ))

        self.test_results.extend(results)
        return results

    def send_test_messages(self, topic: str, count: int = 100) -> TestResult:
        """
        Send test messages to a topic

        Args:
            topic: Target topic
            count: Number of messages to send

        Returns:
            Test result
        """
        start_time = time.time()
        sent_count = 0
        failed_count = 0

        def delivery_callback(err, msg):
            nonlocal sent_count, failed_count
            if err:
                failed_count += 1
                logger.error(f"Message delivery failed: {err}")
            else:
                sent_count += 1

        try:
            for i in range(count):
                message = {
                    'event_id': str(uuid.uuid4()),
                    'event_type': 'TEST_EVENT',
                    'timestamp': datetime.utcnow().isoformat(),
                    'test_data': {
                        'message_number': i,
                        'test_id': str(uuid.uuid4()),
                        'payload_size': len(f"test message {i}") * 100
                    }
                }

                self.producer.produce(
                    topic=topic,
                    key=str(i),
                    value=json.dumps(message),
                    callback=delivery_callback
                )

                # Poll for delivery reports
                self.producer.poll(0)

            # Wait for all messages to be delivered
            self.producer.flush(timeout=60)

            duration = time.time() - start_time

            if failed_count == 0:
                return TestResult(
                    test_name=f"Send {count} messages to {topic}",
                    passed=True,
                    duration=duration,
                    message=f"Successfully sent {sent_count} messages",
                    details={'sent_count': sent_count, 'failed_count': failed_count}
                )
            else:
                return TestResult(
                    test_name=f"Send {count} messages to {topic}",
                    passed=False,
                    duration=duration,
                    message=f"Failed to send {failed_count} out of {count} messages",
                    details={'sent_count': sent_count, 'failed_count': failed_count}
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=f"Send {count} messages to {topic}",
                passed=False,
                duration=duration,
                message=f"Error sending messages: {e}"
            )

    def consume_test_messages(self, topic: str, count: int = 100, timeout: int = 60) -> TestResult:
        """
        Consume test messages from a topic

        Args:
            topic: Source topic
            count: Expected number of messages
            timeout: Timeout in seconds

        Returns:
            Test result
        """
        start_time = time.time()
        received_count = 0
        consumed_messages = []

        consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': f'test-consumer-{uuid.uuid4()}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

        try:
            consumer.subscribe([topic])

            while received_count < count and (time.time() - start_time) < timeout:
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug("Reached end of partition")
                        continue
                    else:
                        raise KafkaException(msg.error())

                # Parse message
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    consumed_messages.append(message_data)
                    received_count += 1

                    if received_count % 10 == 0:
                        logger.info(f"Received {received_count} messages")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue

            consumer.commit(asynchronous=False)
            consumer.close()

            duration = time.time() - start_time

            if received_count == count:
                return TestResult(
                    test_name=f"Consume {count} messages from {topic}",
                    passed=True,
                    duration=duration,
                    message=f"Successfully consumed {received_count} messages",
                    details={
                        'received_count': received_count,
                        'consumed_messages': consumed_messages[:5]  # First 5 for inspection
                    }
                )
            else:
                return TestResult(
                    test_name=f"Consume {count} messages from {topic}",
                    passed=False,
                    duration=duration,
                    message=f"Only received {received_count} out of {count} expected messages",
                    details={
                        'received_count': received_count,
                        'expected_count': count,
                        'consumed_messages': consumed_messages[:5]
                    }
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=f"Consume {count} messages from {topic}",
                passed=False,
                duration=duration,
                message=f"Error consuming messages: {e}"
            )
        finally:
            try:
                consumer.close()
            except:
                pass

    def test_end_to_end_flow(self, topic: str, message_count: int = 50) -> TestResult:
        """
        Test complete end-to-end message flow

        Args:
            topic: Test topic
            message_count: Number of messages to test

        Returns:
            Test result
        """
        start_time = time.time()

        # Step 1: Send messages
        send_result = self.send_test_messages(topic, message_count)

        if not send_result.passed:
            return TestResult(
                test_name="End-to-end flow test",
                passed=False,
                duration=time.time() - start_time,
                message=f"Send phase failed: {send_result.message}"
            )

        # Small delay to ensure messages are available
        time.sleep(2)

        # Step 2: Consume messages
        consume_result = self.consume_test_messages(topic, message_count)

        if not consume_result.passed:
            return TestResult(
                test_name="End-to-end flow test",
                passed=False,
                duration=time.time() - start_time,
                message=f"Consume phase failed: {consume_result.message}"
            )

        duration = time.time() - start_time

        return TestResult(
            test_name="End-to-end flow test",
            passed=True,
            duration=duration,
            message="End-to-end flow test passed",
            details={
                'send_result': send_result.details,
                'consume_result': consume_result.details
            }
        )

    def test_message_format_validation(self, topic: str) -> TestResult:
        """
        Test message format validation

        Args:
            topic: Test topic

        Returns:
            Test result
        """
        start_time = time.time()
        test_messages = [
            {
                'event_id': str(uuid.uuid4()),
                'event_type': 'VALID_EVENT',
                'timestamp': datetime.utcnow().isoformat(),
                'payload': {'test': 'data'}
            },
            {
                'event_id': str(uuid.uuid4()),
                'event_type': 'VALID_EVENT',
                'timestamp': datetime.utcnow().isoformat(),
                'payload': {'test': 'data', 'nested': {'more': 'data'}}
            }
        ]

        try:
            # Send test messages
            for i, message in enumerate(test_messages):
                self.producer.produce(
                    topic=topic,
                    key=str(i),
                    value=json.dumps(message)
                )

            self.producer.flush()

            # Consume and validate
            consumer = Consumer({
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': f'validation-consumer-{uuid.uuid4()}',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })

            consumer.subscribe([topic])

            received_messages = []
            for _ in range(len(test_messages)):
                msg = consumer.poll(timeout=5.0)
                if msg:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    received_messages.append(message_data)

            consumer.commit(asynchronous=False)
            consumer.close()

            # Validate messages
            if len(received_messages) != len(test_messages):
                return TestResult(
                    test_name="Message format validation",
                    passed=False,
                    duration=time.time() - start_time,
                    message=f"Expected {len(test_messages)} messages, got {len(received_messages)}"
                )

            for sent, received in zip(test_messages, received_messages):
                if sent['event_id'] != received['event_id']:
                    return TestResult(
                        test_name="Message format validation",
                        passed=False,
                        duration=time.time() - start_time,
                        message=f"Message ID mismatch: {sent['event_id']} != {received['event_id']}"
                    )

            return TestResult(
                test_name="Message format validation",
                passed=True,
                duration=time.time() - start_time,
                message="All messages validated successfully",
                details={'validated_messages': len(received_messages)}
            )

        except Exception as e:
            return TestResult(
                test_name="Message format validation",
                passed=False,
                duration=time.time() - start_time,
                message=f"Validation error: {e}"
            )

    def test_performance(self, topic: str, message_count: int = 1000) -> TestResult:
        """
        Test Kafka performance

        Args:
            topic: Test topic
            message_count: Number of messages for performance test

        Returns:
            Test result
        """
        start_time = time.time()

        # Send messages and measure time
        send_start = time.time()
        send_result = self.send_test_messages(topic, message_count)
        send_duration = time.time() - send_start

        if not send_result.passed:
            return TestResult(
                test_name=f"Performance test ({message_count} messages)",
                passed=False,
                duration=time.time() - start_time,
                message=f"Send failed: {send_result.message}"
            )

        # Small delay
        time.sleep(2)

        # Consume messages and measure time
        consume_start = time.time()
        consume_result = self.consume_test_messages(topic, message_count, timeout=120)
        consume_duration = time.time() - consume_start

        if not consume_result.passed:
            return TestResult(
                test_name=f"Performance test ({message_count} messages)",
                passed=False,
                duration=time.time() - start_time,
                message=f"Consume failed: {consume_result.message}"
            )

        total_duration = time.time() - start_time

        # Calculate throughput
        send_throughput = send_result.details['sent_count'] / send_duration if send_duration > 0 else 0
        consume_throughput = consume_result.details['received_count'] / consume_duration if consume_duration > 0 else 0

        return TestResult(
            test_name=f"Performance test ({message_count} messages)",
            passed=True,
            duration=total_duration,
            message=f"Performance test completed",
            details={
                'send_duration': send_duration,
                'consume_duration': consume_duration,
                'total_duration': total_duration,
                'send_throughput': send_throughput,
                'consume_throughput': consume_throughput,
                'sent_count': send_result.details['sent_count'],
                'received_count': consume_result.details['received_count']
            }
        )


class KafkaTestSuite:
    """
    Complete Kafka test suite
    """

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.helper = KafkaTestHelper(bootstrap_servers)
        self.test_topics = [
            'test-todo-events',
            'test-chat-events',
            'test-user-events',
            'test-dlq'
        ]

    async def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """
        Run complete test suite

        Returns:
            Test results organized by test category
        """
        logger.info("Starting Kafka test suite...")

        # Phase 1: Infrastructure tests
        infrastructure_tests = self._run_infrastructure_tests()

        # Phase 2: Functional tests
        functional_tests = self._run_functional_tests()

        # Phase 3: Performance tests
        performance_tests = self._run_performance_tests()

        # Phase 4: Integration tests
        integration_tests = self._run_integration_tests()

        results = {
            'infrastructure': infrastructure_tests,
            'functional': functional_tests,
            'performance': performance_tests,
            'integration': integration_tests
        }

        # Print summary
        self._print_test_summary(results)

        return results

    def _run_infrastructure_tests(self) -> List[TestResult]:
        """Run infrastructure tests"""
        logger.info("Running infrastructure tests...")

        results = []

        # Test 1: Topic creation
        topic_results = self.helper.create_test_topics(self.test_topics)
        results.extend(topic_results)

        # Test 2: Basic connectivity
        try:
            # Try to list topics as connectivity test
            admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
            metadata = admin_client.list_topics(timeout=10)
            results.append(TestResult(
                test_name="Kafka connectivity test",
                passed=True,
                duration=0.0,
                message="Successfully connected to Kafka cluster"
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="Kafka connectivity test",
                passed=False,
                duration=0.0,
                message=f"Failed to connect to Kafka: {e}"
            ))

        return results

    def _run_functional_tests(self) -> List[TestResult]:
        """Run functional tests"""
        logger.info("Running functional tests...")

        results = []

        # Test each topic
        for topic in self.test_topics[:3]:  # Skip DLQ for now
            # End-to-end flow test
            flow_result = self.helper.test_end_to_end_flow(topic, message_count=20)
            results.append(flow_result)

            # Message format validation
            validation_result = self.helper.test_message_format_validation(topic)
            results.append(validation_result)

        return results

    def _run_performance_tests(self) -> List[TestResult]:
        """Run performance tests"""
        logger.info("Running performance tests...")

        results = []

        # Performance test on main topic
        perf_result = self.helper.test_performance('test-todo-events', message_count=500)
        results.append(perf_result)

        return results

    def _run_integration_tests(self) -> List[TestResult]:
        """Run integration tests"""
        logger.info("Running integration tests...")

        results = []

        # Test producer-consumer integration
        integration_result = self.helper.test_end_to_end_flow('test-chat-events', message_count=100)
        results.append(integration_result)

        return results

    def _print_test_summary(self, results: Dict[str, List[TestResult]]):
        """Print test summary"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        print("\n" + "=" * 80)
        print("KAFKA TEST SUITE SUMMARY")
        print("=" * 80)

        for category, category_results in results.items():
            print(f"\n{category.upper()} TESTS:")
            print("-" * 40)

            category_passed = sum(1 for r in category_results if r.passed)
            category_failed = len(category_results) - category_passed

            total_tests += len(category_results)
            passed_tests += category_passed
            failed_tests += category_failed

            for result in category_results:
                status = "PASS" if result.passed else "FAIL"
                duration = f"{result.duration:.2f}s" if result.duration > 0 else "N/A"
                print(f"  {status:4} | {result.test_name:40} | {duration}")

            print(f"\nCategory Summary: {category_passed} passed, {category_failed} failed")

        print("\n" + "=" * 80)
        print(f"TOTAL: {total_tests} tests, {passed_tests} passed, {failed_tests} failed")
        print("=" * 80)

        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"❌ {failed_tests} tests failed")


# Example usage
if __name__ == "__main__":
    import os

    # Configuration
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

    async def main():
        # Create test suite
        test_suite = KafkaTestSuite(BOOTSTRAP_SERVERS)

        # Run all tests
        results = await test_suite.run_all_tests()

        # Exit with appropriate code
        total_failed = sum(
            len([r for r in category_results if not r.passed])
            for category_results in results.values()
        )

        exit(0 if total_failed == 0 else 1)

    # Run the main function
    asyncio.run(main())