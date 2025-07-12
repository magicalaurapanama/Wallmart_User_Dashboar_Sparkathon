import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
from datetime import datetime
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Walmart User Dashboard"

# API base URL (change this when deploying)
API_BASE = "http://localhost:5000/api"

# Helper functions
def make_api_request(endpoint, params=None):
    """Make API request with error handling"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def create_metric_card(title, value, subtitle="", color="primary", icon=""):
    """Create a metric card component with enhanced styling"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H3(value, className=f"text-{color} mb-1 fw-bold"),
                    html.P(title, className="card-text mb-1 fw-semibold"),
                    html.Small(subtitle, className="text-muted")
                ], width=8),
                dbc.Col([
                    html.I(className=f"{icon} fa-2x text-{color} opacity-75")
                ], width=4, className="text-center") if icon else None
            ], align="center")
        ])
    ], className="shadow-sm border-0", style={
        "height": "120px", 
        "background": f"linear-gradient(135deg, rgba(var(--bs-{color}-rgb), 0.1) 0%, rgba(var(--bs-{color}-rgb), 0.05) 100%)",
        "border-left": f"4px solid var(--bs-{color})"
    })

# Layout
app.layout = dbc.Container([
    # Header with gradient background
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🛒 Walmart User Dashboard", 
                       className="text-white mb-0 display-4 fw-bold"),
                html.P("Intelligent Shopping Analytics & Recommendations", 
                       className="text-white-50 lead mb-0")
            ], className="text-center py-4")
        ], width=12)
    ], className="mb-4", style={
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "border-radius": "15px",
        "box-shadow": "0 10px 30px rgba(0,0,0,0.1)"
    }),
    
    # User Selection Row with improved styling
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("👤 Select User", className="form-label fw-bold text-primary mb-2"),
                    dcc.Dropdown(
                        id='user-dropdown',
                        placeholder="Choose a user to analyze...",
                        style={"marginBottom": "0"},
                        className="shadow-sm",
                        optionHeight=35,
                        clearable=False
                    )
                ])
            ], className="shadow-sm border-0")
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("📊 Quick Stats", className="form-label fw-bold text-success mb-2"),
                    html.Div(id="user-stats", children="Select a user to view statistics",
                           className="text-muted")
                ])
            ], className="shadow-sm border-0")
        ], width=6)
    ], className="mb-4"),
    
    # Filters Row with enhanced design
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("📅 Filter by Month", className="form-label fw-bold text-info mb-2"),
                    dcc.Dropdown(
                        id='month-filter',
                        options=[
                            {'label': 'All Months', 'value': None},
                            {'label': 'January', 'value': 1},
                            {'label': 'February', 'value': 2},
                            {'label': 'March', 'value': 3},
                            {'label': 'April', 'value': 4},
                            {'label': 'May', 'value': 5},
                            {'label': 'June', 'value': 6},
                            {'label': 'July', 'value': 7},
                            {'label': 'August', 'value': 8},
                            {'label': 'September', 'value': 9},
                            {'label': 'October', 'value': 10},
                            {'label': 'November', 'value': 11},
                            {'label': 'December', 'value': 12}
                        ],
                        value=None,
                        placeholder="All months",
                        className="shadow-sm",
                        optionHeight=35,
                        clearable=False
                    )
                ])
            ], className="shadow-sm border-0")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("🏷️ Filter by Category", className="form-label fw-bold text-warning mb-2"),
                    dcc.Dropdown(
                        id='category-filter',
                        placeholder="All categories",
                        className="shadow-sm",
                        optionHeight=35,
                        clearable=False
                    )
                ])
            ], className="shadow-sm border-0")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("⚡ Actions", className="form-label fw-bold text-danger mb-2"),
                    dbc.Button("🔄 Refresh Data", id="refresh-btn", 
                             color="gradient-primary", size="sm", className="w-100 shadow-sm")
                ])
            ], className="shadow-sm border-0")
        ], width=4)
    ], className="mb-5"),
    
    # Metrics Row
    dbc.Row([
        dbc.Col([
            html.Div(id="metrics-cards")
        ], width=12)
    ], className="mb-4"),
    
    # Main Content Tabs
    dbc.Tabs([
        dbc.Tab(label="📊 Purchase Analytics", tab_id="analytics"),
        dbc.Tab(label="🛍️ Shopping Patterns", tab_id="patterns"),
        dbc.Tab(label="📝 Smart Bucket List", tab_id="bucket-list"),
        dbc.Tab(label="� My Saved Items", tab_id="saved-items"),
        dbc.Tab(label="�💰 Spending Trends", tab_id="trends")
    ], id="main-tabs", active_tab="analytics", className="mb-3"),
    
    # Tab Content
    html.Div(id="tab-content"),
    
    # Hidden divs for storing data
    html.Div(id="users-data", style={"display": "none"}),
    html.Div(id="categories-data", style={"display": "none"}),
    html.Div(id="purchases-data", style={"display": "none"}),
    html.Div(id="bucket-list-data", style={"display": "none"}),
    html.Div(id="saved-items-data", style={"display": "none"}),
    
], fluid=True)

