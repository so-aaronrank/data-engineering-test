"""
Event Generator for Restaurant Analytics Pipeline
Simulates a stream of restaurant operations events with realistic patterns
"""

import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from faker import Faker

fake = Faker()


class RestaurantEventGenerator:
    """Generates realistic restaurant events with table service flow"""
    
    RESTAURANTS = [
        ("rest_001", "Downtown Location"),
        ("rest_002", "Westside Location"),
        ("rest_003", "Eastside Location"),
        ("rest_004", "Uptown Location"),
        ("rest_005", "Suburban Location"),
    ]
    
    MENU_ITEMS = {
        "Pizza": [
            ("Margherita Pizza", 18.99),
            ("Pepperoni Pizza", 20.99),
            ("Quattro Formaggi", 22.99),
            ("BBQ Chicken Pizza", 21.99),
            ("Veggie Supreme Pizza", 19.99),
        ],
        "Pasta": [
            ("Spaghetti Carbonara", 16.99),
            ("Fettuccine Alfredo", 17.99),
            ("Penne Arrabbiata", 15.99),
            ("Lasagna Bolognese", 19.99),
            ("Seafood Linguine", 24.99),
        ],
        "Salad": [
            ("Caesar Salad", 12.99),
            ("Greek Salad", 13.99),
            ("House Garden Salad", 10.99),
            ("Caprese Salad", 14.99),
        ],
        "Appetizer": [
            ("Garlic Bread", 7.99),
            ("Bruschetta", 9.99),
            ("Mozzarella Sticks", 10.99),
            ("Calamari", 13.99),
            ("Wings", 12.99),
        ],
        "Entree": [
            ("Grilled Salmon", 26.99),
            ("Ribeye Steak", 34.99),
            ("Chicken Parmesan", 21.99),
            ("Lamb Chops", 32.99),
            ("Eggplant Parmigiana", 18.99),
        ],
        "Dessert": [
            ("Tiramisu", 8.99),
            ("Chocolate Lava Cake", 9.99),
            ("Cheesecake", 8.99),
            ("Gelato", 6.99),
        ],
        "Beverage": [
            ("Soft Drink", 3.99),
            ("Iced Tea", 3.99),
            ("Sparkling Water", 4.99),
            ("Fresh Juice", 5.99),
            ("Coffee", 3.99),
        ],
    }
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            Faker.seed(seed)
    
    def generate_item_id(self, category: str, item_name: str) -> str:
        """Generate consistent menu item IDs"""
        # Simple hash-based ID for consistency
        return f"item_{hash(category + item_name) % 100000:05d}"
    
    def generate_table_session(self) -> Dict:
        """Generate a table session with restaurant service flow"""
        # Select restaurant
        restaurant_id, restaurant_name = random.choice(self.RESTAURANTS)
        
        # Generate identifiers
        table_id = f"table_{random.randint(1, 30):02d}"
        server_id = f"server_{random.randint(100, 999)}"
        order_id = f"order_{fake.uuid4()[:8]}"
        party_size = random.choices([2, 3, 4, 5, 6], weights=[35, 25, 25, 10, 5])[0]
        
        base_timestamp = datetime.now()
        events = []
        
        # Event 1: table_seated
        seated_timestamp = base_timestamp
        events.append({
            "event_id": str(uuid.uuid4()),
            "event_type": "table_seated",
            "timestamp": seated_timestamp.isoformat(),
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant_name,
            "table_id": table_id,
            "party_size": party_size,
            "server_id": server_id,
        })
        
        # Event 2: order_placed (5-15 minutes after seating)
        # 90% of tables place an order
        if random.random() < 0.9:
            order_timestamp = seated_timestamp + timedelta(minutes=random.randint(5, 15))
            
            # Build order with 2-6 items
            num_items = random.randint(2, 6)
            order_items = []
            subtotal = 0
            
            for _ in range(num_items):
                category = random.choice(list(self.MENU_ITEMS.keys()))
                item_name, price = random.choice(self.MENU_ITEMS[category])
                item_id = self.generate_item_id(category, item_name)
                quantity = random.choices([1, 2], weights=[85, 15])[0]
                
                order_items.append({
                    "item_id": item_id,
                    "item_name": item_name,
                    "category": category,
                    "price": price,
                    "quantity": quantity,
                })
                subtotal += price * quantity
            
            subtotal = round(subtotal, 2)
            
            events.append({
                "event_id": str(uuid.uuid4()),
                "event_type": "order_placed",
                "timestamp": order_timestamp.isoformat(),
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "table_id": table_id,
                "server_id": server_id,
                "order_id": order_id,
                "items": order_items,
                "subtotal": subtotal,
            })
            
            # Event 3: order_completed (15-35 minutes after order placed)
            kitchen_time_minutes = random.randint(15, 35)
            completed_timestamp = order_timestamp + timedelta(minutes=kitchen_time_minutes)
            
            events.append({
                "event_id": str(uuid.uuid4()),
                "event_type": "order_completed",
                "timestamp": completed_timestamp.isoformat(),
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "table_id": table_id,
                "order_id": order_id,
                "kitchen_time_minutes": kitchen_time_minutes,
            })
            
            # Event 4: payment (10-25 minutes after order completed)
            # 95% of orders result in payment
            if random.random() < 0.95:
                payment_timestamp = completed_timestamp + timedelta(minutes=random.randint(10, 25))
                
                tax = round(subtotal * 0.09, 2)  # 9% tax
                tip = round(subtotal * random.choice([0.15, 0.18, 0.20, 0.22, 0.25]), 2)
                total_amount = round(subtotal + tax + tip, 2)
                payment_method = random.choices(
                    ["credit_card", "debit_card", "cash", "mobile_payment"],
                    weights=[50, 25, 15, 10]
                )[0]
                
                events.append({
                    "event_id": str(uuid.uuid4()),
                    "event_type": "payment",
                    "timestamp": payment_timestamp.isoformat(),
                    "restaurant_id": restaurant_id,
                    "restaurant_name": restaurant_name,
                    "table_id": table_id,
                    "order_id": order_id,
                    "subtotal": subtotal,
                    "tax": tax,
                    "tip": tip,
                    "total_amount": total_amount,
                    "payment_method": payment_method,
                })
        
        return {"table_id": table_id, "events": events}
    
    def introduce_issues(self, events: List[Dict]) -> List[Dict]:
        """
        Introduce real-world issues:
        - Duplicates (5% chance)
        - Out-of-order delivery (10% chance of timestamp shuffle)
        - Late arrivals (3% chance of significant delay)
        """
        modified_events = []
        
        for event in events:
            # Add original event
            modified_events.append(event.copy())
            
            # 5% chance of duplicate
            if random.random() < 0.05:
                duplicate = event.copy()
                duplicate["event_id"] = event["event_id"]  # Same ID for deduplication testing
                modified_events.append(duplicate)
            
            # 3% chance of late arrival (same event, much later timestamp)
            if random.random() < 0.03:
                late_event = event.copy()
                # Event will be delivered now, but timestamp is from the past
                modified_events.append(late_event)
        
        # 10% chance to shuffle a portion (simulate out-of-order)
        if random.random() < 0.1 and len(modified_events) > 2:
            # Shuffle a random subset
            start_idx = random.randint(0, len(modified_events) - 2)
            end_idx = min(start_idx + random.randint(2, 5), len(modified_events))
            subset = modified_events[start_idx:end_idx]
            random.shuffle(subset)
            modified_events[start_idx:end_idx] = subset
        
        return modified_events


