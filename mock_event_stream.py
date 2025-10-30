"""
Mock Event Stream - Simulates Kafka without requiring actual Kafka setup
Provides a simple queue-based interface that candidates can consume from
"""

import json
import queue
import threading
import time
from datetime import datetime
from typing import Optional, Dict, List
from event_generator import RestaurantEventGenerator


class MockKafkaConsumer:
    """
    Mock Kafka consumer that reads from an in-memory queue
    Simulates the kafka-python Consumer interface
    """
    
    def __init__(self, topics: List[str], **kwargs):
        self.topics = topics
        self.queue = queue.Queue(maxsize=1000)
        self.running = False
        self.generator_thread = None
        self.auto_offset_reset = kwargs.get('auto_offset_reset', 'latest')
        self.group_id = kwargs.get('group_id', 'test-group')
        
        print(f"MockKafkaConsumer initialized for topics: {topics}")
        print(f"Group: {self.group_id}, auto_offset_reset: {self.auto_offset_reset}")
    
    def start_generating(self, events_per_second: float = 10):
        """Start background thread to generate events"""
        if self.running:
            return
        
        self.running = True
        self.generator_thread = threading.Thread(
            target=self._generate_events,
            args=(events_per_second,),
            daemon=True
        )
        self.generator_thread.start()
        print(f"Event generation started at {events_per_second} events/sec")
    
    def _generate_events(self, events_per_second: float):
        """Background thread that generates events"""
        generator = RestaurantEventGenerator()
        
        while self.running:
            try:
                # Generate a table session
                session = generator.generate_table_session()
                events = generator.introduce_issues(session["events"])
                
                # Add events to queue
                for event in events:
                    # Create a mock Kafka message
                    message = MockKafkaMessage(
                        topic=self.topics[0],
                        partition=0,
                        offset=int(time.time() * 1000),
                        key=event.get('table_id', '').encode('utf-8'),
                        value=json.dumps(event).encode('utf-8'),
                        timestamp=int(datetime.fromisoformat(
                            event['timestamp'].replace('Z', '+00:00')
                        ).timestamp() * 1000)
                    )
                    
                    try:
                        self.queue.put(message, timeout=1)
                    except queue.Full:
                        print("Warning: Queue full, dropping events")
                
                # Rate limiting
                sleep_time = len(events) / events_per_second
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error generating events: {e}")
                time.sleep(1)
    
    def poll(self, timeout_ms: int = 1000, max_records: int = 500) -> Dict:
        """
        Poll for new messages (mimics kafka-python interface)
        Returns dict of {TopicPartition: [messages]}
        """
        messages = []
        timeout_sec = timeout_ms / 1000.0
        start_time = time.time()
        
        while len(messages) < max_records:
            remaining_time = timeout_sec - (time.time() - start_time)
            if remaining_time <= 0:
                break
            
            try:
                message = self.queue.get(timeout=min(remaining_time, 0.1))
                messages.append(message)
            except queue.Empty:
                break
        
        if messages:
            # Return in kafka-python format
            topic_partition = MockTopicPartition(self.topics[0], 0)
            return {topic_partition: messages}
        return {}
    
    def close(self):
        """Stop the consumer"""
        self.running = False
        if self.generator_thread:
            self.generator_thread.join(timeout=2)
        print("MockKafkaConsumer closed")


class MockKafkaMessage:
    """Mock Kafka message object"""
    
    def __init__(self, topic, partition, offset, key, value, timestamp):
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.key = key
        self.value = value
        self.timestamp = timestamp
    
    def __repr__(self):
        return (f"MockKafkaMessage(topic={self.topic}, partition={self.partition}, "
                f"offset={self.offset}, timestamp={self.timestamp})")


class MockTopicPartition:
    """Mock TopicPartition object"""
    
    def __init__(self, topic, partition):
        self.topic = topic
        self.partition = partition
    
    def __hash__(self):
        return hash((self.topic, self.partition))
    
    def __eq__(self, other):
        return self.topic == other.topic and self.partition == other.partition
    
    def __repr__(self):
        return f"MockTopicPartition(topic={self.topic}, partition={self.partition})"


class FileBasedEventStream:
    """
    Alternative: Read events from a JSONL file
    Useful for replaying the same dataset
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_handle = None
        self.line_number = 0
    
    def __enter__(self):
        self.file_handle = open(self.filepath, 'r')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_handle:
            self.file_handle.close()
    
    def read_batch(self, batch_size: int = 100) -> List[Dict]:
        """Read a batch of events from the file"""
        if not self.file_handle:
            raise ValueError("Stream not opened. Use 'with' statement.")
        
        batch = []
        for _ in range(batch_size):
            line = self.file_handle.readline()
            if not line:
                break  # End of file
            
            try:
                event = json.loads(line.strip())
                batch.append(event)
                self.line_number += 1
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON at line {self.line_number}: {e}")
        
        return batch
    
    def read_all(self) -> List[Dict]:
        """Read all events from the file"""
        if not self.file_handle:
            raise ValueError("Stream not opened. Use 'with' statement.")
        
        events = []
        for line in self.file_handle:
            try:
                event = json.loads(line.strip())
                events.append(event)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON: {e}")
        
        return events


# Example usage
if __name__ == "__main__":
    print("Mock Restaurant Event Stream Demo\n")
    
    # Option 1: Queue-based stream (like Kafka)
    print("=== Queue-based Stream (MockKafkaConsumer) ===")
    consumer = MockKafkaConsumer(['restaurant-events'], group_id='test-consumer')
    consumer.start_generating(events_per_second=5)
    
    print("Consuming 20 events...\n")
    consumed = 0
    
    try:
        while consumed < 20:
            messages_dict = consumer.poll(timeout_ms=2000, max_records=10)
            
            for topic_partition, messages in messages_dict.items():
                for message in messages:
                    event = json.loads(message.value.decode('utf-8'))
                    restaurant = event.get('restaurant_name', 'N/A')
                    table = event.get('table_id', 'N/A')
                    print(f"{consumed + 1}. {event['event_type']:20} | "
                          f"{event['timestamp']} | "
                          f"{restaurant} | Table: {table}")
                    consumed += 1
    
    finally:
        consumer.close()
    
    print("\n=== File-based Stream ===")
    print("First generate sample data:")
    print("  poetry run python event_generator.py batch")
    print("\nThen read from file:")
    print("  with FileBasedEventStream('sample_events.jsonl') as stream:")
    print("      events = stream.read_batch(100)")