# Callbacks

@app.callback(
    [Output('users-data', 'children'),
     Output('categories-data', 'children')],
    [Input('refresh-btn', 'n_clicks')],
    prevent_initial_call=False
)
def load_initial_data(n_clicks):
    """Load users and categories data"""
    users_data = make_api_request("/users")
    categories_data = make_api_request("/categories")
    
    return json.dumps(users_data), json.dumps(categories_data)

@app.callback(
    [Output('user-dropdown', 'options'),
     Output('category-filter', 'options')],
    [Input('users-data', 'children'),
     Input('categories-data', 'children')]
)
def update_dropdowns(users_json, categories_json):
    """Update dropdown options"""
    user_options = []
    category_options = [{'label': 'All Categories', 'value': None}]
    
    if users_json:
        try:
            users_data = json.loads(users_json)
            if 'users' in users_data:
                user_options = [{'label': user, 'value': user} for user in users_data['users']]
        except:
            pass
    
    if categories_json:
        try:
            categories_data = json.loads(categories_json)
            if 'categories' in categories_data:
                category_options.extend([
                    {'label': cat, 'value': cat} for cat in categories_data['categories']
                ])
        except:
            pass
    
    return user_options, category_options

@app.callback(
    Output('purchases-data', 'children'),
    [Input('user-dropdown', 'value'),
     Input('month-filter', 'value'),
     Input('category-filter', 'value'),
     Input('refresh-btn', 'n_clicks')],
    prevent_initial_call=False
)
def load_purchase_data(user_id, month, category, n_clicks):
    """Load purchase data based on filters"""
    if not user_id:
        return json.dumps({})
    
    params = {}
    # Fix month filtering - convert to int if not None
    if month is not None and month != "" and month != "None":
        try:
            params['month'] = int(month)
        except (ValueError, TypeError):
            pass
    
    # Fix category filtering - handle string values properly
    if category is not None and category != "" and category != "None" and category != "All Categories":
        params['category'] = str(category)
    
    print(f"🔍 Loading purchases for user: {user_id}")
    print(f"📅 Month filter: {month} -> params month: {params.get('month', 'None')}")
    print(f"🏷️ Category filter: {category} -> params category: {params.get('category', 'None')}")
    print(f"📋 Final params: {params}")
    
    purchases_data = make_api_request(f"/users/{user_id}/purchases", params)
    print(f"📦 Received {len(purchases_data.get('purchases', []))} purchases")
    return json.dumps(purchases_data)

@app.callback(
    Output('user-stats', 'children'),
    [Input('purchases-data', 'children')]
)
def update_user_stats(purchases_json):
    """Update user statistics"""
    if not purchases_json:
        return "No data available"
    
    try:
        data = json.loads(purchases_json)
        if 'purchases' in data:
            purchases = data['purchases']
            total_items = len(purchases)
            total_spent = sum([p.get('CleanPrice', 0) or 0 for p in purchases])
            
            return f"📦 {total_items} items | 💰 ${total_spent:.2f} total"
    except:
        pass
    
    return "Unable to load stats"

