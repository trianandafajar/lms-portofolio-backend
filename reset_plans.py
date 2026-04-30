from app.db import database
from app.models.subscription import Plan
from peewee import MySQLDatabase
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

def reset_plans():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    name = os.getenv("DB_NAME", "lms")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    
    db = MySQLDatabase(name, user=user, password=password, host=host, port=port)
    database.initialize(db)
    
    plans_data = [
        # Monthly Plans
        {
            "id": 1,
            "name": "Starter Monthly",
            "stripe_price_id": "free_monthly",
            "description": "Perfect for individual educators getting started.",
            "price": Decimal("0.00"),
        },
        {
            "id": 2,
            "name": "Medium Monthly",
            "stripe_price_id": "price_medium_monthly",
            "description": "For growing teams and institutions.",
            "price": Decimal("10.00"),
        },
        {
            "id": 3,
            "name": "Enterprise Monthly",
            "stripe_price_id": "price_enterprise_monthly",
            "description": "Unlimited power for large organizations.",
            "price": Decimal("20.00"),
        },
        # Yearly Plans (10% discount: Price * 12 * 0.9)
        {
            "id": 4,
            "name": "Starter Yearly",
            "stripe_price_id": "free_yearly",
            "description": "Perfect for individual educators getting started.",
            "price": Decimal("0.00"),
        },
        {
            "id": 5,
            "name": "Medium Yearly",
            "stripe_price_id": "price_medium_yearly",
            "description": "For growing teams and institutions.",
            "price": Decimal("108.00"), # 10 * 12 * 0.9
        },
        {
            "id": 6,
            "name": "Enterprise Yearly",
            "stripe_price_id": "price_enterprise_yearly",
            "description": "Unlimited power for large organizations.",
            "price": Decimal("216.00"), # 20 * 12 * 0.9
        },
    ]
    
    with database.connection_context():
        # Clear all plans
        print("Cleaning up old plans...")
        Plan.delete().execute()
        
        # Insert new plans with specific IDs
        for p in plans_data:
            Plan.create(**p)
            print(f"Created {p['name']} with ID {p['id']} and price {p['price']}")

if __name__ == "__main__":
    reset_plans()
