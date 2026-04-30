from app.db import database
from app.models.subscription import Plan
from peewee import MySQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def update_prices():
    # Manual init for script
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    name = os.getenv("DB_NAME", "lms")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    
    db = MySQLDatabase(name, user=user, password=password, host=host, port=port)
    database.initialize(db)
    
    prices = {
        "Starter": 0,
        "Medium": 10,
        "Enterprise": 20
    }
    
    with database.connection_context():
        for name, price in prices.items():
            plan = Plan.get_or_none(Plan.name == name)
            if plan:
                plan.price = price
                plan.save()
                print(f"Updated {name} to {price}")
            else:
                print(f"Plan {name} not found")

if __name__ == "__main__":
    update_prices()