@app.callback(
    Output('metrics-cards', 'children'),
    [Input('purchases-data', 'children'),
     Input('user-dropdown', 'value')]
)
def update_metrics(purchases_json, user_id):
    """Update metrics cards"""
    if not user_id or not purchases_json:
        return []
    
    try:
        data = json.loads(purchases_json)
        purchases = data.get('purchases', [])
        
        if not purchases:
            return [dbc.Alert("No purchases found for the selected filters.", color="info")]
        
        # Calculate metrics
        total_spent = sum([p.get('CleanPrice', 0) or 0 for p in purchases])
        total_items = len(purchases)
        unique_products = len(set([p.get('Item Name', '') for p in purchases]))
        avg_price = total_spent / total_items if total_items > 0 else 0
        
        # Category breakdown
        categories = {}
        for p in purchases:
            cat = p.get('Category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + (p.get('CleanPrice', 0) or 0)
        
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "None"
        
        return dbc.Row([
            dbc.Col([
                create_metric_card("Total Spent", f"${total_spent:.2f}", "All purchases", "success", "fas fa-dollar-sign")
            ], width=3),
            dbc.Col([
                create_metric_card("Items Purchased", str(total_items), "Total quantity", "primary", "fas fa-shopping-bag")
            ], width=3),
            dbc.Col([
                create_metric_card("Unique Products", str(unique_products), "Different items", "info", "fas fa-cube")
            ], width=3),
            dbc.Col([
                create_metric_card("Top Category", top_category, f"${categories.get(top_category, 0):.2f}", "warning", "fas fa-star")
            ], width=3)
        ])
    
    except Exception as e:
        return [dbc.Alert(f"Error calculating metrics: {str(e)}", color="danger")]

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('user-dropdown', 'value')],
    [State('purchases-data', 'children'),
     State('saved-items-data', 'children')],
    prevent_initial_call=False
)
def update_tab_content(active_tab, user_id, purchases_json, saved_items_json):
    """Update content based on active tab"""
    if not user_id:
        return dbc.Alert("Please select a user to view dashboard content.", color="info")
    
    print(f"🔄 Updating tab content for: {active_tab}, user: {user_id}")
    
    try:
        if active_tab == "analytics":
            return create_analytics_tab(purchases_json)
        elif active_tab == "patterns":
            return create_patterns_tab(purchases_json, user_id)
        elif active_tab == "bucket-list":
            return create_bucket_list_tab(user_id)
        elif active_tab == "saved-items":
            return create_saved_items_tab(saved_items_json, user_id)
        elif active_tab == "trends":
            return create_trends_tab(user_id)
        else:
            return html.Div("Select a tab to view content")
    except Exception as e:
        print(f"❌ Error in update_tab_content: {str(e)}")
        return dbc.Alert(f"Error loading tab content: {str(e)}", color="danger")

def create_analytics_tab(purchases_json):
    """Create analytics tab content"""
    if not purchases_json:
        return dbc.Alert("No purchase data available.", color="warning")
    
    try:
        data = json.loads(purchases_json)
        purchases = data.get('purchases', [])
        
        if not purchases:
            return dbc.Alert("No purchases found for the selected filters.", color="info")
        
        df = pd.DataFrame(purchases)
        
        # Category spending chart with improved styling
        category_spending = df.groupby('Category')['CleanPrice'].sum().reset_index()
        category_fig = px.pie(
            category_spending, 
            values='CleanPrice', 
            names='Category',
            title="💰 Spending by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        category_fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>"
        )
        category_fig.update_layout(
            font=dict(size=14),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5),
            margin=dict(t=60, b=20, l=20, r=20)
        )
        
        # Monthly spending with enhanced visualization
        df['OrderDate'] = pd.to_datetime(df['OrderDate'])
        df['Month'] = df['OrderDate'].dt.month
        monthly_spending = df.groupby('Month')['CleanPrice'].sum().reset_index()
        
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        monthly_spending['MonthName'] = monthly_spending['Month'].map(month_names)
        
        monthly_fig = px.bar(
            monthly_spending,
            x='MonthName',
            y='CleanPrice',
            title="📈 Monthly Spending Trend",
            color='CleanPrice',
            color_continuous_scale='Blues'
        )
        monthly_fig.update_layout(
            xaxis_title="Month", 
            yaxis_title="Amount Spent ($)",
            font=dict(size=14),
            margin=dict(t=60, b=40, l=40, r=20),
            showlegend=False
        )
        monthly_fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Total Spent: $%{y:.2f}<extra></extra>"
        )
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Category Analysis", className="mb-0 text-primary")),
                        dbc.CardBody([
                            dcc.Graph(figure=category_fig, style={"height": "400px"})
                        ])
                    ], className="shadow-sm border-0")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Monthly Trends", className="mb-0 text-success")),
                        dbc.CardBody([
                            dcc.Graph(figure=monthly_fig, style={"height": "400px"})
                        ])
                    ], className="shadow-sm border-0")
                ], width=6)
            ])
        ], fluid=True)
    
    except Exception as e:
        return dbc.Alert(f"Error creating analytics: {str(e)}", color="danger")

