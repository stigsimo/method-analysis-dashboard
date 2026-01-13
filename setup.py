#!/usr/bin/env python
"""
Setup script to create project structure and empty config files
"""

import os
import json


def main():
    """Create directory structure and placeholder files."""

    print("\n" + "="*70)
    print("📁 Setting up Method Analysis Dashboard")
    print("="*70 + "\n")

    # Create directories
    os.makedirs('config', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    print("✅ Created directories: config/, data/")

    # Create empty config files
    config_files = {
        'config/method_categories.json': {},
        'config/method_shortnames.json': {},
        'config/method_variants.json': {},
    }

    for filepath, default_content in config_files.items():
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=2)
            print(f"✅ Created {filepath}")
        else:
            print(f"ℹ️  {filepath} already exists")

    print("\n" + "="*70)
    print("✅ Setup complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Move your CSV file to data/ folder")
    print("2. Populate config/*.json files:")
    print("   - method_categories.json: method → category mapping")
    print("   - method_shortnames.json: method → display name")
    print("   - method_variants.json: method → [variant terms]")
    print("3. Update CSV_PATH in config.py")
    print("4. Run: python dashboard.py")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
