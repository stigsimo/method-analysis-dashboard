"""
Dash layout components
"""

from dash import dcc, html


def create_layout(all_categories):
    """Create dashboard layout."""

    return html.Div([
        html.H1("Interactive Method Analysis Dashboard", 
                style={'textAlign': 'center', 'marginBottom': 20}),

        # Control Panel
        html.Div([
            # Search
            html.Div([
                html.Label("🔍 Search Methods:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Input(
                    id='method-search',
                    type='text',
                    placeholder='Type at least 2 characters...',
                    style={'width': '100%', 'padding': '5px', 'marginBottom': 10}
                ),
                html.Div(id='search-results', style={'maxHeight': '150px', 'overflowY': 'auto'}),
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': 15}),

            # Top N selection
            html.Div([
                html.Label("📊 Select Top N Methods:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Slider(
                    id='top-n-slider',
                    min=5, max=50, step=5, value=15,
                    marks={i: str(i) for i in range(5, 51, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Button('Apply Top N', id='apply-top-n', n_clicks=1,
                           style={'marginTop': 15, 'width': '100%', 'padding': '8px',
                                  'backgroundColor': '#4CAF50', 'color': 'white',
                                  'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
                html.Button('Clear Selection', id='clear-selection', n_clicks=0,
                           style={'marginTop': 5, 'width': '100%', 'padding': '8px',
                                  'backgroundColor': '#f44336', 'color': 'white',
                                  'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': 15}),

            # Category filter
            html.Div([
                html.Label("📂 Filter by Category:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Checklist(
                    id='category-checklist',
                    options=[{'label': f' {cat}', 'value': cat} for cat in all_categories],
                    value=all_categories,
                    style={'marginTop': 10},
                    labelStyle={'display': 'block', 'marginBottom': '5px'}
                ),
            ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'backgroundColor': '#f5f5f5', 'padding': 20, 'marginBottom': 15, 
                  'borderRadius': 8, 'border': '1px solid #ddd'}),

        # Network parameters
        html.Div([
            html.H3("Network Display Options", style={'marginBottom': 10}),
            html.Div([
                html.Label("Min Co-occurrence:", style={'fontWeight': 'bold'}),
                dcc.Slider(id='min-cooc-slider', min=1, max=20, step=1, value=5,
                          marks={i: str(i) for i in [1, 5, 10, 15, 20]},
                          tooltip={"placement": "bottom", "always_visible": True}),
            ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': 20}),

            html.Div([
                html.Label("Max Edges per Method:", style={'fontWeight': 'bold'}),
                dcc.Slider(id='max-edges-slider', min=1, max=20, step=1, value=5,
                          marks={i: str(i) for i in [1, 5, 10, 15, 20]},
                          tooltip={"placement": "bottom", "always_visible": True}),
            ], style={'width': '48%', 'display': 'inline-block'}),
        ], style={'backgroundColor': '#fafafa', 'padding': 20, 'marginBottom': 15,
                  'borderRadius': 8, 'border': '1px solid #ddd'}),

        # Selected methods display
        html.Div([
            html.Label("📌 Currently Selected:", style={'fontWeight': 'bold', 'marginBottom': 10}),
            html.Div(id='selected-methods-display'),
        ], style={'padding': 15, 'marginBottom': 20, 'backgroundColor': 'white',
                  'borderRadius': 8, 'border': '1px solid #ddd'}),

        # Stores for state
        dcc.Store(id='selected-methods-store', data=[]),
        dcc.Store(id='highlighted-method-store', data=None),
        dcc.Store(id='highlighted-edge-store', data=None),

        # Reset button
        html.Div([
            html.Button(
                '🔄 Reset Highlighting', 
                id='reset-highlight', 
                n_clicks=0,
                style={
                    'padding': '8px 15px',
                    'backgroundColor': '#607D8B',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                }
            ),
        ], style={'marginBottom': 10}),

        # Network plot
        dcc.Graph(id='network-plot'),

        # Paper details panel
        html.Div([
            html.H3(id='paper-panel-title', style={'marginBottom': 10}),
            html.Div(id='paper-details-content')
        ], id='paper-details-panel', style={
            'padding': 20,
            'marginTop': 20,
            'marginBottom': 20,
            'backgroundColor': 'white',
            'borderRadius': 8,
            'border': '2px solid #4CAF50',
            'display': 'none'
        }),

        # Trend plot
        html.Hr(style={'margin': '30px 0'}),
        dcc.Graph(id='trend-plot'),

    ], style={'padding': 25, 'fontFamily': 'Arial, sans-serif', 'maxWidth': '1800px', 'margin': '0 auto'})


def format_paper_info(papers_df_subset):
    """Format papers dataframe as HTML for display."""

    if papers_df_subset.empty:
        return html.Div(
            "No papers found with both methods",
            style={'color': '#999', 'fontStyle': 'italic', 'padding': '20px'}
        )

    paper_cards = []
    for idx, paper in papers_df_subset.iterrows():
        card = html.Div([
            html.Div([
                html.Strong(f"📄 {paper['title']}", style={'fontSize': '14px'}),
                html.Br(),
                html.Span(f"{paper['authors']} ({paper['year']})", 
                         style={'fontSize': '12px', 'color': '#666'}),
                html.Br(),
                html.Span(f"Citations: {paper['citationCount']} | Methods: {', '.join(paper['methods'])}", 
                         style={'fontSize': '11px', 'color': '#888'}),
                html.Br(),
                html.A(f"DOI: {paper['doi']}", 
                      href=f"https://doi.org/{paper['doi']}", 
                      target="_blank",
                      style={'fontSize': '10px', 'color': '#2196F3'})
            ], style={
                'padding': '12px',
                'margin': '8px 0',
                'backgroundColor': '#f9f9f9',
                'borderLeft': '4px solid #4CAF50',
                'borderRadius': '4px'
            })
        ])
        paper_cards.append(card)

    return html.Div(paper_cards)
