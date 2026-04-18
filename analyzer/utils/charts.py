"""
Plotly chart generation for resume analytics.
Returns JSON-serializable Plotly figure data for frontend rendering.
"""
import json


def generate_radar_chart_data(skills_dict):
    """
    Generate Plotly radar chart data from skills dictionary.
    Returns JSON string for frontend Plotly.js rendering.
    """
    categories = list(skills_dict.keys())
    values = list(skills_dict.values())

    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    figure_data = {
        "data": [{
            "type": "scatterpolar",
            "r": values,
            "theta": categories,
            "fill": "toself",
            "fillcolor": "rgba(79, 110, 247, 0.15)",
            "line": {
                "color": "#4F6EF7",
                "width": 2
            },
            "marker": {
                "color": "#00D4FF",
                "size": 8,
                "symbol": "circle"
            },
            "name": "Skills"
        }],
        "layout": {
            "polar": {
                "radialaxis": {
                    "visible": True,
                    "range": [0, 100],
                    "tickfont": {"color": "#8892B0", "size": 10},
                    "gridcolor": "rgba(79, 110, 247, 0.1)"
                },
                "angularaxis": {
                    "tickfont": {"color": "#E8EAF6", "size": 12},
                    "gridcolor": "rgba(79, 110, 247, 0.15)"
                },
                "bgcolor": "rgba(0,0,0,0)"
            },
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#E8EAF6"},
            "showlegend": False,
            "margin": {"t": 40, "b": 40, "l": 60, "r": 60}
        }
    }

    return json.dumps(figure_data)


def generate_gauge_data(score):
    """
    Generate Plotly gauge chart data for match score.
    Returns JSON string for frontend Plotly.js rendering.
    """
    # Determine color based on score
    if score >= 80:
        bar_color = "#00E676"
    elif score >= 60:
        bar_color = "#4F6EF7"
    elif score >= 40:
        bar_color = "#FFD600"
    else:
        bar_color = "#FF5252"

    figure_data = {
        "data": [{
            "type": "indicator",
            "mode": "gauge+number",
            "value": score,
            "number": {
                "suffix": "%",
                "font": {"size": 48, "color": "#E8EAF6", "family": "Space Grotesk"}
            },
            "gauge": {
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#8892B0",
                    "tickfont": {"color": "#8892B0"}
                },
                "bar": {"color": bar_color, "thickness": 0.75},
                "bgcolor": "rgba(13, 20, 38, 0.6)",
                "borderwidth": 1,
                "bordercolor": "rgba(79, 110, 247, 0.3)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(255, 82, 82, 0.1)"},
                    {"range": [40, 60], "color": "rgba(255, 214, 0, 0.1)"},
                    {"range": [60, 80], "color": "rgba(79, 110, 247, 0.1)"},
                    {"range": [80, 100], "color": "rgba(0, 230, 118, 0.1)"}
                ],
                "threshold": {
                    "line": {"color": "#00D4FF", "width": 3},
                    "thickness": 0.8,
                    "value": score
                }
            }
        }],
        "layout": {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#E8EAF6", "family": "Space Grotesk"},
            "margin": {"t": 30, "b": 10, "l": 30, "r": 30},
            "height": 250
        }
    }

    return json.dumps(figure_data)
