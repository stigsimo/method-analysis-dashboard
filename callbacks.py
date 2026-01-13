"""
Dash callback functions
"""

import json
import pandas as pd
import numpy as np
from dash import Input, Output, State, callback_context, ALL, html
from rapidfuzz import fuzz, process

from layout import format_paper_info
from plotting import create_network_plot, create_trend_plot


def register_callbacks(app, data):
    """Register all dashboard callbacks."""

    # Unpack data
    cooc_matrix = data['cooc_matrix']
    paper_method_binary = data['paper_method_binary']
    method_totals = data['method_totals']
    papers_df = data['papers_df']
    method_to_category_map = data['method_to_category_map']
    method_shortnames = data['method_shortnames']
    all_methods = data['all_methods']
    all_categories = data['all_categories']

    # Generate trend data (placeholder - replace with real data if available)
    years = list(range(2015, 2026))
    trend_data = []
    for method in all_methods:
        for year in years:
            trend_data.append({
                'year': year,
                'method': method,
                'points': np.random.uniform(0.1, 1.0) * (year - 2014) * np.random.uniform(0.5, 1.5),
                'category': data['method_categories'].get(method.lower(), 'Other')
            })
    trend_df = pd.DataFrame(trend_data)

    # Helper functions
    def fuzzy_search_methods(search_term, method_list, limit=10):
        """Fuzzy search with method variants."""
        if not search_term or len(search_term) < 2:
            return []
        results = process.extract(search_term, method_list, scorer=fuzz.WRatio, limit=limit)
        return [result[0] for result in results if result[1] > 50]

    def get_top_n_methods(n, categories):
        """Get top N methods by occurrences."""
        eligible = [m for m in all_methods if method_to_category_map.get(m) in categories]
        sorted_methods = sorted(eligible, key=lambda x: method_totals.get(x, 0), reverse=True)
        return sorted_methods[:n]

    def filter_by_categories(methods_list, categories):
        """Filter methods by categories."""
        if not methods_list:
            return []
        return [m for m in methods_list if method_to_category_map.get(m) in categories]

    def get_papers_for_methods(method1, method2, top_n=5):
        """Get papers using both methods."""
        print(f"\n📚 Searching: {method1} + {method2}")

        if method1 not in paper_method_binary.columns or method2 not in paper_method_binary.columns:
            return pd.DataFrame()

        has_both = (paper_method_binary[method1] == 1) & (paper_method_binary[method2] == 1)
        paper_ids = paper_method_binary[has_both].index.tolist()

        print(f"   Found {len(paper_ids)} papers")

        if not paper_ids:
            return pd.DataFrame()

        matching = papers_df[papers_df['paperId'].isin(paper_ids)].copy()
        if matching.empty:
            return pd.DataFrame()

        matching['score'] = matching['year'] * 100 + matching['citationCount'] / 10
        matching = matching.sort_values('score', ascending=False)

        return matching.head(top_n)

    # Callback 1: Search results
    @app.callback(
        Output('search-results', 'children'),
        Input('method-search', 'value')
    )
    def update_search_results(search_term):
        if not search_term or len(search_term) < 2:
            return html.Div("Type at least 2 characters...", 
                           style={'fontStyle': 'italic', 'color': '#999', 'fontSize': '12px'})

        matches = fuzzy_search_methods(search_term, all_methods, limit=10)

        if not matches:
            return html.Div("No matches found", style={'color': '#f44336', 'fontSize': '12px'})

        return html.Div([
            html.Button(method, id={'type': 'method-button', 'index': method}, n_clicks=0,
                       style={'margin': '3px', 'padding': '5px 10px', 'backgroundColor': '#e3f2fd',
                              'border': '1px solid #2196F3', 'borderRadius': '3px',
                              'cursor': 'pointer', 'fontSize': '11px'})
            for method in matches
        ])

    # Callback 2: Update selected methods
    @app.callback(
        Output('selected-methods-store', 'data'),
        [Input({'type': 'method-button', 'index': ALL}, 'n_clicks'),
         Input('apply-top-n', 'n_clicks'),
         Input('clear-selection', 'n_clicks')],
        [State('selected-methods-store', 'data'),
         State('top-n-slider', 'value'),
         State('category-checklist', 'value')]
    )
    def update_selected_methods(method_clicks, top_n_clicks, clear_clicks, 
                               current_selected, top_n, selected_cats):
        ctx = callback_context

        if not ctx.triggered:
            return get_top_n_methods(top_n, selected_cats)

        trigger_id = ctx.triggered[0]['prop_id']

        if 'clear-selection' in trigger_id:
            return []

        if 'apply-top-n' in trigger_id:
            return get_top_n_methods(top_n, selected_cats)

        if 'method-button' in trigger_id:
            button_id = json.loads(trigger_id.split('.')[0])
            clicked_method = button_id['index']
            current_selected = current_selected or []

            if clicked_method in current_selected:
                current_selected.remove(clicked_method)
            else:
                current_selected.append(clicked_method)

            return current_selected

        return current_selected or []

    # Callback 3: Display selected methods
    @app.callback(
        Output('selected-methods-display', 'children'),
        Input('selected-methods-store', 'data')
    )
    def display_selected_methods(selected_methods):
        if not selected_methods:
            return html.Div("No specific methods selected - showing all in selected categories",
                           style={'fontStyle': 'italic', 'color': '#666', 'fontSize': '13px'})

        return html.Div([
            html.Span(f"{method} ×",
                     style={'display': 'inline-block', 'margin': '3px', 'padding': '5px 12px',
                            'backgroundColor': '#4CAF50', 'color': 'white', 'borderRadius': '15px',
                            'fontSize': '11px', 'fontWeight': 'bold'})
            for method in selected_methods
        ] + [
            html.Div(f"Total: {len(selected_methods)} methods",
                    style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#666', 'fontSize': '12px'})
        ])

    # Callback 4: Handle clicks
    @app.callback(
        [Output('highlighted-method-store', 'data'),
         Output('highlighted-edge-store', 'data')],
        [Input('network-plot', 'clickData'),
         Input('reset-highlight', 'n_clicks')],
        [State('highlighted-method-store', 'data')]
    )
    def handle_network_clicks(clickData, reset_clicks, current_highlighted):
        ctx = callback_context

        if not ctx.triggered:
            return None, None

        trigger = ctx.triggered[0]['prop_id']

        if 'reset-highlight' in trigger and reset_clicks > 0:
            return None, None

        if 'clickData' in trigger and clickData:
            point = clickData['points'][0]
            if 'customdata' in point:
                if isinstance(point['customdata'], str):
                    method_name = point['customdata']
                    if current_highlighted == method_name:
                        return None, None
                    return method_name, None
                elif isinstance(point['customdata'], list):
                    return None, point['customdata']

        return current_highlighted, None

    # Callback 5: Update network and papers
    @app.callback(
        [Output('network-plot', 'figure'),
         Output('paper-details-panel', 'style'),
         Output('paper-panel-title', 'children'),
         Output('paper-details-content', 'children')],
        [Input('selected-methods-store', 'data'),
         Input('category-checklist', 'value'),
         Input('min-cooc-slider', 'value'),
         Input('max-edges-slider', 'value'),
         Input('highlighted-method-store', 'data'),
         Input('highlighted-edge-store', 'data')]
    )
    def update_network_and_papers(selected_methods, selected_categories, min_cooc, max_edges,
                                  highlighted_method, highlighted_edge):
        fig = create_network_plot(
            cooc_matrix, method_totals, method_to_category_map, method_shortnames,
            all_categories, selected_methods, selected_categories, min_cooc, max_edges,
            highlighted_method, highlighted_edge
        )

        if highlighted_edge and len(highlighted_edge) == 2:
            method1, method2 = highlighted_edge
            papers = get_papers_for_methods(method1, method2, top_n=5)

            panel_style = {
                'padding': 20, 'marginTop': 20, 'marginBottom': 20,
                'backgroundColor': 'white', 'borderRadius': 8,
                'border': '2px solid #4CAF50', 'display': 'block'
            }

            title = f"📚 Top 5 Papers: {method1} + {method2}"
            content = format_paper_info(papers)

            return fig, panel_style, title, content

        return fig, {'display': 'none'}, "", ""

    # Callback 6: Update trend plot
    @app.callback(
        Output('trend-plot', 'figure'),
        [Input('selected-methods-store', 'data'),
         Input('category-checklist', 'value')]
    )
    def update_trend_plot(selected_methods, selected_categories):
        return create_trend_plot(trend_df, selected_methods, selected_categories)
