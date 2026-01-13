"""
Data loading and processing functions
"""

import os
import json
import pandas as pd
import numpy as np
from config import TOPIC_INDICES, SPELLING_MAP, MIN_PAPERS_PER_METHOD


def try_read_csv(file_path, sep_choices=(';', ',')):
    """Try to read CSV with different separators for robustness."""
    for sep in sep_choices:
        try:
            df = pd.read_csv(file_path, sep=sep, encoding='utf-8')
            if len(df.columns) == 1 and ',' in df.columns[0]:
                continue
            return df
        except Exception:
            continue
    raise ValueError(f"Could not load {file_path} with any separator.")


def normalize_method_name(method):
    """Normalize method names to handle variations in spelling, hyphenation, etc."""
    if pd.isna(method):
        return method

    text = str(method).lower().strip()
    text = text.replace('-', ' ').replace('_', ' ')

    for uk, us in SPELLING_MAP.items():
        text = text.replace(uk, us)

    text = ' '.join(text.split())
    return text


def load_json_config(file_path, description="config"):
    """Load JSON configuration file with error handling."""
    if not os.path.exists(file_path):
        print(f"   ⚠️  {description} not found: {os.path.basename(file_path)}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✅ Loaded {description}: {len(data)} entries")
        return data
    except Exception as e:
        print(f"   ❌ Error loading {description}: {e}")
        return None


def prepare_papers_dataframe(papers_df_wide):
    """Converts wide format to list format for methods."""
    base_cols = ['paperId', 'title', 'year', 'citationCount']

    if 'authors' not in papers_df_wide.columns:
        papers_df_wide['authors'] = 'Authors N/A'
    if 'doi' not in papers_df_wide.columns:
        papers_df_wide['doi'] = papers_df_wide['paperId']

    base_cols.extend(['authors', 'doi'])

    def extract_methods(row):
        methods = []
        for i in range(1, 11):
            method_col = f'Method_{i}'
            if pd.notna(row.get(method_col)) and row.get(method_col) != '':
                methods.append(row[method_col])
        return methods

    def extract_scores(row):
        scores = {}
        for i in range(1, 11):
            method_col = f'Method_{i}'
            score_col = f'Method_{i}_score'
            if pd.notna(row.get(method_col)) and row.get(method_col) != '':
                if pd.notna(row.get(score_col)):
                    scores[row[method_col]] = row[score_col]
        return scores

    papers_df = papers_df_wide[base_cols].copy()
    papers_df['methods'] = papers_df_wide.apply(extract_methods, axis=1)
    papers_df['method_scores'] = papers_df_wide.apply(extract_scores, axis=1)
    papers_df = papers_df[papers_df['methods'].apply(len) > 0]

    return papers_df


def build_cooccurrence_from_methods(
    df,
    method_cols=None,
    paper_id_col='paperId',
    min_papers=MIN_PAPERS_PER_METHOD,
    year_filter=None,
    citation_filter=0,
    normalize_methods=True,
    topic_filter=None,
    topic_cols=('Primary_Topic_Index', 'Secondary_Topic_Index'),
    topic_mode='ANY',
):
    """Build co-occurrence matrix from Method_1...Method_10 columns."""

    df_work = df.copy()

    # Apply filters
    if year_filter is not None and 'year' in df_work.columns:
        before = len(df_work)
        df_work = df_work[df_work['year'] >= year_filter]
        print(f"Year filter (≥{year_filter}): kept {len(df_work)}/{before} papers")

    if citation_filter > 0 and 'citationCount' in df_work.columns:
        before = len(df_work)
        df_work = df_work[df_work['citationCount'] >= citation_filter]
        print(f"Citation filter (≥{citation_filter}): kept {len(df_work)}/{before} papers")

    if topic_filter is not None:
        before = len(df_work)
        topic_filter_set = set(topic_filter) if not isinstance(topic_filter, set) else topic_filter
        primary_col, secondary_col = topic_cols

        if topic_mode.upper() == 'ANY':
            mask = (
                df_work[primary_col].isin(topic_filter_set) | 
                df_work[secondary_col].isin(topic_filter_set)
            )
        elif topic_mode.upper() == 'PRIMARY':
            mask = df_work[primary_col].isin(topic_filter_set)
        elif topic_mode.upper() == 'SECONDARY':
            mask = df_work[secondary_col].isin(topic_filter_set)
        elif topic_mode.upper() == 'BOTH':
            mask = (
                df_work[primary_col].isin(topic_filter_set) & 
                df_work[secondary_col].isin(topic_filter_set)
            )
        else:
            raise ValueError(f"topic_mode must be 'ANY', 'PRIMARY', 'SECONDARY', or 'BOTH'")

        df_work = df_work[mask]
        print(f"Topic filter ({topic_mode}): kept {len(df_work)}/{before} papers")

    if df_work.empty:
        print("No papers remaining after filters!")
        return None, None, None

    print(f"Working with {len(df_work)} papers after all filters")

    if method_cols is None:
        method_cols = [f'Method_{i}' for i in range(1, 11)]

    if normalize_methods:
        print("Normalizing method names...")
        for col in method_cols:
            df_work[col] = df_work[col].apply(normalize_method_name)

    # Melt to long format
    df_long = df_work.melt(
        id_vars=[paper_id_col],
        value_vars=method_cols,
        var_name='method_rank',
        value_name='Method'
    ).dropna(subset=['Method'])

    # Filter by minimum occurrence
    method_counts = df_long['Method'].value_counts()
    frequent_methods = method_counts[method_counts >= min_papers].index.tolist()
    df_long = df_long[df_long['Method'].isin(frequent_methods)]

    print(f"Kept {len(frequent_methods)} methods appearing in ≥{min_papers} papers")

    # Create binary paper × method matrix
    paper_method = df_long.groupby([paper_id_col, 'Method']).size().unstack(fill_value=0)
    paper_method_binary = (paper_method > 0).astype(int)

    # Co-occurrence matrix
    cooc = paper_method_binary.T @ paper_method_binary
    method_totals = pd.Series(np.diag(cooc.values), index=cooc.index)

    cooc = cooc.astype(float)
    np.fill_diagonal(cooc.values, np.nan)

    return cooc, paper_method_binary, method_totals


