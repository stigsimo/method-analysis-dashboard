# UV Setup Guide

## What is UV?

UV is a fast Python package manager and project manager written in Rust. It's:
- **10-100x faster** than pip
- **Compatible** with existing pip/pyproject.toml projects
- **Manages Python versions** automatically
- **Has built-in virtual environment** management

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Alternative: pip
```bash
pip install uv
```

## Quick Start

```bash
# 1. One-command setup
./quickstart.sh          # Unix/Mac
quickstart.bat          # Windows

# Or manually:
uv sync                 # Install dependencies
python setup.py         # Create config structure

# 2. Add your data and config files

# 3. Run dashboard
uv run python dashboard.py
```

## UV Commands

### Project Setup
```bash
# Create venv and install dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras

# Update dependencies
uv sync --upgrade
```

### Running Code
```bash
# Run without activating venv
uv run python dashboard.py

# Run any Python script
uv run python your_script.py

# Or activate venv traditionally
source .venv/bin/activate  # Unix/Mac
.venv\Scripts\activate    # Windows
python dashboard.py
```

### Dependency Management
```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev pytest

# Remove dependency
uv remove package-name

# Show installed packages
uv pip list
```

### Python Version Management
```bash
# UV automatically uses .python-version file (3.11)

# Or specify manually
uv venv --python 3.11

# List available Python versions
uv python list
```

## Project Files

### pyproject.toml
Main project configuration. UV reads this for:
- Dependencies
- Project metadata
- Build configuration
- Tool settings (black, ruff)

### .python-version
Specifies Python version (3.11). UV automatically installs if missing.

### uv.lock
Auto-generated lock file (like package-lock.json). Ensures reproducible installs.
**Don't edit manually!**

## Common Tasks

### Fresh Install
```bash
rm -rf .venv uv.lock
uv sync
```

### Update All Dependencies
```bash
uv sync --upgrade
```

### Export to requirements.txt
```bash
uv pip freeze > requirements.txt
```

### Cache Management
```bash
# Show cache size
uv cache dir

# Clean cache
uv cache clean
```

## Deployment

### Docker (Recommended)
```bash
docker build -t method-dashboard .
docker run -p 8050:8050 method-dashboard
```

### Production Server
```bash
# Install production dependencies only
uv sync --no-dev

# Run with gunicorn
uv run gunicorn dashboard:app.server --bind 0.0.0.0:8050 --workers 4
```

## Troubleshooting

### UV command not found
Add to PATH or reinstall:
```bash
export PATH="$HOME/.cargo/bin:$PATH"  # Unix/Mac
```

### Wrong Python version
Check `.python-version` file:
```bash
cat .python-version  # Should be 3.11
```

### Dependency conflicts
```bash
uv sync --reinstall
```

### Cache issues
```bash
uv cache clean
uv sync --reinstall
```

## Benefits vs pip

| Feature | UV | pip |
|---------|----|----|
| Speed | ⚡ 10-100x faster | Slow |
| Python management | ✅ Built-in | ❌ Separate tool |
| Lock files | ✅ uv.lock | ❌ Manual |
| Offline mode | ✅ Cached | ❌ Requires network |
| Error messages | ✅ Clear | ⚠️ Cryptic |
| Compatibility | ✅ pip-compatible | ✅ Standard |

## Learn More

- UV Docs: https://docs.astral.sh/uv/
- GitHub: https://github.com/astral-sh/uv
- Blog: https://astral.sh/blog
