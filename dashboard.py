"""
Main Dashboard Application
Method Analysis Dashboard - Interactive network visualization
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

# Load data at module level (required for production deployment)
print("\n" + "="*70)
print("🚀 Loading Method Analysis Dashboard Data")
print("="*70)
data = load_dashboard_data(CSV_PATH, CONFIG_DIR)

# Set layout at module level (required for production)
app.layout = create_layout(data['all_categories'])

# Register callbacks at module level
register_callbacks(app, data)

print("\n" + "="*70)
print("📊 Dashboard Ready!")
print("="*70)
print(f"Methods: {len(data['all_methods'])}")
print(f"Papers: {len(data['papers_df'])}")
print(f"Categories: {len(data['all_categories'])}")
print("="*70 + "\n")

def main():
    """Run the dashboard locally."""
    print(f"🌐 Open browser to: http://localhost:{PORT}")
    app.run(debug=DEBUG, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
