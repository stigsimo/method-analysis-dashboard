"""
Plotly visualization functions for network and trend plots
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def create_network_plot(
    cooc_matrix,
    method_totals,
    method_to_category_map,
    method_shortnames,
    all_categories,
    selected_methods,
    selected_categories,
    min_cooc=5,
    max_edges=5,
    highlighted_method=None,
    highlighted_edge=None
):
    """Create interactive circular network visualization."""

    # Filter methods
    if selected_methods and len(selected_methods) > 0:
        methods_to_plot = [
            m for m in selected_methods 
            if method_to_category_map.get(m) in selected_categories
        ]
    else:
        methods_to_plot = [
            m for m in cooc_matrix.index
            if method_to_category_map.get(m) in selected_categories
        ]

    if not methods_to_plot:
        return _create_empty_figure("No methods to display. Adjust filters.")

    n_methods = len(methods_to_plot)

    # Calculate circular positions
    method_positions = {
        method: 2 * np.pi * i / n_methods 
        for i, method in enumerate(methods_to_plot)
    }

    # Build edges
    edge_list = []
    for method1 in methods_to_plot:
        method_edges = []
        for method2 in methods_to_plot:
            if method1 != method2:
                cooc = cooc_matrix.loc[method1, method2]
                if cooc >= min_cooc:
                    method_edges.append({
                        'source': method1,
                        'target': method2,
                        'weight': cooc
                    })
        method_edges.sort(key=lambda x: x['weight'], reverse=True)
        edge_list.extend(method_edges[:max_edges])

    # Remove duplicates
    unique_edges = {}
    for edge in edge_list:
        pair = tuple(sorted([edge['source'], edge['target']]))
        if pair not in unique_edges or edge['weight'] > unique_edges[pair]['weight']:
            unique_edges[pair] = edge

    # Determine highlighted edges
    highlighted_edges = set()
    if highlighted_method:
        for edge in unique_edges.values():
            if edge['source'] == highlighted_method or edge['target'] == highlighted_method:
                highlighted_edges.add(tuple(sorted([edge['source'], edge['target']])))
    if highlighted_edge:
        highlighted_edges.add(tuple(sorted(highlighted_edge)))

    # Create traces
    edge_line_traces, edge_marker_traces = _create_edge_traces(
        unique_edges, method_positions, highlighted_edges
    )

    node_trace = _create_node_trace(
        methods_to_plot, method_positions, method_shortnames, method_totals,
        method_to_category_map, all_categories, highlighted_method, unique_edges
    )

    legend_traces = _create_legend_traces(
        methods_to_plot, method_to_category_map, selected_categories, all_categories
    )

    # Assemble figure
    fig = go.Figure(data=edge_line_traces + edge_marker_traces + [node_trace] + legend_traces)

    fig.update_layout(
        title=dict(
            text=f"Method Co-occurrence Network<br>"
                 f"<sub>{n_methods} methods, {len(unique_edges)} connections | "
                 f"Click node to highlight, click edge for papers, reset button to clear</sub>",
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(title='Categories', yanchor='top', y=1, xanchor='left', x=1.02),
        hovermode='closest',
        margin=dict(b=20, l=20, r=150, t=100),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        height=800,
        clickmode='event+select'
    )

    return fig


def create_trend_plot(trend_df, selected_methods, selected_categories):
    """Create interactive trend line plot."""

    filtered_df = trend_df[trend_df['category'].isin(selected_categories)].copy()

    if selected_methods and len(selected_methods) > 0:
        filtered_df = filtered_df[filtered_df['method'].isin(selected_methods)]

    if filtered_df.empty:
        return _create_empty_figure("No trend data. Adjust filters.", height=600)

    n_methods = filtered_df['method'].nunique()

    fig = px.line(
        filtered_df,
        x='year',
        y='points',
        color='method',
        markers=True,
        title=f'Method Adoption Trends ({n_methods} methods)',
        labels={'points': 'Weighted Score', 'year': 'Publication Year'}
    )

    fig.update_layout(
        hovermode='x unified',
        legend=dict(title='Method', yanchor='top', y=1, xanchor='left', x=1.02),
        height=600,
        xaxis=dict(dtick=1)
    )

    return fig


def _create_empty_figure(message, height=800):
    """Create empty figure with message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="red")
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=height
    )
    return fig


