# Senior Data Engineer Interview: Real-Time Restaurant Analytics

## Overview

Design and implement a real-time analytics system that processes restaurant operations events and powers a live dashboard. This is a collaborative exercise—think of it as pair programming. Feel free to ask questions, discuss trade-offs, and use any resources (documentation, LLMs, etc.).

**Duration: 60 minutes**

| Phase | Time | Focus |
|-------|------|-------|
| Architecture & Database Selection | 15-20 min | System design, justify technology choices |
| Schema Design & Implementation | 20-25 min | Data modeling, DDL, ingestion code |
| Queries & Discussion | 15-20 min | Analytics queries, optimization, trade-offs |

---

## Business Context

You're building analytics infrastructure for a large restaurant chain. The operations team needs a real-time dashboard showing:

- **Revenue metrics**: Live revenue by location, payment trends
- **Order flow**: Table seated → order placed → order completed → payment
- **Popular items**: Trending menu items in real-time
- **Operational metrics**: Wait times, table turnover, kitchen performance

---

## Technical Constraints

| Constraint | Value |
|------------|-------|
| Locations | 20,000 restaurants |
| Peak load | 100 orders/second (lunch & dinner rushes) |
| Baseline load | 1 order/second (overnight) |
| Event types | 4 (table_seated, order_placed, order_completed, payment) |
| Events per order | ~4 events average |
| Dashboard refresh | Near real-time (< 10 second latency acceptable) |
| Query SLA | P95 < 500ms for dashboard queries |

### Data Quality Realities

Your ingestion pipeline must handle:

- **Duplicates**: ~2% of events are duplicated (same `event_id`)
- **Late arrivals**: Events can arrive up to 5 minutes late
- **Out-of-order**: Events may arrive out of sequence
- **Malformed data**: ~0.1% of events have issues (missing fields, bad types)

---

## Your Task

### Phase 1: Architecture & Database Selection (15-20 min)

Before writing code, discuss and document your architecture:

**1. Database Selection**

Choose a primary datastore and justify your choice. Consider:
- Write patterns (high-volume event ingestion)
- Read patterns (time-based aggregations, real-time dashboards)
- Scaling model (how does it handle 20K locations?)
- Operational complexity (your team has 3 data engineers)
- Cost model

Some options to consider (not exhaustive):
- PostgreSQL / TimescaleDB
- ClickHouse
- Apache Druid
- Cassandra / ScyllaDB
- DynamoDB + something else
- BigQuery / Snowflake / Redshift
- Kafka + ksqlDB
- Or a combination

**2. Ingestion Architecture**

How do events flow from restaurants to your database?
- Direct writes vs. message queue?
- Batching strategy?
- How do you handle backpressure at peak load?

**3. High-Level Data Model**

- Single table vs. multiple tables?
- How do you handle the nested `items` array in orders?
- Normalized vs. denormalized?

---

### Phase 2: Schema Design & Implementation (20-25 min)

**1. Schema Definition**

Write the DDL for your chosen database:
- Table structure(s)
- Partitioning / sharding strategy
- Indexes or other optimizations
- Any materialized views or pre-aggregations

**2. Ingestion Code**

Write a Python script that:
- Reads events (simulating a stream)
- Validates and transforms data as needed
- Handles duplicates and malformed events
- Inserts efficiently (batching, connection management)
- Includes basic error handling and logging


---

### Phase 3: Queries & Discussion (15-20 min)

Write SQL (or equivalent) for these dashboard components:

**Query 1: Live Revenue by Location**
```
Show: location_name, revenue_last_5_min, order_count_last_5_min
Use case: Executive dashboard refreshing every 30 seconds
```

**Query 2: Order Funnel (Last Hour)**
```
Show: location_name, tables_seated, orders_placed, orders_completed, payments
       conversion_rate_seated_to_order, conversion_rate_order_to_payment
Use case: Ops team monitoring flow issues
Challenge: Events are separate—how do you efficiently track the funnel?
```

**Query 3: Trending Menu Items**
```
Show: item_name, category, total_quantity, order_count
Filter: Last 30 minutes, top 10 items
Use case: Kitchen prep and marketing
```

