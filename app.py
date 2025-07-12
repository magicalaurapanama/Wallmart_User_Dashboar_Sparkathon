from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from data_analyzer import PurchaseAnalyzer
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'walmart-dashboard-secret-key')

# Initialize the data analyzer
try:
    analyzer = PurchaseAnalyzer('walmart_distributed_purchases.csv')
    print("Data analyzer initialized successfully")
except Exception as e:
    print(f"Error initializing analyzer: {e}")
    analyzer = None

# Store user bucket lists (in production, this would be in a database)
user_bucket_lists = {}

@app.route('/')
def home():
    """Home page with basic info"""
    return jsonify({
        "message": "Walmart User Dashboard API",
        "version": "1.0",
        "endpoints": [
            "/api/users",
            "/api/categories", 
            "/api/users/<user_id>/purchases",
            "/api/users/<user_id>/recommendations",
            "/api/users/<user_id>/spending-summary",
            "/api/users/<user_id>/monthly-trends",
            "/api/users/<user_id>/bucket-list"
        ]
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of all users"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        users = analyzer.get_users()
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of all product categories"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        categories = analyzer.get_categories()
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/purchases', methods=['GET'])
def get_user_purchases(user_id):
    """Get purchases for a specific user with optional filters"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        month = request.args.get('month', type=int)
        category = request.args.get('category')
        
        purchases = analyzer.get_user_purchases(user_id, month, category)
        return jsonify({
            "user_id": user_id,
            "filters": {
                "month": month,
                "category": category
            },
            "purchases": purchases,
            "count": len(purchases)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/recommendations', methods=['GET'])
def get_user_recommendations(user_id):
    """Get AI-generated recommendations for a user's bucket list"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        min_purchases = request.args.get('min_purchases', default=2, type=int)
        target_interval = request.args.get('target_interval', default=30, type=int)
        
        recommendations = analyzer.generate_recommendations(
            user_id, min_purchases, target_interval
        )
        
        return jsonify({
            "user_id": user_id,
            "recommendations": recommendations,
            "count": len(recommendations),
            "criteria": {
                "min_purchases": min_purchases,
                "target_interval_days": target_interval
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/spending-summary', methods=['GET'])
def get_spending_summary(user_id):
    """Get spending summary by category for a user"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        month = request.args.get('month', type=int)
        summary = analyzer.get_spending_summary(user_id, month)
        
        return jsonify({
            "user_id": user_id,
            "month": month,
            "spending_summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/monthly-trends', methods=['GET'])
def get_monthly_trends(user_id):
    """Get monthly spending trends for a user"""
    if not analyzer:
        return jsonify({"error": "Data analyzer not available"}), 500
    
    try:
        trends = analyzer.get_monthly_trends(user_id)
        return jsonify({
            "user_id": user_id,
            "monthly_trends": trends
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/bucket-list', methods=['GET', 'POST'])
def manage_bucket_list(user_id):
    """Get or update user's custom bucket list"""
    if request.method == 'GET':
        # Return current bucket list or recommendations if none exists
        custom_list = user_bucket_lists.get(user_id, [])
        
        if not custom_list and analyzer:
            # If no custom list, return AI recommendations
            try:
                recommendations = analyzer.generate_recommendations(user_id)
                return jsonify({
                    "user_id": user_id,
                    "bucket_list": recommendations,
                    "type": "ai_generated",
                    "message": "Showing AI-generated recommendations. Use POST to save custom list."
                })
            except:
                pass
        
        return jsonify({
            "user_id": user_id,
            "bucket_list": custom_list,
            "type": "custom" if custom_list else "empty"
        })
    
    elif request.method == 'POST':
        # Update bucket list
        try:
            data = request.get_json()
            bucket_list = data.get('bucket_list', [])
            
            # Validate bucket list format
            for item in bucket_list:
                if not isinstance(item, dict) or 'item' not in item:
                    return jsonify({"error": "Invalid bucket list format"}), 400
            
            user_bucket_lists[user_id] = bucket_list
            
            return jsonify({
                "user_id": user_id,
                "message": "Bucket list updated successfully",
                "bucket_list": bucket_list,
                "count": len(bucket_list)
            })
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "analyzer_available": analyzer is not None
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
