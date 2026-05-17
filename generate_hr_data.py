import pandas as pd
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_INITIAL_EMPLOYEES = 100
DAYS_TO_SIMULATE = 365
START_DATE = datetime(2025, 1, 1)

DEPARTMENTS = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
ROLES = ['Analyst', 'Engineer', 'Manager', 'Director']

os.makedirs('data/raw_json', exist_ok=True)
os.makedirs('data/seed', exist_ok=True)


def generate_initial_employees():
    employees = []
    for _ in range(NUM_INITIAL_EMPLOYEES):
        emp = {
            'emp_id': fake.unique.random_number(digits=5),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'department': random.choice(DEPARTMENTS),
            'role': random.choice(ROLES),
            'salary': random.randint(50000, 150000),
            'hire_date': fake.date_between(start_date='-3y', end_date=START_DATE).strftime('%Y-%m-%d'),
            'status': 'Active'
        }
        employees.append(emp)
    
    df = pd.DataFrame(employees)
    df.to_csv('data/seed/initial_employees.csv', index=False)
    print("✅ Created initial_employees.csv")
    return employees


def generate_daily_events(active_employees, current_date):
    events = []
    
  
    for emp in active_employees[:]: # Iterate over a copy
        if random.random() < 0.005: # 0.5% chance of quitting on any given day
            events.append({
                'event_id': fake.uuid4(),
                'timestamp': current_date.isoformat(),
                'emp_id': emp['emp_id'],
                'event_type': 'TERMINATION'
            })
            active_employees.remove(emp)

    for emp in active_employees:
        if random.random() < 0.01: # 1% chance
            new_salary = emp['salary'] + random.randint(5000, 15000)
            events.append({
                'event_id': fake.uuid4(),
                'timestamp': current_date.isoformat(),
                'emp_id': emp['emp_id'],
                'event_type': 'PROMOTION',
                'new_salary': new_salary,
                'new_role': random.choice(ROLES) # Simplify role change
            })
            emp['salary'] = new_salary

    for emp in active_employees:
        if random.random() < 0.008: # 0.8% chance
            new_dept = random.choice([d for d in DEPARTMENTS if d != emp['department']])
            events.append({
                'event_id': fake.uuid4(),
                'timestamp': current_date.isoformat(),
                'emp_id': emp['emp_id'],
                'event_type': 'DEPARTMENT_TRANSFER',
                'new_department': new_dept
            })
            emp['department'] = new_dept

    
    if random.random() < 0.2: 
        new_emp = {
            'emp_id': fake.unique.random_number(digits=5),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'department': random.choice(DEPARTMENTS),
            'role': random.choice(ROLES),
            'salary': random.randint(50000, 150000),
            'hire_date': current_date.strftime('%Y-%m-%d'),
            'status': 'Active'
        }
        active_employees.append(new_emp)
        events.append({
            'event_id': fake.uuid4(),
            'timestamp': current_date.isoformat(),
            'emp_id': new_emp['emp_id'],
            'event_type': 'HIRE',
            'details': new_emp
        })

    return events

# --- Main Execution ---
print("Starting Data Generation...")
current_workforce = generate_initial_employees()

for i in range(DAYS_TO_SIMULATE):
    sim_date = START_DATE + timedelta(days=i)
    daily_payload = generate_daily_events(current_workforce, sim_date)
    
    if daily_payload:
        filename = f"data/raw_json/hr_events_{sim_date.strftime('%Y-%m-%d')}.json"
        with open(filename, 'w') as f:
            json.dump(daily_payload, f, indent=4)
        print(f"📄 Generated {len(daily_payload)} events for {sim_date.strftime('%Y-%m-%d')}")

print("🎉 Data generation complete! Check the 'data' folder.")