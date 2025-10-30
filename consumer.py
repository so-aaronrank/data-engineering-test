"""
Restaurant Event Consumer

Your task: Build a consumer that processes restaurant events and loads them into ClickHouse.

Requirements:
- Read events from sample_events.jsonl
- Validate events (required fields, reasonable values)
- Transform as needed for your schema design
- Batch insert into ClickHouse efficiently
- Handle errors appropriately
- Track and report basic metrics

Event types:
- table_seated: Customer sits down
- order_placed: Order taken (contains nested items array)
- order_completed: Kitchen finishes
- payment: Customer pays

Considerations:
- ~5% of events are duplicates (same event_id)
- Events may be out of order
- Some events may have malformed data

ClickHouse connection example:
    import clickhouse_connect
    
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='default',
        password=''
    )
    
    # Insert example
    client.insert('table_name', data, column_names=['col1', 'col2', ...])

Hint: Check consumer_example.py if you get stuck, but try your own approach first!
"""

import json
import clickhouse_connect


# Your implementation here


if __name__ == "__main__":
    # Your entry point here
    pass

