import threading
import time
import subprocess
import sys
import os

def start_flask_api():
    """Start the Flask API server"""
    print("Starting Flask API server on port 5000...")
    os.system("python app.py")

def start_dash_dashboard():
    """Start the Dash dashboard server"""
    print("Starting Dash dashboard on port 8050...")
    time.sleep(3)  # Wait for Flask to start
    os.system("python dashboard.py")

def main():
    """Start both servers"""
    print("🚀 Starting Walmart User Dashboard...")
    print("=" * 50)
    
    # Start Flask API in a separate thread
    flask_thread = threading.Thread(target=start_flask_api)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Dash dashboard
    start_dash_dashboard()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)
