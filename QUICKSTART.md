# Quick Start Guide

Welcome! This guide will help you get started with the interview exercise.

## Setup (5 minutes)

### 1. Install Dependencies

Choose either Poetry or pip:

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Start ClickHouse
```bash
# Using Docker (recommended)
docker-compose up -d

# Verify it's running
docker ps | grep clickhouse

# Test connection
docker exec -it interview-clickhouse clickhouse-client --query "SELECT 1"
```

**Alternative:** If you don't have Docker, you can install ClickHouse locally:
- Mac: `brew install clickhouse`
- Linux: Follow instructions at https://clickhouse.com/docs/en/install

### 3. Generate Sample Data
```bash
# Generate a batch of sample events to work with
poetry run python event_generator.py batch
# Or: python event_generator.py batch

# This creates sample_events.jsonl with ~500 events
```

## Understanding the Data

### View Sample Events
```bash
# Look at a few sample events
head -n 5 sample_events.jsonl | jq '.'

# Or without jq
head -n 5 sample_events.jsonl
```

## Your Tasks

### 1. Design ClickHouse Schema (15-20 min)
Create a SQL file with your schema design. Consider:
- What table engine should you use? (Hint: look at MergeTree family)
- How will you handle duplicate events?
- What should your ORDER BY and PARTITION BY be?
- How will you store nested data (order_placed has an items array)?
- What data types are appropriate for each field?
- How will your schema support the required queries (see section 3)?

### 2. Implement Consumer (25-30 min)
Implement `consumer.py` to process the events. Your consumer should:
- Read events from the batch file (`sample_events.jsonl`)
- Validate and transform data
- Insert into ClickHouse in batches
- Handle errors gracefully

### 3. Write Queries (10-15 min)
Create SQL queries to support the dashboard:

**Query 1: Revenue in Last 5 Minutes by Restaurant**
- Output: restaurant_name, total revenue, order count
- Should use payment events
- Performance target: < 100ms

**Query 2: Order Flow Funnel Metrics**
- Show conversion: table_seated → order_placed → order_completed → payment
- For the last hour, by restaurant
- Output: restaurant_name, counts for each stage, conversion rates

**Query 3: Top 10 Popular Menu Items**
- Last 30 minutes, real-time
- Output: item_name, category, quantity ordered, times ordered
- Consider: how will you handle the nested items array from order_placed events?

## Testing Your Solution

### Create Tables
```bash
# Connect to ClickHouse
docker exec -it interview-clickhouse clickhouse-client

# Run your CREATE TABLE statements
-- paste your SQL here
```

### Run Your Consumer
```bash
# Using Poetry
poetry run python consumer.py

# Or directly with python
python consumer.py
```

### Query the Data
```bash
# In another terminal
docker exec -it interview-clickhouse clickhouse-client

# First, verify your data loaded correctly
SELECT event_type, count() FROM your_table GROUP BY event_type;

# Then test your dashboard queries
# Write queries to support the requirements in section 3 above
```

## Tips

✅ **DO:**
- Use LLMs and documentation freely
- Ask clarifying questions
- Think out loud - explain your reasoning
- Consider what would happen in production
- Start simple, then add complexity

❌ **DON'T:**
- Worry about finishing everything perfectly
- Get stuck on one part - move on and come back
- Forget to test your code
- Optimize prematurely

## Helpful Resources

### ClickHouse Documentation
- Table engines: https://clickhouse.com/docs/en/engines/table-engines
- Data types: https://clickhouse.com/docs/en/sql-reference/data-types
- Functions: https://clickhouse.com/docs/en/sql-reference/functions

### Python Libraries
- `clickhouse-connect` docs: https://clickhouse.com/docs/en/integrations/python

### Reading the Event File
```python
import json

# Simple approach - read the entire file
with open('sample_events.jsonl', 'r') as f:
    for line in f:
        event = json.loads(line)
        # process event

# Or use the FileBasedEventStream helper
from mock_event_stream import FileBasedEventStream

with FileBasedEventStream('sample_events.jsonl') as stream:
    events = stream.read_batch(100)  # Read 100 events at a time
    for event in events:
        # process event
```

## Troubleshooting

### ClickHouse won't start
```bash
# Check logs
docker logs interview-clickhouse

# Restart
docker-compose down && docker-compose up -d
```

### Can't connect to ClickHouse
```bash
# Check if it's running
docker ps | grep clickhouse

# Try connecting with explicit port (using 9001 due to Zscaler on 9000)
clickhouse-client --host localhost --port 9001
```

### Need more test data?
```bash
# Generate a larger batch
python event_generator.py batch

# Or generate with more tables
# Edit event_generator.py line 318 to change num_tables parameter
```

## Questions?

Don't hesitate to ask your interviewer for:
- Clarification on requirements
- Help with setup issues
- Guidance if you're stuck

**Remember:** We want to see your thought process and how you approach problems, not just whether you finish everything!

Good luck! 🚀