def _create_edge_traces(unique_edges, method_positions, highlighted_edges):
    """Create edge line and marker traces."""
    edge_line_traces = []
    edge_marker_traces = []

    if not unique_edges:
        return edge_line_traces, edge_marker_traces

    max_weight = max(e['weight'] for e in unique_edges.values())
    min_weight = min(e['weight'] for e in unique_edges.values())

    for pair, edge in unique_edges.items():
        theta1 = method_positions[edge['source']]
        theta2 = method_positions[edge['target']]

        x1, y1 = np.cos(theta1), np.sin(theta1)
        x2, y2 = np.cos(theta2), np.sin(theta2)
        x_mid, y_mid = (x1 + x2) / 2, (y1 + y2) / 2

        is_highlighted = pair in highlighted_edges

        # Normalize weight
        norm_weight = (edge['weight'] - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5

        # Line styling
        width = (3 + 5 * norm_weight) if is_highlighted else (0.5 + 3 * norm_weight)
        color = 'rgba(255, 69, 0, 0.8)' if is_highlighted else 'rgba(120,120,120,0.3)'

        edge_line_traces.append(go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode='lines',
            line=dict(width=width, color=color),
            hoverinfo='skip',
            showlegend=False,
        ))

        # Clickable markers
        marker_size = 25 if is_highlighted else 15
        marker_color = 'rgba(255, 100, 0, 0.2)' if is_highlighted else 'rgba(0,0,0,0)'

        edge_marker_traces.append(go.Scatter(
            x=[x_mid], y=[y_mid],
            mode='markers',
            marker=dict(
                size=marker_size,
                color=marker_color,
                line=dict(
                    width=1 if is_highlighted else 0,
                    color='rgba(255,69,0,0.5)' if is_highlighted else 'rgba(0,0,0,0)'
                )
            ),
            hovertext=f"<b>{edge['source']} ↔ {edge['target']}</b><br>"
                     f"Co-occurrence: {edge['weight']}<br>"
                     f"<i>Click to see papers</i>",
            hoverinfo='text',
            showlegend=False,
            customdata=[[edge['source'], edge['target']]],
        ))

    return edge_line_traces, edge_marker_traces


def _create_node_trace(methods_to_plot, method_positions, method_shortnames,
                      method_totals, method_to_category_map, all_categories,
                      highlighted_method, unique_edges):
    """Create node scatter trace."""
    node_x, node_y, node_text, node_hover = [], [], [], []
    node_colors, node_sizes, node_opacity, node_customdata = [], [], [], []

    color_palette = px.colors.qualitative.Set2
    color_map = {cat: color_palette[i % len(color_palette)] 
                 for i, cat in enumerate(all_categories)}

    for method, theta in method_positions.items():
        x, y = np.cos(theta), np.sin(theta)
        node_x.append(x)
        node_y.append(y)

        display_name = method_shortnames.get(method, method)
        if len(display_name) > 18:
            display_name = display_name[:15] + '...'
        node_text.append(display_name)

        cat = method_to_category_map.get(method, 'Unknown')
        total = method_totals.get(method, 0)

        # Check connectivity
        is_connected = False
        if highlighted_method:
            for edge in unique_edges.values():
                if (method == highlighted_method or
                    (edge['source'] == highlighted_method and edge['target'] == method) or
                    (edge['target'] == highlighted_method and edge['source'] == method)):
                    is_connected = True
                    break

        node_hover.append(
            f"<b>{method}</b><br>Category: {cat}<br>Occurrences: {total}<br>"
            f"<i>Click to highlight connections</i>"
        )

        # Styling
        if method == highlighted_method:
            node_colors.append('#FF4500')
            node_sizes.append((12 + np.log1p(total) * 3) * 1.5)
            node_opacity.append(1.0)
        elif is_connected:
            node_colors.append('#FFA500')
            node_sizes.append((12 + np.log1p(total) * 3) * 1.2)
            node_opacity.append(1.0)
        else:
            node_colors.append(color_map.get(cat, 'gray'))
            node_sizes.append(12 + np.log1p(total) * 3)
            node_opacity.append(0.4 if highlighted_method else 0.85)

        node_customdata.append(method)

    return go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        textfont=dict(size=8, color='black'),
        hovertext=node_hover,
        hoverinfo='text',
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color='white'),
            opacity=node_opacity
        ),
        customdata=node_customdata,
        showlegend=False,
        name='node'
    )


def _create_legend_traces(methods_to_plot, method_to_category_map, 
                         selected_categories, all_categories):
    """Create category legend traces."""
    color_palette = px.colors.qualitative.Set2
    color_map = {cat: color_palette[i % len(color_palette)] 
                 for i, cat in enumerate(all_categories)}

    legend_traces = []
    for cat in sorted(selected_categories):
        n_in_plot = sum(1 for m in methods_to_plot if method_to_category_map.get(m) == cat)
        if n_in_plot > 0:
            legend_traces.append(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color_map[cat]),
                name=f"{cat} ({n_in_plot})",
                showlegend=True
            ))

    return legend_traces