def generate_continuous_stream(events_per_second: float = 10, duration_seconds: int = 300):
    """
    Generate continuous stream of restaurant events
    
    Args:
        events_per_second: Target rate of events
        duration_seconds: How long to run (None = infinite)
    """
    generator = RestaurantEventGenerator()
    
    print(f"Starting restaurant event generation at {events_per_second} events/second")
    print("Events will be written to stdout (one JSON per line)")
    print("Pipe this to a file or Kafka producer as needed\n")
    
    start_time = time.time()
    event_count = 0
    
    try:
        while True:
            if duration_seconds and (time.time() - start_time) > duration_seconds:
                break
            
            # Generate a table session
            session = generator.generate_table_session()
            events = generator.introduce_issues(session["events"])
            
            # Output events
            for event in events:
                print(json.dumps(event))
                event_count += 1
            
            # Rate limiting
            sleep_time = len(events) / events_per_second
            time.sleep(sleep_time)
            
            # Progress indicator (to stderr so it doesn't interfere with JSON output)
            if event_count % 100 == 0:
                elapsed = time.time() - start_time
                rate = event_count / elapsed if elapsed > 0 else 0
                print(f"[Progress: {event_count} events, {rate:.1f} events/sec]", 
                      file=__import__('sys').stderr)
    
    except KeyboardInterrupt:
        print(f"\n[Stopped. Generated {event_count} events]", 
              file=__import__('sys').stderr)


def generate_sample_batch(num_tables: int = 100, output_file: str = "sample_events.jsonl"):
    """Generate a batch of sample events for testing"""
    generator = RestaurantEventGenerator(seed=42)  # Fixed seed for reproducibility
    
    all_events = []
    
    for _ in range(num_tables):
        session = generator.generate_table_session()
        events = generator.introduce_issues(session["events"])
        all_events.extend(events)
    
    with open(output_file, 'w') as f:
        for event in all_events:
            f.write(json.dumps(event) + '\n')
    
    print(f"Generated {len(all_events)} events from {num_tables} table sessions")
    print(f"Saved to {output_file}")
    
    # Print some statistics
    event_types = {}
    for event in all_events:
        event_type = event["event_type"]
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("\nEvent type distribution:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        # Generate batch file for testing
        generate_sample_batch(num_tables=100)
    else:
        # Generate continuous stream
        generate_continuous_stream(events_per_second=10, duration_seconds=None)
