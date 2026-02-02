"""
Configuration and constants for Method Analysis Dashboard
"""
import os
# Topic indices for filtering
TOPIC_INDICES = [2, 5, 6, 7, 8, 13]

# Data paths
CSV_PATH = r'data/enhanced_method_analysis_2026_01_06_reliability_resilience_power_systems.csv'
CONFIG_DIR = 'config'

# Dashboard settings
DEBUG = False
PORT = int(os.environ.get('PORT', 8050))  # Use Render's PORT or default to 8050
HOST = '0.0.0.0'  # Change to '127.0.0.1' for local only

# Network visualization defaults
DEFAULT_MIN_COOC = 5
DEFAULT_MAX_EDGES = 5
DEFAULT_TOP_N = 15
MIN_PAPERS_PER_METHOD = 4

# Method name normalization
SPELLING_MAP = {
    'optimisation': 'optimization',
    'optimise': 'optimize',
    'optimised': 'optimized',
    'optimising': 'optimizing',
    'behaviour': 'behavior',
    'modelling': 'modeling',
    'colour': 'color',
    'centre': 'center',
    'analyse': 'analyze',
    'parameterise': 'parameterize',
}