def create_patterns_tab(purchases_json, user_id):
    """Create shopping patterns tab"""
    try:
        data = json.loads(purchases_json) if purchases_json else {}
        purchases = data.get('purchases', [])
        
        if not purchases:
            return dbc.Alert("No purchase data available for pattern analysis.", color="info")
        
        df = pd.DataFrame(purchases)
        
        # Top products by frequency
        product_freq = df['Item Name'].value_counts().head(10)
        freq_fig = px.bar(
            x=product_freq.values,
            y=product_freq.index,
            orientation='h',
            title="Most Frequently Purchased Items"
        )
        freq_fig.update_layout(xaxis_title="Purchase Count", yaxis_title="Product")
        
        # Purchase amounts distribution
        amount_fig = px.histogram(
            df,
            x='CleanPrice',
            nbins=20,
            title="Purchase Amount Distribution"
        )
        amount_fig.update_layout(xaxis_title="Amount ($)", yaxis_title="Frequency")
        
        return dbc.Row([
            dbc.Col([
                dcc.Graph(figure=freq_fig)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=amount_fig)
            ], width=6)
        ])
    
    except Exception as e:
        return dbc.Alert(f"Error analyzing patterns: {str(e)}", color="danger")

def create_bucket_list_tab(user_id):
    """Create bucket list tab with recommendations"""
    if not user_id:
        return dbc.Alert("Please select a user to view recommendations.", color="info")
    
    try:
        print(f"🔍 Creating bucket list for user: {user_id}")
        
        # Get AI recommendations
        recommendations_data = make_api_request(f"/users/{user_id}/recommendations")
        
        if not recommendations_data or 'error' in recommendations_data:
            error_msg = recommendations_data.get('error', 'Unknown error') if recommendations_data else 'No response from API'
            print(f"❌ Error in recommendations: {error_msg}")
            return dbc.Alert(f"Error loading recommendations: {error_msg}", color="danger")
        
        recommendations = recommendations_data.get('recommendations', [])
        print(f"📋 Found {len(recommendations)} recommendations")
        
        if not recommendations:
            return dbc.Alert("No recommendations available for this user.", color="info")
        
        # Create compact recommendation items
        rec_items = []
        for i, rec in enumerate(recommendations[:12]):  # Show top 12
            try:
                item = dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            dbc.Checkbox(
                                id={"type": "recommendation-checkbox", "index": i},
                                value=False,
                                className="me-2"
                            )
                        ], width=1),
                        dbc.Col([
                            html.Div([
                                html.Strong(rec['item'], className="text-primary"),
                                html.Br(),
                                dbc.Badge(rec['category'], color="secondary", className="me-2"),
                                html.Span(f"${rec['avg_price']:.2f}", className="text-success fw-bold"),
                                html.Br(),
                                html.Small(rec['recommendation_reason'], className="text-muted")
                            ])
                        ], width=11)
                    ], align="center")
                ], className="border-0 py-2", style={"border-left": "3px solid #007bff"})
                rec_items.append(item)
            except Exception as e:
                print(f"❌ Error processing recommendation {i}: {str(e)}")
                continue
        
        print(f"✅ Created {len(rec_items)} recommendation items")
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H4("🤖 AI-Generated Recommendations", className="mb-3 text-primary"),
                    html.P("Select items to add to your shopping list:", className="text-muted mb-3"),
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6(f"📋 Recommended Items ({len(rec_items)} items)", className="mb-0 text-secondary")
                        ]),
                        dbc.CardBody([
                            dbc.ListGroup(rec_items, flush=True, className="mb-3") if rec_items else html.P("No items to display", className="text-muted")
                        ])
                    ], className="shadow-sm border-0")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("💾 Save Selected Items", id="save-bucket-btn", color="success", size="lg", className="me-3"),
                    dbc.Button("🔄 Refresh Recommendations", id="refresh-recommendations-btn", color="outline-primary", size="lg"),
                ], width=12, className="text-center mt-3")
            ]),
            html.Div(id="bucket-save-status", className="mt-3")
        ], fluid=True)
        
    except Exception as e:
        print(f"❌ Unexpected error in create_bucket_list_tab: {str(e)}")
        return dbc.Alert(f"Unexpected error: {str(e)}", color="danger")

