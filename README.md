# 🛒 Walmart User Dashboard

An interactive web dashboard for analyzing user purchase data with AI-powered recommendations and visualizations.

## 🌟 Features

- **Interactive Analytics**: Filter purchases by month and category
- **AI Recommendations**: Smart bucket list based on purchase patterns
- **Visual Insights**: Charts and graphs for spending trends
- **User-Friendly Interface**: Modern, responsive design
- **Real-time Data**: Live filtering and updates

## 🛠️ Tech Stack

- **Backend**: Flask (Python API)
- **Frontend**: Dash with Plotly (Interactive visualizations)
- **Data Analysis**: Pandas, NumPy
- **Styling**: Bootstrap Components
- **Deployment**: Heroku-ready

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Install required packages
pip install -r requirements.txt
```

### 2. Run the Dashboard

```powershell
# Option 1: Run both servers automatically
python run_dashboard.py

# Option 2: Run servers separately
# Terminal 1 - Flask API:
python app.py

# Terminal 2 - Dash Dashboard:
python dashboard.py
```

### 3. Access the Dashboard

- **Dashboard**: http://localhost:8050
- **API Endpoints**: http://localhost:5000/api

## 📊 Dashboard Features

### Analytics Tab
- Spending breakdown by category (pie chart)
- Monthly spending trends (bar chart)
- Key metrics cards

### Shopping Patterns Tab
- Most frequently purchased items
- Purchase amount distribution
- Shopping behavior analysis

### Smart Bucket List Tab
- AI-generated recommendations based on purchase history
- Editable shopping list
- Recommendation explanations

### Spending Trends Tab
- Category spending over time
- Total monthly spending trends
- Seasonal pattern analysis

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users` | GET | Get list of all users |
| `/api/categories` | GET | Get product categories |
| `/api/users/{id}/purchases` | GET | Get user purchases (with filters) |
| `/api/users/{id}/recommendations` | GET | Get AI recommendations |
| `/api/users/{id}/spending-summary` | GET | Get spending summary |
| `/api/users/{id}/monthly-trends` | GET | Get monthly trends |
| `/api/users/{id}/bucket-list` | GET/POST | Manage bucket list |

### Example API Usage

```python
import requests

# Get all users
response = requests.get("http://localhost:5000/api/users")
users = response.json()

# Get user purchases for January
params = {"month": 1}
response = requests.get("http://localhost:5000/api/users/U001/purchases", params=params)
purchases = response.json()

# Get AI recommendations
response = requests.get("http://localhost:5000/api/users/U001/recommendations")
recommendations = response.json()
```

## 🎯 AI Recommendation Algorithm

The dashboard uses sophisticated analysis to generate personalized recommendations:

1. **Purchase Frequency Analysis**: Identifies regularly bought items
2. **Timing Patterns**: Calculates average intervals between purchases
3. **Category Preferences**: Analyzes spending patterns by category
4. **Seasonal Trends**: Considers monthly purchasing behavior

### Recommendation Criteria:
- Minimum 2 purchases of the same item
- Average purchase interval between 15-45 days
- Recent purchase activity
- Price stability

## 📁 Project Structure

```
User_Dash_Board/
├── walmart_distributed_purchases.csv  # Dataset
├── app.py                             # Flask API server
├── dashboard.py                       # Dash frontend
├── data_analyzer.py                   # Data analysis engine
├── run_dashboard.py                   # Startup script
├── requirements.txt                   # Dependencies
├── Procfile                          # Heroku deployment
├── .env                              # Configuration
└── README.md                         # Documentation
```

## 🌐 Deployment to Heroku

### 1. Prepare for Deployment

```powershell
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Install Heroku CLI and login
heroku login
```

### 2. Create Heroku App

```powershell
# Create new Heroku app
heroku create your-app-name

# Add PostgreSQL (optional, for future use)
heroku addons:create heroku-postgresql:hobby-dev
```

### 3. Deploy

```powershell
# Deploy to Heroku
git push heroku main

# Open your deployed app
heroku open
```

### 4. Set Environment Variables

```powershell
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
```

## 🔍 Data Analysis Features

### Purchase Pattern Recognition
- **Frequency Analysis**: Identifies how often users buy specific items
- **Interval Calculation**: Determines average time between purchases
- **Category Segmentation**: Groups purchases by product categories
- **Trend Detection**: Spots seasonal and monthly patterns

### Smart Recommendations
- **Replenishment Alerts**: Suggests when to reorder consumables
- **Category Diversification**: Recommends trying new product categories
- **Budget Optimization**: Identifies cost-effective alternatives
- **Seasonal Suggestions**: Proposes seasonal items based on timing

## 📈 Metrics and KPIs

The dashboard tracks key performance indicators:

- **Total Spending**: Cumulative purchase amounts
- **Purchase Frequency**: Number of shopping trips
- **Category Distribution**: Spending across different product types
- **Average Order Value**: Mean purchase amount
- **Product Diversity**: Number of unique items purchased

## 🛡️ Security Considerations

- Environment variables for sensitive configuration
- Input validation on all API endpoints
- CORS protection for cross-origin requests
- Rate limiting for API calls (recommended for production)

## 🔄 Future Enhancements

- **Database Integration**: PostgreSQL for persistent storage
- **User Authentication**: Login system for multiple users
- **Push Notifications**: Shopping reminders
- **Mobile App**: React Native companion app
- **Machine Learning**: Advanced recommendation algorithms
- **Social Features**: Shared shopping lists
- **Price Tracking**: Historical price analysis
- **Inventory Management**: Stock level monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```powershell
   # Kill processes on ports 5000 and 8050
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   ```

2. **Import Errors**
   ```powershell
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Data Loading Issues**
   - Ensure `walmart_distributed_purchases.csv` is in the project root
   - Check file permissions and encoding (should be UTF-8)

4. **API Connection Errors**
   - Verify Flask server is running on port 5000
   - Check firewall settings

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation
3. Examine browser console for frontend errors
4. Check server logs for backend issues


