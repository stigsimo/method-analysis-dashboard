# Method Analysis Dashboard

Interactive network visualization for research method co-occurrence analysis.

## Features

- **Interactive Network Visualization**: Circular layout showing method relationships
- **Edge Clicking**: Click edges to see papers using both methods
- **Node Highlighting**: Click nodes to highlight all connections
- **Fuzzy Search**: Search methods with abbreviations and variants
- **Category Filtering**: Filter methods by research categories
- **Trend Analysis**: View method adoption over time

## Installation with UV

[UV](https://github.com/astral-sh/uv) is a fast Python package manager. It's recommended for this project.

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Setup Project

```bash
# Clone or download project
cd method_analysis_dashboard

# Create virtual environment and install dependencies (one command!)
uv sync

# This automatically:
# - Creates .venv/
# - Installs Python 3.11 if needed
# - Installs all dependencies from pyproject.toml
```

### Run Dashboard

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run dashboard
python dashboard.py

# Or directly with uv (no activation needed)
uv run python dashboard.py
```

## Alternative: Traditional Installation

If you prefer pip:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Or from requirements.txt
pip install -r requirements.txt
```

## Project Structure

```
method_analysis_dashboard/
├── dashboard.py              # Main application
├── config.py                 # Configuration
├── data_processing.py        # Data loading
├── plotting.py               # Visualizations
├── callbacks.py              # Dash callbacks
├── layout.py                 # UI layout
├── pyproject.toml           # Project configuration (UV/pip)
├── .python-version          # Python version for UV
├── README.md                # This file
│
├── config/                   # Configuration files
│   ├── method_categories.json
│   ├── method_shortnames.json
│   ├── method_variants.json
│   └── topic_names.json
│
└── data/                     # Data files
    └── your_data.csv
```

## Configuration

### 1. Run Setup

```bash
python setup.py
```

This creates `config/` and `data/` directories with placeholder files.

### 2. Add Your Data

Move your files:
- CSV → `data/your_data.csv`
- method_categories → `config/method_categories.json`
- method_shortnames → `config/method_shortnames.json`
- method_variant_groups → `config/method_variants.json`

### 3. Update config.py

```python
CSV_PATH = r'data/your_data.csv'
TOPIC_INDICES = [2, 5, 6, 7, 8, 13]  # Your topics
```

## Configuration Files

**method_categories.json** - Map methods to categories:
```json
{
  "monte carlo simulation": "Risk, reliability and probabilistic methods",
  "machine learning": "Intelligent systems"
}
```

**method_shortnames.json** - Display names:
```json
{
  "monte carlo simulation": "Monte Carlo",
  "artificial neural network": "ANN"
}
```

**method_variants.json** - Alternative terms:
```json
{
  "monte carlo simulation": [
    "monte carlo",
    "monte carlo simulation",
    "mcs"
  ]
}
```

## Usage

### Start Dashboard

```bash
# With UV
uv run python dashboard.py

# Or activate venv first
source .venv/bin/activate
python dashboard.py
```

Then open: http://localhost:8050

### Development Commands

```bash
# Install dev dependencies
uv sync --all-extras

# Format code
uv run black .

# Lint code  
uv run ruff check .

# Run tests (if added)
uv run pytest
```

### Customize Settings

Edit `config.py`:

```python
PORT = 8050               # Dashboard port
HOST = '127.0.0.1'       # Local only
# HOST = '0.0.0.0'       # Network accessible
DEBUG = False            # Production mode
```

## Data Format

CSV file should contain:

- `paperId`: Unique identifier
- `title`: Paper title
- `year`: Publication year
- `citationCount`: Citation count
- `Method_1` through `Method_10`: Method names
- `Primary_Topic_Index`, `Secondary_Topic_Index`: Topic categories
- Optional: `authors`, `doi`

## Deployment

### Local Network

```python
# In config.py
HOST = '0.0.0.0'
```

Access from other computers: `http://YOUR_IP:8050`

### Docker (recommended for production)

```bash
# Build image
docker build -t method-dashboard .

# Run container
docker run -p 8050:8050 method-dashboard
```

### Production Server

Options:
- **Gunicorn**: `uv run gunicorn dashboard:app.server --bind 0.0.0.0:8050`
- **Docker**: See Dockerfile
- **Systemd**: See deployment docs

## UV Benefits

✅ **10-100x faster** than pip  
✅ **Automatic Python version management**  
✅ **Unified dependency resolution**  
✅ **Lock file support** (uv.lock)  
✅ **Works offline** (cached packages)  
✅ **Compatible with pip/pyproject.toml**

## Troubleshooting

**No methods displayed?**
- Check topic indices in `config.py`
- Verify CSV path is correct
- Check method name normalization

**UV sync fails?**
- Update UV: `uv self update`
- Check Python version: `python --version`
- Try: `uv sync --reinstall`

**Search not working?**
- Ensure `method_variants.json` is loaded
- Check method names match between CSV and config files

## License

MIT License

## Contact

For questions or issues, contact: [your email]