def create_trends_tab(user_id):
    """Create spending trends tab"""
    if not user_id:
        return dbc.Alert("Please select a user to view trends.", color="info")
    
    # Get monthly trends
    trends_data = make_api_request(f"/users/{user_id}/monthly-trends")
    
    if 'error' in trends_data:
        return dbc.Alert(f"Error loading trends: {trends_data['error']}", color="danger")
    
    trends = trends_data.get('monthly_trends', [])
    
    if not trends:
        return dbc.Alert("No trend data available.", color="info")
    
    # Create trends visualization
    df = pd.DataFrame(trends)
    
    # Category trends over time
    trend_fig = px.line(
        df,
        x='Month',
        y='CleanPrice',
        color='Category',
        title="Spending Trends by Category Over Time"
    )
    trend_fig.update_layout(xaxis_title="Month", yaxis_title="Amount Spent ($)")
    
    # Total monthly spending
    monthly_total = df.groupby('Month')['CleanPrice'].sum().reset_index()
    total_fig = px.area(
        monthly_total,
        x='Month',
        y='CleanPrice',
        title="Total Monthly Spending"
    )
    total_fig.update_layout(xaxis_title="Month", yaxis_title="Total Spent ($)")
    
    return dbc.Row([
        dbc.Col([
            dcc.Graph(figure=trend_fig)
        ], width=12),
        dbc.Col([
            dcc.Graph(figure=total_fig)
        ], width=12)
    ])

def create_saved_items_tab(saved_items_json, user_id):
    """Create saved items tab showing user's saved shopping list"""
    if not user_id:
        return dbc.Alert("Please select a user to view saved items.", color="info")
    
    saved_items = []
    if saved_items_json:
        try:
            saved_data = json.loads(saved_items_json)
            saved_items = saved_data.get('items', [])
        except:
            pass
    
    if not saved_items:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-shopping-cart fa-4x text-muted mb-3"),
                        html.H3("Your Shopping List is Empty", className="text-muted"),
                        html.P("Add items from the Smart Bucket List tab to get started!", 
                               className="lead text-muted"),
                        dbc.Button("Go to Recommendations", id="go-to-bucket-btn", 
                                 color="primary", size="lg", className="mt-3")
                    ], className="text-center py-5")
                ], width=12)
            ])
        ], fluid=True)
    
    # Create saved item cards
    item_cards = []
    for i, item in enumerate(saved_items):
        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(item['name'], className="card-title text-success"),
                        html.P([
                            dbc.Badge(item['category'], color="info", className="me-2"),
                            html.Strong(f"${item['price']:.2f}", className="text-primary")
                        ], className="card-text"),
                        html.P(item.get('reason', ''), className="text-muted small")
                    ], width=9),
                    dbc.Col([
                        dbc.Button("🗑️", id={"type": "remove-item", "index": i}, 
                                 color="outline-danger", size="sm", className="float-end")
                    ], width=3)
                ])
            ])
        ], className="mb-3 shadow-sm", style={"border-left": "4px solid #28a745"})
        item_cards.append(card)
    
    total_cost = sum([item['price'] for item in saved_items])
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("🛒 My Shopping List", className="mb-3 text-success"),
                dbc.Alert([
                    html.H5(f"📋 {len(saved_items)} items | 💰 Total: ${total_cost:.2f}", 
                           className="mb-0 text-center")
                ], color="success", className="mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col(item_cards, width=12)
        ]),
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col([
                dbc.Button("🛍️ Export List", id="export-list-btn", color="primary", className="me-3"),
                dbc.Button("🗑️ Clear All", id="clear-all-btn", color="outline-danger"),
            ], width=12, className="text-center")
        ])
    ], fluid=True)