def load_dashboard_data(csv_path, config_dir, topic_filter=TOPIC_INDICES):
    """
    Load and prepare all data for dashboard.

    Returns
    -------
    dict with keys:
        - cooc_matrix
        - paper_method_binary
        - method_totals
        - papers_df
        - method_categories
        - method_shortnames
        - method_variants
        - all_methods
        - all_categories
        - method_to_category_map
    """
    print(f"\n{'='*70}")
    print("🔄 Loading Dashboard Data")
    print(f"{'='*70}\n")

    # Load CSV
    print(f"📊 Loading CSV: {os.path.basename(csv_path)}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = try_read_csv(csv_path)
    print(f"   ✅ Loaded {len(df)} papers\n")

    # Load configuration files
    print(f"📂 Loading config from: {config_dir}")
    method_categories = load_json_config(
        os.path.join(config_dir, 'method_categories.json'), 
        "method categories"
    ) or {}

    method_shortnames = load_json_config(
        os.path.join(config_dir, 'method_shortnames.json'),
        "method shortnames"
    ) or {}

    method_variants = load_json_config(
        os.path.join(config_dir, 'method_variants.json'),
        "method variants"
    ) or {}

    print()

    # Build co-occurrence matrix
    print("🔨 Building co-occurrence matrix...")
    cooc_matrix, paper_method_binary, method_totals = build_cooccurrence_from_methods(
        df,
        min_papers=MIN_PAPERS_PER_METHOD,
        citation_filter=0,
        topic_filter=topic_filter,
    )

    if isinstance(method_totals, pd.Series):
        method_totals = method_totals.to_dict()

    # Prepare filtered papers dataframe
    print("\n📄 Preparing papers dataframe...")
    mask = (
        df['Primary_Topic_Index'].isin(topic_filter) | 
        df['Secondary_Topic_Index'].isin(topic_filter)
    )
    df_filtered = df[mask].copy()

    method_cols = [f'Method_{i}' for i in range(1, 11)]
    for col in method_cols:
        df_filtered[col] = df_filtered[col].apply(normalize_method_name)

    papers_df = prepare_papers_dataframe(df_filtered)
    print(f"   ✅ Prepared {len(papers_df)} papers")

    # Extract metadata
    all_methods = list(cooc_matrix.index)
    all_categories = sorted(set(method_categories.values()))

    method_to_category_map = {}
    for method in all_methods:
        cat = method_categories.get(method.lower())
        if cat:
            method_to_category_map[method] = cat

    print(f"\n{'='*70}")
    print("✅ Data loading complete!")
    print(f"   Methods: {len(all_methods)}")
    print(f"   Categories: {len(all_categories)}")
    print(f"   Papers: {len(papers_df)}")
    print(f"{'='*70}\n")

    return {
        'cooc_matrix': cooc_matrix,
        'paper_method_binary': paper_method_binary,
        'method_totals': method_totals,
        'papers_df': papers_df,
        'method_categories': method_categories,
        'method_shortnames': method_shortnames,
        'method_variants': method_variants,
        'all_methods': all_methods,
        'all_categories': all_categories,
        'method_to_category_map': method_to_category_map,
    }
