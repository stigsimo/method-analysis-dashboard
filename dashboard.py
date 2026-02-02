"""
Main Dashboard Application
Method Analysis Dashboard - Interactive network visualization

Usage:
    python dashboard.py

Then open: http://localhost:8050
"""

import dash

from config import CSV_PATH, CONFIG_DIR, DEBUG, PORT, HOST
from data_processing import load_dashboard_data
from layout import create_layout
from callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Method Analysis Dashboard"
)

# Expose server for deployment (required for Gunicorn)
server = app.server

def main():
    """Initialize and run dashboard."""
    
    # Load data
    print("\n" + "="*70)
    print("🚀 Starting Method Analysis Dashboard")
    print("="*70)
    
    data = load_dashboard_data(CSV_PATH, CONFIG_DIR)
    
    # Create layout
    app.layout = create_layout(data['all_categories'])
    
    # Register callbacks
    register_callbacks(app, data)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 Dashboard Ready!")
    print("="*70)
    print(f"Methods: {len(data['all_methods'])}")
    print(f"Papers: {len(data['papers_df'])}")
    print(f"Categories: {len(data['all_categories'])}")
    print()
    print("💡 Features:")
    print("  • Click method node → highlight connections")
    print("  • Click edge → show papers using both methods")
    print("  • Reset button → clear highlighting")
    print()
    print(f"🌐 Open browser to: http://localhost:{PORT}")
    print("="*70 + "\n")
    
    # Run server
    app.run(debug=DEBUG, host=HOST, port=PORT)
if __name__ == '__main__':
    main()
