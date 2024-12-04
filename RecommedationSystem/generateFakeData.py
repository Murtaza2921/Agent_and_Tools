from pymongo import MongoClient
from faker import Faker
import random

# MongoDB connection setup
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['ecommerce_db']  # Replace with your actual database name
    return db

# Function to generate fake user-product interaction data
def generate_fake_data(num_users=100, num_products=50, num_interactions=500):
    fake = Faker()
    db = connect_to_mongodb()
    
    # Generate fake user data
    users = []
    for user_id in range(1, num_users + 1):
        users.append({
            "user_id": user_id,
            "name": fake.name(),
            "email": fake.email(),
        })
    
    # Insert users into MongoDB (optional)
    db.users.insert_many(users)

    # Generate fake products (in a real case, products would be actual items)
    products = [f'Product_{i}' for i in range(1, num_products + 1)]  # Sample product IDs

    # Generate fake interactions (e.g., user-product ratings)
    interactions = []
    for _ in range(num_interactions):
        user_id = random.randint(1, num_users)  # Random user ID
        product_id = random.choice(products)  # Random product ID
        rating = random.randint(1, 5)  # Random rating (1 to 5)
        interactions.append({
            "user_id": user_id,
            "product_id": product_id,
            "rating": rating
        })

    # Insert interactions into MongoDB (optional)
    db.user_interactions.insert_many(interactions)

# Run the data generation
generate_fake_data()

print("Fake data inserted successfully into MongoDB!")


###pip install faker pymongo
