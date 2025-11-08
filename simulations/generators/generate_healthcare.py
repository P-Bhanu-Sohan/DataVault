import json
import random
from datetime import datetime, timedelta

def generate_healthcare_data(num_records):
    data = []
    diagnoses = ["Type 2 Diabetes", "Hypertension", "Asthma", "Migraine", "Depression"]
    treatments = ["Medication A", "Medication B", "Physical Therapy", "Counseling", "Dietary Changes"]
    patient_names = [
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
        visit_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))
        chosen_name = random.choice(patient_names)
        record = {
            "patient_id": str(10000 + i),
            "first_name": chosen_name["first_name"],
            "last_name": chosen_name["last_name"],
            "age": random.randint(18, 80),
            "diagnosis": random.choice(diagnoses),
            "treatment_plan": random.choice(treatments),
            "visit_date": visit_date.strftime("%Y-%m-%d")
        }
        data.append(record)
    return data

with open('/Users/kishorepingali/Desktop/DataVault/simulations/datasets/healthcare.json', 'w') as f:
    json.dump(generate_healthcare_data(500), f, indent=4)