**Bonus Query: Wait Time Analysis** (if time permits)
```
Show: P50, P90, P99 time from table_seated to order_completed
Group by: location, hour_of_day
Use case: Identifying slow locations/times
```

---

## Event Schema Reference

### table_seated
```json
{
  "event_id": "evt_abc123",
  "event_type": "table_seated",
  "timestamp": "2025-01-15T18:23:45.123Z",
  "location_id": "loc_00142",
  "location_name": "Chicago - River North",
  "table_id": "table_12",
  "party_size": 4,
  "server_id": "server_456"
}
```

### order_placed
```json
{
  "event_id": "evt_def456",
  "event_type": "order_placed",
  "timestamp": "2025-01-15T18:30:15.456Z",
  "location_id": "loc_00142",
  "location_name": "Chicago - River North",
  "table_id": "table_12",
  "order_id": "ord_789xyz",
  "server_id": "server_456",
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

### order_completed
```json
{
  "event_id": "evt_ghi789",
  "event_type": "order_completed",
  "timestamp": "2025-01-15T18:55:30.789Z",
  "location_id": "loc_00142",
  "location_name": "Chicago - River North",
  "table_id": "table_12",
  "order_id": "ord_789xyz",
  "kitchen_time_minutes": 22
}
```

### payment
```json
{
  "event_id": "evt_jkl012",
  "event_type": "payment",
  "timestamp": "2025-01-15T19:05:45.123Z",
  "location_id": "loc_00142",
  "location_name": "Chicago - River North",
  "table_id": "table_12",
  "order_id": "ord_789xyz",
  "subtotal": 50.97,
  "tax": 4.58,
  "tip": 10.00,
  "total_amount": 65.55,
  "payment_method": "credit_card"
}
```

---

## Discussion Topics

Throughout the exercise (or at the end), be ready to discuss:

1. **Trade-offs**: What did you optimize for? What did you sacrifice?
2. **Failure modes**: What happens if [database/queue/ingestion] goes down during peak?
3. **Schema evolution**: How would you add a new event type or field?
4. **Scaling**: What changes at 10x load? 100x locations?
5. **Monitoring**: What metrics would you track? What alerts would you set?
6. **Data quality**: How would you detect and handle data quality regressions?
7. **Backfill**: You discover a bug that corrupted 1 week of data. How do you fix it?

---

## Evaluation Criteria

| Area | Weight | What We're Looking For |
|------|--------|------------------------|
| **Architecture Thinking** | 30% | Appropriate technology choices with clear reasoning; understands trade-offs; realistic about operational complexity |
| **Data Modeling** | 25% | Schema supports query patterns efficiently; handles time-series nature; strategy for duplicates and late data |
| **Implementation** | 25% | Clean, readable code; appropriate error handling; performance-conscious (batching, connections) |
| **Query Design** | 15% | Correct results; efficient approach; awareness of optimization techniques |
| **Communication** | 5% | Explains reasoning clearly; asks good questions; acknowledges alternatives |

---

## Tips

- **Ask questions**: Requirements are intentionally somewhat open—clarify what matters
- **Think out loud**: We want to understand your reasoning, not just the end result
- **Use resources**: Documentation, LLMs, Google—whatever you'd use on the job
- **Timebox yourself**: If you're stuck, say so and we'll move on or help
- **Production mindset**: Think about operability, not just correctness
- **It's okay to not finish**: Quality and reasoning matter more than completion

---

## Quick Reference: Capacity Math

Some rough numbers to help with your design:

```
Peak: 100 orders/sec × 4 events/order = 400 events/sec
Daily peak hours: ~6 hours (lunch + dinner)
Daily baseline: ~18 hours at 1 order/sec

Daily events (rough):
  Peak: 400 events/sec × 6 hours × 3600 sec/hour = 8.6M events
  Baseline: 4 events/sec × 18 hours × 3600 sec/hour = 0.26M events
  Total: ~9M events/day

Event size: ~500 bytes average (JSON)
Daily raw data: ~4.5 GB uncompressed

Monthly: ~270M events, ~135 GB uncompressed
Yearly: ~3.2B events, ~1.6 TB uncompressed
```

---

## Getting Started

1. Review the requirements and event schemas
2. Sketch out your architecture
3. Implement schema and ingestion
4. Write queries
5. Discuss trade-offs and alternatives
