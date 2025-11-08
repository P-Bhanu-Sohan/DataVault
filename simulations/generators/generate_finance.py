import json
import random
from datetime import datetime, timedelta

def generate_finance_data(num_records):
    data = []
    transaction_types = ["Credit", "Debit"]
    merchant_categories = ["Groceries", "Restaurants", "Gas", "Shopping", "Utilities"]
    account_holder_names = [
        {"first_name": "Alice", "last_name": "Smith"},
        {"first_name": "Bob", "last_name": "Johnson"},
        {"first_name": "Charlie", "last_name": "Brown"},
        {"first_name": "Diana", "last_name": "Prince"},
        {"first_name": "Eve", "last_name": "Adams"},
        {"first_name": "Frank", "last_name": "White"},
        {"first_name": "Grace", "last_name": "Black"},
        {"first_name": "Heidi", "last_name": "Green"},
        {"first_name": "Ivan", "last_name": "Blue"},
        {"first_name": "Judy", "last_name": "Red"}
    ]
    for i in range(num_records):
        transaction_time = datetime(2025, 1, 1) + timedelta(seconds=random.randint(0, 31536000))
        chosen_name = random.choice(account_holder_names)
        record = {
            "account_hash": str(20000 + i),
            "first_name": chosen_name["first_name"],
            "last_name": chosen_name["last_name"],
            "transaction_type": random.choice(transaction_types),
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "merchant_category": random.choice(merchant_categories),
            "transaction_time": transaction_time.isoformat() + "Z"
        }
        data.append(record)
    return data

with open('/Users/kishorepingali/Desktop/DataVault/simulations/datasets/finance.json', 'w') as f:
    json.dump(generate_finance_data(500), f, indent=4)
