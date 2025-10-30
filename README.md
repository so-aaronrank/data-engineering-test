## Overview
Build a real-time analytics system that processes restaurant operations events and powers a live dashboard showing key metrics.

**Time Allocation: 60 minutes**
- Setup & Understanding: 5-10 minutes
- Schema Design: 15-20 minutes
- Implementation: 25-30 minutes
- Query & Discussion: 10-15 minutes

## Business Context
You're building analytics infrastructure for a restaurant chain. The operations team needs a real-time dashboard showing:
- Revenue in the last 5 minutes by restaurant location
- Order flow metrics (table seated → order placed → order completed → payment)
- Popular menu items in real-time
- Average wait times and table turnover

Events arrive from a mock stream with possible duplicates and out-of-order delivery.

## Your Task

### Phase 1: Schema Design (15-20 min)
Design ClickHouse table(s) to store restaurant events with consideration for:
- Appropriate table engine 
- Partitioning and ordering keys
- Handling duplicates
- Query performance for time-based aggregations
- Data retention policies

### Phase 2: Consumer Implementation (25-30 min)
Write a Python consumer that:
- Reads events from the batch file (`sample_events.jsonl`)
- Transforms/validates data as needed
- Inserts data into ClickHouse efficiently
- Handles errors gracefully

### Phase 3: Query Development (10-15 min)
Create SQL queries to support the dashboard:

1. **Revenue in last 5 minutes by restaurant location**
   - Output: restaurant_name, total revenue, order count
   - Performance target: < 100ms

2. **Order flow funnel metrics**
   - Show conversion: table_seated → order_placed → order_completed → payment
   - For the last hour, by restaurant
   - Include conversion rates between stages

3. **Top 10 popular menu items**
   - Last 30 minutes, real-time
   - Output: item_name, category, quantity ordered, times ordered


## Data Schema

### Event Types

#### table_seated
```json
{
  "event_id": "uuid",
  "event_type": "table_seated",
  "timestamp": "2025-10-29T18:23:45.123Z",
  "restaurant_id": "rest_001",
  "restaurant_name": "Downtown Location",
  "table_id": "table_12",
  "party_size": 4,
  "server_id": "server_456"
}
```

#### order_placed
```json
{
  "event_id": "uuid",
  "event_type": "order_placed",
  "timestamp": "2025-10-29T18:30:15.456Z",
  "restaurant_id": "rest_001",
  "restaurant_name": "Downtown Location",
  "table_id": "table_12",
  "server_id": "server_456",
  "order_id": "order_789",
  "items": [
    {
      "item_id": "item_101",
      "item_name": "Margherita Pizza",
      "category": "Pizza",
      "price": 18.99,
      "quantity": 2
    },
    {
      "item_id": "item_205",
      "item_name": "Caesar Salad",
      "category": "Salad",
      "price": 12.99,
      "quantity": 1
    }
  ],
  "subtotal": 50.97
}
```

#### order_completed
```json
{
  "event_id": "uuid",
  "event_type": "order_completed",
  "timestamp": "2025-10-29T18:55:30.789Z",
  "restaurant_id": "rest_001",
  "restaurant_name": "Downtown Location",
  "table_id": "table_12",
  "order_id": "order_789",
  "kitchen_time_minutes": 22
}
```

#### payment
```json
{
  "event_id": "uuid",
  "event_type": "payment",
  "timestamp": "2025-10-29T19:05:45.123Z",
  "restaurant_id": "rest_001",
  "restaurant_name": "Downtown Location",
  "table_id": "table_12",
  "order_id": "order_789",
  "subtotal": 50.97,
  "tax": 4.58,
  "tip": 10.00,
  "total_amount": 65.55,
  "payment_method": "credit_card"
}
```

## Evaluation Criteria

We're looking for:
- **Schema design thinking**: Appropriate table engines, keys, and partitioning
- **Real-world considerations**: Deduplication, late data, performance
- **Code quality**: Clean, readable Python with error handling
- **Communication**: Explaining trade-offs and design decisions
- **ClickHouse knowledge**: Understanding of specific features and best practices

## Tips
- You can use LLMs and documentation freely
- Ask clarifying questions about requirements
- Think out loud - we want to understand your reasoning
- It's okay if you don't finish everything - focus on quality over quantity
- Consider operational concerns (monitoring, errors, backpressure)

## Questions to Consider
- How will you handle duplicate events?
- What happens if events arrive out of order?
- How will you partition data for optimal query performance?
- What indexes/projections might help?
- How would this scale to 10x the volume?
- How would you handle orders with multiple items?
- How would you calculate wait times between events?