import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from collections import defaultdict

class PurchaseAnalyzer:
    def __init__(self, csv_file):
        """Initialize the analyzer with the CSV file"""
        self.df = pd.read_csv(csv_file)
        self.process_data()
    
    def process_data(self):
        """Clean and process the raw data"""
        # Convert OrderDate to datetime
        self.df['OrderDate'] = pd.to_datetime(self.df['OrderDate'])
        
        # Extract month and year
        self.df['Month'] = self.df['OrderDate'].dt.month
        self.df['Year'] = self.df['OrderDate'].dt.year
        
        # Clean TotalPrice (seems to have concatenated values)
        self.df['CleanPrice'] = self.df['TotalPrice'].astype(str).str.split('.').str[0]
        self.df['CleanPrice'] = pd.to_numeric(self.df['CleanPrice'].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        
        # Fill NaN values with Base Price
        self.df['CleanPrice'] = self.df['CleanPrice'].fillna(self.df['Base Price'])
        
    def get_users(self):
        """Get list of all users"""
        return sorted(self.df['CustomerID'].unique())
    
    def get_categories(self):
        """Get list of all categories"""
        return sorted(self.df['Category'].unique())
    
    def get_user_purchases(self, user_id, month=None, category=None):
        """Get filtered purchases for a user"""
        user_data = self.df[self.df['CustomerID'] == user_id]
        
        if month:
            user_data = user_data[user_data['Month'] == month]
        
        if category:
            user_data = user_data[user_data['Category'] == category]
        
        return user_data.to_dict('records')
    
    def analyze_purchase_patterns(self, user_id):
        """Analyze purchase patterns for recommendations"""
        user_data = self.df[self.df['CustomerID'] == user_id]
        
        # Group by product and analyze frequency
        product_analysis = user_data.groupby(['Item Name', 'Category']).agg({
            'OrderDate': ['count', 'min', 'max'],
            'CleanPrice': 'mean',
            'Quantity': 'sum'
        }).round(2)
        
        # Flatten column names
        product_analysis.columns = ['purchase_count', 'first_purchase', 'last_purchase', 'avg_price', 'total_quantity']
        
        # Calculate days between first and last purchase
        product_analysis['days_span'] = (product_analysis['last_purchase'] - product_analysis['first_purchase']).dt.days
        
        # Calculate average interval between purchases
        product_analysis['avg_interval'] = product_analysis['days_span'] / (product_analysis['purchase_count'] - 1)
        product_analysis['avg_interval'] = product_analysis['avg_interval'].fillna(0)
        
        return product_analysis.reset_index()
    
    def generate_recommendations(self, user_id, min_purchases=2, target_interval_days=30):
        """Generate bucket list recommendations based on purchase patterns"""
        analysis = self.analyze_purchase_patterns(user_id)
        
        # Filter for products with regular purchase patterns
        recommendations = analysis[
            (analysis['purchase_count'] >= min_purchases) & 
            (analysis['avg_interval'] > 0) &
            (analysis['avg_interval'] <= target_interval_days * 1.5) &
            (analysis['avg_interval'] >= target_interval_days * 0.5)
        ]
        
        # Sort by purchase frequency and recency
        recommendations = recommendations.sort_values(['purchase_count', 'avg_interval'], ascending=[False, True])
        
        # Create bucket list with categories
        bucket_list = []
        for _, row in recommendations.iterrows():
            bucket_list.append({
                'item': row['Item Name'],
                'category': row['Category'],
                'purchase_count': int(row['purchase_count']),
                'avg_interval_days': round(row['avg_interval'], 1),
                'avg_price': round(row['avg_price'], 2),
                'recommendation_reason': f"Purchased {int(row['purchase_count'])} times, avg every {round(row['avg_interval'], 1)} days"
            })
        
        return bucket_list[:15]  # Top 15 recommendations
    
    def get_spending_summary(self, user_id, month=None):
        """Get spending summary by category"""
        user_data = self.df[self.df['CustomerID'] == user_id]
        
        if month:
            user_data = user_data[user_data['Month'] == month]
        
        summary = user_data.groupby('Category').agg({
            'CleanPrice': 'sum',
            'OrderID': 'nunique',
            'Item Name': 'count'
        }).round(2)
        
        summary.columns = ['total_spent', 'num_orders', 'num_items']
        return summary.reset_index().to_dict('records')
    
    def get_monthly_trends(self, user_id):
        """Get monthly spending trends"""
        user_data = self.df[self.df['CustomerID'] == user_id]
        
        monthly = user_data.groupby(['Month', 'Category']).agg({
            'CleanPrice': 'sum'
        }).round(2).reset_index()
        
        return monthly.to_dict('records')

# Example usage and testing
if __name__ == "__main__":
    analyzer = PurchaseAnalyzer('walmart_distributed_purchases.csv')
    
    # Test with first user
    users = analyzer.get_users()
    print(f"Users found: {users}")
    
    if users:
        test_user = users[0]
        print(f"\nAnalyzing user: {test_user}")
        
        # Get recommendations
        recommendations = analyzer.generate_recommendations(test_user)
        print(f"\nTop recommendations:")
        for rec in recommendations[:5]:
            print(f"- {rec['item']} ({rec['category']}) - {rec['recommendation_reason']}")
        
        # Get categories
        categories = analyzer.get_categories()
        print(f"\nCategories: {categories}")
        
        # Get spending summary
        summary = analyzer.get_spending_summary(test_user)
        print(f"\nSpending by category:")
        for cat in summary[:5]:
            print(f"- {cat['Category']}: ${cat['total_spent']}")