# Callback for saving selected recommendations
@app.callback(
    [Output('saved-items-data', 'children'),
     Output('bucket-save-status', 'children')],
    [Input('save-bucket-btn', 'n_clicks')],
    [State({"type": "recommendation-checkbox", "index": dash.dependencies.ALL}, 'value'),
     State('user-dropdown', 'value'),
     State('saved-items-data', 'children')],
    prevent_initial_call=True
)
def save_selected_items(n_clicks, checkbox_values, user_id, current_saved_json):
    """Save selected recommendations to user's shopping list"""
    if not n_clicks or not user_id:
        return dash.no_update, dash.no_update
    
    # Get current saved items
    current_saved = []
    if current_saved_json:
        try:
            saved_data = json.loads(current_saved_json)
            current_saved = saved_data.get('items', [])
        except:
            pass
    
    # Get recommendations data
    recommendations_data = make_api_request(f"/users/{user_id}/recommendations")
    recommendations = recommendations_data.get('recommendations', [])
    
    # Find selected items
    selected_items = []
    for i, is_selected in enumerate(checkbox_values):
        if is_selected and i < len(recommendations):
            rec = recommendations[i]
            selected_items.append({
                'name': rec['item'],
                'category': rec['category'],
                'price': rec['avg_price'],
                'reason': rec['recommendation_reason']
            })
    
    # Add to current saved items (avoid duplicates)
    existing_names = [item['name'] for item in current_saved]
    for item in selected_items:
        if item['name'] not in existing_names:
            current_saved.append(item)
    
    # Create success message
    if selected_items:
        status_message = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Successfully saved {len(selected_items)} items to your shopping list!"
        ], color="success", dismissable=True)
    else:
        status_message = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please select items to save to your list."
        ], color="warning", dismissable=True)
    
    return json.dumps({'items': current_saved}), status_message

# Callback for switching to bucket list tab
@app.callback(
    Output('main-tabs', 'active_tab'),
    [Input('go-to-bucket-btn', 'n_clicks')],
    prevent_initial_call=True
)
def go_to_bucket_list(n_clicks):
    """Switch to bucket list tab when button is clicked"""
    if n_clicks:
        return "bucket-list"
    return dash.no_update

# Callback for removing items from saved list
@app.callback(
    Output('saved-items-data', 'children', allow_duplicate=True),
    [Input({"type": "remove-item", "index": ALL}, 'n_clicks')],
    [State('saved-items-data', 'children')],
    prevent_initial_call=True
)
def remove_saved_item(n_clicks_list, current_saved_json):
    """Remove an item from the saved shopping list"""
    if not any(n_clicks_list) or not current_saved_json:
        return dash.no_update
    
    # Find which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_data = json.loads(button_id)
    index_to_remove = button_data['index']
    
    # Get current saved items
    try:
        saved_data = json.loads(current_saved_json)
        current_saved = saved_data.get('items', [])
    except:
        return dash.no_update
    
    # Remove the item at the specified index
    if 0 <= index_to_remove < len(current_saved):
        current_saved.pop(index_to_remove)
    
    return json.dumps({'items': current_saved})

# Callback for clearing all saved items
@app.callback(
    Output('saved-items-data', 'children', allow_duplicate=True),
    [Input('clear-all-btn', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_saved_items(n_clicks):
    """Clear all saved items"""
    if n_clicks:
        return json.dumps({'items': []})
    return dash.no_update

# Callback for refreshing recommendations
@app.callback(
    Output('main-tabs', 'active_tab', allow_duplicate=True),
    [Input('refresh-recommendations-btn', 'n_clicks')],
    prevent_initial_call=True
)
def refresh_recommendations(n_clicks):
    """Refresh recommendations by reloading the tab"""
    if n_clicks:
        return "bucket-list"  # This will trigger the tab content to reload
    return dash.no_update

# Separate callback to update analytics/patterns tabs when purchases data changes
@app.callback(
    Output('tab-content', 'children', allow_duplicate=True),
    [Input('purchases-data', 'children')],
    [State('main-tabs', 'active_tab'),
     State('user-dropdown', 'value')],
    prevent_initial_call=True
)
def update_data_dependent_tabs(purchases_json, active_tab, user_id):
    """Update tabs that depend on purchases data"""
    if not user_id or not active_tab:
        return dash.no_update
    
    # Only update tabs that depend on purchases data
    if active_tab in ["analytics", "patterns"]:
        try:
            if active_tab == "analytics":
                return create_analytics_tab(purchases_json)
            elif active_tab == "patterns":
                return create_patterns_tab(purchases_json, user_id)
        except Exception as e:
            print(f"❌ Error in update_data_dependent_tabs: {str(e)}")
            return dbc.Alert(f"Error loading tab content: {str(e)}", color="danger")
    
    return dash.no_update

if __name__ == '__main__':
    app.run(debug=True, port=8050)
