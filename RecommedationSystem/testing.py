from pymongo import MongoClient
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from random import randint, choice

# MongoDB connection setup
def connect_to_mongodb():
    # Replace with your MongoDB URI and database details
    client = MongoClient("mongodb://localhost:27017/")
    db = client['ecommerce_db']  # Replace with your database name
    return db

# Function to extract data from MongoDB and create a transaction DataFrame
def extract_data_from_mongodb():
    db = connect_to_mongodb()
    
    # Example: Extracting user interactions (replace with your actual collection)
    user_data = db['user_interactions'].find()  # Replace with your collection
    
    # Convert MongoDB data to a DataFrame for easier manipulation
    df = pd.DataFrame(list(user_data))
    
    # Create a transaction matrix where rows represent users and columns represent products
    # Each entry in the matrix will be 1 if the user has interacted with the product, else 0
    transaction_data = pd.pivot_table(df, index='user_id', columns='product_id', values='rating', aggfunc='count', fill_value=0)
    
    return transaction_data

# Function to generate recommendations using the Apriori algorithm
def extract_and_recommend_from_mongodb(user_data):
    # Extract data from MongoDB
    transaction_data = extract_data_from_mongodb()
    
    # Apply the Apriori algorithm to find frequent itemsets (with min_support of 0.4)
    frequent_itemsets = apriori(transaction_data, min_support=0.4, use_colnames=True)
    
    # Generate association rules from the frequent itemsets
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    
    # Find the user's interactions (e.g., products they've interacted with)
    user_id = user_data['user_id']
    user_interactions = transaction_data.loc[user_id]
    
    # Filter out products the user has already interacted with
    interacted_products = user_interactions[user_interactions > 0].index.tolist()
    
    # Find association rules where the antecedent is in the user's interactions
    recommended_products = set()
    for _, rule in rules.iterrows():
        # If the user has interacted with the antecedents of the rule, recommend the consequents
        if any(item in interacted_products for item in rule['antecedents']):
            recommended_products.update(rule['consequents'])
    
    # Remove products the user has already interacted with from the recommendations
    recommended_products -= set(interacted_products)
    
    # Return top N recommendations (e.g., top 5)
    return list(recommended_products)[:5]

# Example usage
user_data = {'user_id': 1}  # Example user ID
recommended_products = extract_and_recommend_from_mongodb(user_data)

print("Recommended Products:", recommended_products)
