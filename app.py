from dash import Dash, dcc, html, Input, Output, dash_table, State, callback_context
from dash_bootstrap_components import Tooltip
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import ast
import numpy as np
import plotly.graph_objects as go
import requests



dishes = pd.read_csv("data/all_dishes.csv")
places = pd.read_csv("data/all_places.csv")

REGION_COLORS = {
    "Hokkaido": {"background": "#C9EDE1", "text": "#2D5A47"}, # Hokkaido region

    "Aomori": {"background": "#D4E1F4", "text": "#2B5C73"}, # Tohoku region
    "Akita": {"background": "#D4E1F4", "text": "#2B5C73"},
    "Iwate": {"background": "#D4E1F4", "text": "#2B5C73"},
    "Yamagata": {"background": "#D4E1F4", "text": "#2B5C73"},
    "Miyagi": {"background": "#D4E1F4", "text": "#2B5C73"},
    "Fukushima": {"background": "#D4E1F4", "text": "#2B5C73"},

    "Ibaraki": {"background": "#E1F3D5", "text": "#345C3B"}, # Kanto region
    "Tochigi": {"background": "#E1F3D5", "text": "#345C3B"},
    "Gunma": {"background": "#E1F3D5", "text": "#345C3B"},
    "Saitama": {"background": "#E1F3D5", "text": "#345C3B"},
    "Chiba": {"background": "#E1F3D5", "text": "#345C3B"},
    "Tokyo": {"background": "#E1F3D5", "text": "#345C3B"},
    "Kanagawa": {"background": "#E1F3D5", "text": "#345C3B"},

    "Niigata": {"background": "#F5D6D6", "text": "#8B3A3A"}, # Chubu region
    "Toyama": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Ishikawa": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Fukui": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Yamanashi": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Nagano": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Gifu": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Shizuoka": {"background": "#F5D6D6", "text": "#8B3A3A"},
    "Aichi": {"background": "#F5D6D6", "text": "#8B3A3A"},
    
    "Mie": {"background": "#FFE6C8", "text": "#B85C00"}, # Kansai region
    "Shiga": {"background": "#FFE6C8", "text": "#B85C00"},
    "Kyoto": {"background": "#FFE6C8", "text": "#B85C00"},
    "Osaka": {"background": "#FFE6C8", "text": "#B85C00"},
    "Hyogo": {"background": "#FFE6C8", "text": "#B85C00"},
    "Nara": {"background": "#FFE6C8", "text": "#B85C00"},
    "Wakayama": {"background": "#FFE6C8", "text": "#B85C00"},

    "Tottori": {"background": "#E8D4F8", "text": "#6B2B7A"}, # Chugoku region
    "Shimane": {"background": "#E8D4F8", "text": "#6B2B7A"},
    "Okayama": {"background": "#E8D4F8", "text": "#6B2B7A"},
    "Hiroshima": {"background": "#E8D4F8", "text": "#6B2B7A"},
    "Yamaguchi": {"background": "#E8D4F8", "text": "#6B2B7A"},

    "Tokushima": {"background": "#F7E9B0", "text": "#7A6A00"}, # Shikoku region
    "Kagawa": {"background": "#F7E9B0", "text": "#7A6A00"},
    "Ehime": {"background": "#F7E9B0", "text": "#7A6A00"},
    "Kochi": {"background": "#F7E9B0", "text": "#7A6A00"},

    "Fukuoka": {"background": "#F9D6E5", "text": "#A63A5B"}, # Kyushu and Okinawa region
    "Saga": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Nagasaki": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Kumamoto": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Oita": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Miyazaki": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Kagoshima": {"background": "#F9D6E5", "text": "#A63A5B"},
    "Okinawa": {"background": "#F9D6E5", "text": "#A63A5B"},

    "default": {"background": "#CCCCCC", "text": "#2E2E2E"}
}

app = Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css","https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap"
    ],
    suppress_callback_exceptions=True
)
server = app.server

def haversine(lat1, lon1, lat2, lon2):
    if any(pd.isna([lat1, lon1, lat2, lon2])):
        return np.nan

    R = 6371

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = R * c
    return km

def get_season_icon(season):
    m = {
        "all season": "seasonal.svg",
        "spring":       "calendar.svg",
        "summer":       "summer.svg",
        "fall":         "autumn.svg",
        "autumn":       "autumn.svg",
        "winter":       "winter.svg"
    }
    return m.get(str(season).lower(), "seasonal.svg")

def generate_radar_chart_elements(dish_name, standardize_scale=False, is_dark_mode=False):
    
    if is_dark_mode:
        grid_color = "rgba(255, 255, 255, 0.2)"
        tick_color = "#E0E0E0"
        subtle_tick_color = "rgba(255,255,255,0.6)"
    else:
        grid_color = "rgba(0, 0, 0, 0.3)"
        tick_color = "black"
        subtle_tick_color = "rgba(0,0,0,0.8)"
    
    plot_paper_bg = "rgba(0,0,0,0)"
    
    if dish_name is None:
        row = pd.DataFrame()
    else:
        row = dishes[dishes["dish_name"] == dish_name]
        
    nutrients = ["Calories      ", "Protein", "Carbohydrates", "Fat", "Sodium"]
    DAILY_TARGETS = {"calories": 2000, "protein": 50, "carbohydrates": 275, "fat": 70, "sodium": 2300}

    if not row.empty:
        values = [
            round(row.iloc[0].get("calories", 0)       / DAILY_TARGETS["calories"]    * 100, 1),
            round(row.iloc[0].get("protein", 0)       / DAILY_TARGETS["protein"]     * 100, 1),
            round(row.iloc[0].get("carbohydrates", 0) / DAILY_TARGETS["carbohydrates"] * 100, 1),
            round(row.iloc[0].get("fat", 0)           / DAILY_TARGETS["fat"]         * 100, 1),
            round(row.iloc[0].get("sodium", 0)        / DAILY_TARGETS["sodium"]      * 100, 1)
        ]
    else:
        values = [0, 0, 0, 0, 0]

    max_val = max(values) if values else 0
    capped_annotations = []
    
    if standardize_scale:
        max_val = 999

    MICRO_CHART_THRESHOLD = 30
    SMALL_CHART_THRESHOLD = 45
    
    if max_val <= MICRO_CHART_THRESHOLD:
        dynamic_range_max = 32
        dynamic_spoke_length = 32
        dynamic_grid_levels = [5, 10, 15, 20, 25, 30]
        dynamic_tick_vals = [0, 5, 10, 15, 20, 25, 30]
        dynamic_fill_color = "rgba(255, 106, 0, 0.35)" if is_dark_mode else "rgba(255, 106, 0, 0.25)"
        dynamic_line_color = "rgba(255, 106, 0, 1)"
        dynamic_subtitle_text = "Micro-Zoomed Version (0-30%)"
        dynamic_subtitle_color = "#FF8A3D" if is_dark_mode else "#FF6A00"
        dynamic_subtitle_weight = "700"
        is_normal_scale = False
    elif max_val <= SMALL_CHART_THRESHOLD:
        dynamic_range_max = 52
        dynamic_spoke_length = 52
        dynamic_grid_levels = [10, 20, 30, 40, 50]
        dynamic_tick_vals = [0, 10, 20, 30, 40, 50]
        dynamic_fill_color = "rgba(14, 159, 110, 0.35)" if is_dark_mode else "rgba(14, 159, 110, 0.25)"
        dynamic_line_color = "rgba(14, 159, 110, 1)"
        dynamic_subtitle_text = "Zoomed Version (0-50%)"
        dynamic_subtitle_color = "#10C792" if is_dark_mode else "#0E9F6E"
        dynamic_subtitle_weight = "700"
        is_normal_scale = False
    else:
        dynamic_range_max = 105
        dynamic_spoke_length = 105
        dynamic_grid_levels = [20, 40, 60, 80, 100]
        dynamic_tick_vals = [0, 20, 40, 60, 80, 100]
        dynamic_fill_color = "rgba(0, 123, 255, 0.35)" if is_dark_mode else "rgba(0, 123, 255, 0.25)"
        dynamic_line_color = "rgba(0, 123, 255, 1)"
        dynamic_subtitle_text = "Normal Version (0-100%)"
        dynamic_subtitle_color = "#3D9FFF" if is_dark_mode else "#007BFF"
        dynamic_subtitle_weight = "700"
        is_normal_scale = True
        for i in range(len(values)):
            if values[i] > 100:
                capped_annotations.append((["Calories", "Protein", "Carbohydrates", "Fat", "Sodium"][i], values[i]))
        
    
    dynamic_tick_text = [f"{t}%" for t in dynamic_tick_vals]
            
    abs_vals = [
        row.iloc[0].get("calories", 0) if not row.empty else 0,
        row.iloc[0].get("protein", 0) if not row.empty else 0,
        row.iloc[0].get("carbohydrates", 0) if not row.empty else 0,
        row.iloc[0].get("fat", 0) if not row.empty else 0,
        row.iloc[0].get("sodium", 0) if not row.empty else 0,
    ]
    units = ["kcal", "g", "g", "g", "mg"]
    hover_texts = [
        f"{['Calories', 'Protein', 'Carbohydrates', 'Fat', 'Sodium'][i]}: {abs_vals[i]} {units[i]}<br>({values[i]} %)"
        for i in range(len(nutrients))
    ]

    r_values = values
    if max_val > SMALL_CHART_THRESHOLD:
        r_values = [min(v, 100) for v in values]

    fig = go.Figure()
    grid_theta = nutrients + [nutrients[0]]

    for level in dynamic_grid_levels:
        fig.add_trace(go.Scatterpolar(
            r=[level] * 6, theta=grid_theta, mode="lines",
            line=dict(color=grid_color, width=0.8, dash="dash"),
            hoverinfo="none", showlegend=False
        ))

    for nutrient_label in nutrients:
        fig.add_trace(go.Scatterpolar(
            r=[0, dynamic_spoke_length], theta=[nutrient_label, nutrient_label],
            mode="lines", line=dict(color=grid_color, width=0.8, dash="dash"),
            hoverinfo="none", showlegend=False
        ))
        
    fig.add_trace(go.Scatterpolar(
        r=r_values + [r_values[0]], theta=nutrients + [nutrients[0]],
        fill="toself", fillcolor=dynamic_fill_color, mode="none",
        hoverinfo="none",
        showlegend=False
    ))

    fig.add_trace(go.Scatterpolar(
        r=r_values + [r_values[0]], theta=nutrients + [nutrients[0]],
        fill="none", mode="lines+markers",
        line_color=dynamic_line_color, line_width=1.5,
        marker=dict(size=5, color=dynamic_line_color),
        hovertext=hover_texts + [hover_texts[0]],
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        showlegend=False, dragmode=False,
        plot_bgcolor=plot_paper_bg,
        paper_bgcolor=plot_paper_bg,
        polar=dict(
            angularaxis=dict(
                rotation=90, direction="clockwise",
                tickfont=dict(size=10, color=tick_color),
                gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"
            ),
            radialaxis=dict(
                visible=True, range=[0, dynamic_range_max],
                tickvals=dynamic_tick_vals, ticktext=dynamic_tick_text,
                tickfont=dict(size=8, color=subtle_tick_color),
                angle=90,tickangle=90, gridcolor="rgba(0,0,0,0)",
                showline=False, ticks=""
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=30, r=30, t=15, b=5),
        height=230
    )

    if capped_annotations:
        badge_elements = [
            dbc.Badge(
                f"{label}: {value}%", color="danger", className="me-1",
                style={"fontSize": "12px", "padding": "5px 8px", "fontWeight": 600}
            ) for label, value in capped_annotations
        ]
        
        annotation_box_children = [
            html.I(className="fa fa-warning", style={
                "marginRight": "10px", "color": "#dc3545", "fontSize": "16px",
                "lineHeight": "1.5"
            }),
            html.Div(
                [
                    html.Span(
                        "Values exceed 100% :",
                        style={
                            "fontWeight": "600", "fontSize": "13px",
                            "marginRight": "10px", "flexShrink": 0,
                            "color": "#E0E0E0" if is_dark_mode else "black"
                        }
                    ),
                ] + badge_elements,
                style={
                    "display": "flex", "flexWrap": "nowrap", "overflowX": "auto",
                    "gap": "5px", "alignItems": "center", "paddingBottom": "5px",
                    "width": "100%"
                }
            )
        ]
        
        if is_dark_mode:
             annotation_box_style = {
                "backgroundColor": "#3d1f1f", "border": "1px solid #5a2d2d",
                "borderRadius": "8px", "padding": "8px 12px",
                "marginTop": "8px", "display": "flex",
                "alignItems": "flex-start",
             }
        else:
            annotation_box_style = {
                "backgroundColor": "#fdf3f4", "border": "1px solid #f5c6cb",
                "borderRadius": "8px", "padding": "8px 12px",
                "marginTop": "8px", "display": "flex",
                "alignItems": "flex-start",
            }
    else:
        annotation_box_children = []
        annotation_box_style = {"display": "none"}

    subtitle_children = [
        html.Span("Nutritional Values ", style={
            "fontWeight": "700", "fontSize": "16px",
            "color": tick_color, "marginRight": "6px"
        }),
        html.Span(dynamic_subtitle_text, style={
            "fontWeight": dynamic_subtitle_weight,
            "fontSize": "13px",
            "color": dynamic_subtitle_color,
            "transition": "color 0.3s ease, font-weight 0.3s ease"
        })
    ]
    
    return fig, subtitle_children, annotation_box_children, annotation_box_style, is_normal_scale


def create_right_panel(main_ingredients="", history="", dish_name=None, image_url=None, user_location=None, is_dark_mode=False):

    if is_dark_mode:
        card_style = {
            "border": "1px solid #3a3a3a",
            "box-shadow": "0 2px 6px rgba(0, 0, 0, 0.3)",
            "border-radius": "10px",
            "padding": "20px",
            "box-sizing": "border-box",
            "display": "flex",
            "flexDirection": "column",
            "backgroundColor": "#2b2b2b"
        }
        text_color = "#E0E0E0"
        history_text_color = "#E0E0E0"
        pill_bg = "#3a3a3a"
        pill_shadow = "0 2px 8px rgba(0,0,0,0.5)"
        placeholder_color = "#999999"
        table_bg = "#2b2b2b"
        table_color = "#E0E0E0"
        table_header_bg = "#1a1a1a"
        table_header_color = "#E0E0E0"
        table_border = "1px solid #3a3a3a"
        checkbox_bg = "rgba(43,43,43,0.9)"
        italic_color = "#888"
        main_ingr_bg = "#2b2b2b"
        main_ingr_border = "1px solid #3a3a3a"
        main_ingr_shadow = "0 2px 6px rgba(0, 0, 0, 0.3)"
        main_ingr_span_color = "#B0B0B0"
        rating_colors = ['#4CAF50', '#FFA726', '#EF5350']
    else:
        card_style = {
            "border": "none",
            "box-shadow": "0 2px 6px rgba(0, 0, 0, 0.05)",
            "border-radius": "10px",
            "padding": "20px",
            "box-sizing": "border-box",
            "display": "flex",
            "flexDirection": "column",
            "backgroundColor": "white"
        }
        text_color = "black"
        history_text_color = "black"
        pill_bg = "#FFFFFF"
        pill_shadow = "0 2px 8px rgba(0,0,0,0.32)"
        placeholder_color = "#6c757d"
        table_bg = "white"
        table_color = "black"
        table_header_bg = "white"
        table_header_color = "black"
        table_border = "1px solid #dee2e6"
        checkbox_bg = "rgba(255,255,255,0.7)"
        italic_color = "#555"
        main_ingr_bg = "white"
        main_ingr_border = "none"
        main_ingr_shadow = "0 2px 6px rgba(0, 0, 0, 0.1)"
        main_ingr_span_color = "black"
        rating_colors = ['green', 'orange', 'red']

    
    if dish_name is None:
        placeholder_div = html.Div(
            html.P(
                "Please select a dish on the map",
                style={
                    "fontSize": "20px",
                    "fontWeight": "500",
                    "color": placeholder_color
                }
            ),
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "height": "100%",
                "textAlign": "center",
                "flex": 1
            }
        )
        
        citation_markdown = dcc.Markdown(
            'Created based on "Our Regional Cuisines" (Ministry of Agriculture, Forestry and Fisheries) ([https://www.maff.go.jp/e/policies/market/k_ryouri/index.html](https://www.maff.go.jp/e/policies/market/k_ryouri/index.html))\n'
            'Licensed under PDL 1.0 ([https://www.digital.go.jp/en/resources/open_data/public_data_license_v1.0](https://www.digital.go.jp/en/resources/open_data/public_data_license_v1.0))',
            style={
                "fontSize": "11px",
                "color": italic_color,
                "whiteSpace": "pre-line",
                "lineHeight": "1.5",
                "textAlign": "center",
                "marginTop": "auto",
                "flexShrink": 0,
                "paddingTop": "10px"
            },
            link_target="_blank"
        )

        return html.Div([
            placeholder_div,
            citation_markdown
        ], style={"display": "flex", "flexDirection": "column", "height": "100%"})

    fig, subtitle_children, annotation_box_children, annotation_box_style, is_normal_scale = \
        generate_radar_chart_elements(dish_name, standardize_scale=False, is_dark_mode=is_dark_mode)
    row = dishes[dishes["dish_name"] == dish_name]
        
    left_box = html.Div(
        [
            html.Div([
                html.Img(
                    src=image_url,
                    style={"width": "100%", "marginBottom": "10px", "border-radius": "5px"}
                ) if image_url else None,
                html.Div(history, style={
                    "overflowY": "auto", "maxHeight": "250px", "minHeight": "50px",
                    "color": history_text_color
                })
            ], style={"display": "flex", "flexDirection": "column"} )
        ],
        style={**card_style, "height": "100%"}
    )

    PILL_BASE = {
        "borderRadius": "32px", "padding": "8px 14px", "marginRight": "8px",
        "marginBottom": "8px", "display": "inline-flex", "alignItems": "center",
        "gap": "6px", "fontSize": "15px", "fontWeight": "600",
        "boxShadow": pill_shadow
    }
    
    TYPE_ICON_PATH = "assets/icons/"
    type_icon_map = {
        "noodle": "Noodle.svg", "soup": "Soup.svg", "meat": "Meat.svg",
        "fish": "Fish.svg", "rice": "Rice.svg", "pickles": "Pickles.svg",
        "vegetable": "Vegetable.svg", "sweet": "Sweet.svg", "other": "cutlery.svg"
    }
    area_name = row.iloc[0]['area_name'] if not row.empty else ""
    area_icon_file = "placeholder.svg"
    
    area_icon = html.Img(
        src=f"{TYPE_ICON_PATH}{area_icon_file}",
        style={"height": "22px", "width": "22px", "marginRight": "6px"}
    )
    
    area_pill = html.Span(
        [area_icon, html.Span(area_name, style={"color": text_color})],
        style={**PILL_BASE, "backgroundColor": pill_bg, "color": text_color}
    )
    season_name = row.iloc[0]['seasonality'] if not row.empty else "all season"
    season_icon_file = get_season_icon(season_name)
    
    season_icon = html.Img(
        src=f"{TYPE_ICON_PATH}{season_icon_file}",
        style={"height": "22px", "width": "22px", "marginRight": "6px"}
    )
    
    season_pill = html.Span(
        [season_icon, html.Span(season_name.title(), style={"color": text_color})],
        style={**PILL_BASE, "backgroundColor": pill_bg, "color": text_color}
    )
    dish_type = row.iloc[0]['type'].lower() if not row.empty else ""
    type_icon_file = None
    for key, svg_file in type_icon_map.items():
        if key in dish_type:
            type_icon_file = svg_file
            break
    if type_icon_file:
        type_icon = html.Img(src=f"{TYPE_ICON_PATH}{type_icon_file}", style={"height": "22px", "width": "22px", "marginRight": "6px"})
    else:
        type_icon = html.I(className="fa fa-cutlery", style={"fontSize": "16px", "marginRight": "6px"})
    type_pill = html.Span([type_icon, html.Span(row.iloc[0]['type'].title() if not row.empty else "", style={"color": text_color})],
                                     style={**PILL_BASE, "backgroundColor": pill_bg, "color": text_color})
    
    ICON_PATH = "assets/icons/"
    diet_map = {
        "vegan": "Vegan.svg", "vegetarian": "Vegetarian.svg", "no_gluten": "No_gluten.svg",
        "no_seafood": "No_seafood.svg", "no_pork": "No_pork.svg", "no_dairy": "No_dairy.svg", "no_nuts": "No_nuts.svg"
    }

    style_icon_active = {
        "height": "28px", "width": "28px", "marginRight": "6px",
        "filter": "drop-shadow(0 1px 2px rgba(255,255,255,0.2))" if is_dark_mode else "drop-shadow(0 1px 2px rgba(0,0,0,0.15))",
        "opacity": 1,
        "transition": "opacity 0.3s, filter 0.3s"
    }
    style_icon_inactive = {
        "height": "28px", "width": "28px", "marginRight": "6px",
        "filter": "grayscale(100%) brightness(0.5)" if is_dark_mode else "grayscale(100%)",
        "opacity": 0.3,
        "transition": "opacity 0.3s, filter 0.3s"
    }
    
    tooltip_text_map = {
        "vegan": ("Vegan", "Not Vegan"),
        "vegetarian": ("Vegetarian", "Not Vegetarian"),
        "no_gluten": ("No Gluten", "Contains Gluten"),
        "no_seafood": ("No Seafood", "Contains Seafood"),
        "no_pork": ("No Pork", "Contains Pork"),
        "no_dairy": ("No Dairy", "Contains Dairy"),
        "no_nuts": ("No Nuts", "Contains Nuts")
    }

    diet_icons = []
    
    for col, icon_file in diet_map.items():
        icon_id = f"icon-{col}-{dish_name}"
        is_active = False
        if not row.empty:
            is_active = col in row.columns and row.iloc[0].get(col) == True
        current_style = style_icon_active if is_active else style_icon_inactive
        label_text = col.replace("_", " ").title()
        tooltip_texts = tooltip_text_map.get(col, (label_text, f"Not {label_text}"))
        tooltip_text = tooltip_texts[0] if is_active else tooltip_texts[1]
        
        diet_icons.append(html.Span([
            html.Img(id=icon_id, src=f"{ICON_PATH}{icon_file}", style=current_style),
            Tooltip(tooltip_text, target=icon_id, placement="top")
        ], style={"display": "inline-flex", "alignItems": "center"}))
    
    diet_pill_content = html.Span([html.Strong("Diet", style={"marginRight": "6px", "color": text_color}), html.Div(diet_icons, style={"display": "inline-flex", "gap": "8px"})], style={"display": "inline-flex", "alignItems": "center"})
    diet_pill_style = PILL_BASE.copy()
    diet_pill_style["display"] = "flex"
    diet_pill_style["flex"] = 1
    diet_pill_style["justifyContent"] = "center"
    
    diet_pill = html.Span(diet_pill_content, style={**diet_pill_style, "backgroundColor": pill_bg, "color": text_color})
    
    main_ingr_box = html.Div([
        html.Strong("Main ingredients: ", style={"marginRight": "6px", "color": text_color}),
        html.Span(main_ingredients, style={"fontSize": "14px", "color": main_ingr_span_color})
    ],
        style={
            "border": main_ingr_border, "box-shadow": main_ingr_shadow, "borderRadius": "14px",
            "padding": "8px 12px", "marginTop": "4px", "backgroundColor": main_ingr_bg,
            "display": "inline-block", "maxWidth": "100%"
        })
    
    pill_grid = html.Div(
        [
            html.Div([area_pill], style={"display": "flex", "flexWrap": "wrap", "gap": "10px"}),
            html.Div([season_pill, type_pill], style={"display": "flex", "flexWrap": "wrap", "gap": "10px"}),
            html.Div([diet_pill], style={"display": "flex"})
        ],
        style={"display": "flex", "flexDirection": "column", "gap": "8px", "alignItems": "center"}
    )
    right_box = html.Div(
        [
            pill_grid,
            main_ingr_box,
            html.Div(
                id="chart-subtitle-wrapper",
                children=subtitle_children,
                style={"marginTop": "15px", "display": "flex", "alignItems": "baseline", "flexWrap": "wrap"}
            ),
            html.Div(
                id="chart-annotation-box",
                children=annotation_box_children,
                style=annotation_box_style
            ),
            html.Div(
                [
                    dbc.Checkbox(
                        id="standardize-scale-checkbox",
                        label="Standardize Scale",
                        value=False,
                        style={
                            "position": "absolute", "top": "10px", "right": "10px", "zIndex": 10,
                            "fontWeight": "500", "fontSize": "13px",
                            "backgroundColor": checkbox_bg,
                            "color": text_color,
                            "padding": "2px 5px", "borderRadius": "5px",
                            "display": "none" if is_normal_scale else "inline-block"
                        }
                    ),
                    dcc.Graph(
                        id="radar-chart",
                        figure=fig,
                        config={"displayModeBar": False},
                        style={"height": "230px", "width": "100%", "overflow": "hidden", "marginTop": "0px"}
                    ),
                ],
                style={"position": "relative", "flex": "1", "minHeight": "230px", "marginTop": "15px"}
            ),
            html.P(
                "*in % of daily recommendation",
                style={
                    "fontSize": "11px", "color": italic_color, "textAlign": "left",
                    "fontStyle": "italic", "paddingLeft": "5px",
                    "marginTop": "-10px"
                }
            )
        ],
        style={**card_style, "gap": "8px", "padding": "15px", "height": "100%"}
    )

    message_box_style = {
        "border": card_style["border"], "box-shadow": card_style["box-shadow"],
        "border-radius": "10px", "padding": "20px", "display": "flex",
        "alignItems": "center", "justifyContent": "center",
        "textAlign": "center", "backgroundColor": card_style["backgroundColor"],
        "flexDirection": "column", "minHeight": "150px"
    }
    message_box = html.Div(
        [
            html.I(className="fa fa-info-circle", style={"fontSize": "24px", "color": italic_color, "marginBottom": "15px"}),
            html.P([
                "Sorry, no restaurants are recommended at the moment.",
                html.Br(),
                "We’ll be updating soon, stay tuned!"
            ], style={"margin": "auto", "fontSize": "18px", "fontWeight": "bold", "color": text_color})
        ],
        style=message_box_style
    )
    
    bottom_box = message_box
    
    if not row.empty and "places" in row.columns:
        places_str = row.iloc[0]["places"]
        try:
            place_ids = ast.literal_eval(places_str) if places_str else []
        except Exception:
            place_ids = []

        if place_ids:
            place_rows = places[places["id"].isin(place_ids)].copy()
            place_rows["rating"] = place_rows["rating"].apply(lambda x: x if pd.notna(x) else "?")
            
            user_lat = user_location.get('lat') if user_location else None
            user_lon = user_location.get('lon') if user_location else None
            if user_lat is not None and user_lon is not None:
                place_rows['distance'] = place_rows.apply(
                    lambda row: haversine(user_lat, user_lon, row['latitude'], row['longitude']),
                    axis=1
                )
                place_rows['distance'] = place_rows['distance'].apply(lambda x: f"{x:.1f} km" if pd.notna(x) else "?")
            else:
                place_rows["distance"] = "?"
            
            table_df = place_rows[["name", "distance", "rating", "price_level", "googleMapsUri"]].copy()

            table_df.columns = ["Place Name", "Distance", "Rating", "Price", "googleMapsUri"]
            
            price_mapping = {
                'PRICE_LEVEL_INEXPENSIVE': '¥',
                'PRICE_LEVEL_MODERATE': '¥¥',
                'PRICE_LEVEL_EXPENSIVE': '¥¥¥'
            }
            table_df["Price"] = table_df["Price"].map(price_mapping).fillna("–")
            table_df["Link"] = table_df["googleMapsUri"].apply(
                lambda x: f'<div style="text-align: center;"><a href="{x}" target="_blank"><img src="{TYPE_ICON_PATH}location.svg" alt="Map" style="height: 24px; vertical-align: middle;"></a></div>' if pd.notna(x) else ""
            )
            final_columns = ["Place Name", "Distance", "Rating", "Price", "Link"]
            table_df = table_df[final_columns]
            
            rating_style_rules = [
                {'if': {'column_id': 'Rating', 'filter_query': '{Rating} >= 4 && {Rating} is num'}, 'color': rating_colors[0], 'fontWeight': 'bold'},
                {'if': {'column_id': 'Rating', 'filter_query': '{Rating} >= 3 && {Rating} < 4 && {Rating} is num'}, 'color': rating_colors[1], 'fontWeight': 'bold'},
                {'if': {'column_id': 'Rating', 'filter_query': '{Rating} < 3 && {Rating} is num'}, 'color': rating_colors[2], 'fontWeight': 'bold'},
            ]
            
            alignment_rules = [
                {'if': {'column_id': ['Rating', 'Price']}, 'textAlign': 'center' },
                {'if': {'column_id': ['Place Name', 'Distance']}, 'textAlign': 'center' },
                {'if': {'column_id': 'Link'},
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                }
            ]
            columns_config = []
            for col_name in final_columns:
                if col_name == "Link":
                    columns_config.append({"name": "Map", "id": col_name, "presentation": "markdown"})
                elif col_name == "Distance":
                    columns_config.append({"name": col_name, "id": col_name, "presentation": "markdown"})
                else:
                    columns_config.append({"name": col_name, "id": col_name})
            
            tooltip_data = []
            for _, row in table_df.iterrows():
                row_tooltip = {}
                if row["Distance"] == "?":
                    row_tooltip["Distance"] = "Please enable location to see distance"
                tooltip_data.append(row_tooltip)


            def format_distance_icon(dist_value):
                if dist_value == "?":

                    return f'<div style="text-align: center;"><i class="fa fa-question-circle" style="font-size: 20px; color: #888; vertical-align: middle;"></i></div>'
                return f'<div style="text-align: center;">{dist_value}</div>'
            

            table_df["Distance"] = table_df["Distance"].apply(format_distance_icon)

            
            
            
            bottom_box = dash_table.DataTable(
                columns=columns_config,
                data=table_df.to_dict("records"),
                style_table={
                    "overflowY": "auto",
                    "maxHeight": "210px",
                    "border-radius": "10px",
                    "box-shadow": main_ingr_shadow,
                    "background-color": table_bg,
                },
                style_cell={
                    "padding": "5px", "font-family": "Helvetica, Arial, sans-serif",
                    "font-size": "16px", "color": table_color,
                    "backgroundColor": table_bg,
                    "border": table_border
                },
                style_header={
                    "fontWeight": "bold", "font-family": "Helvetica, Arial, sans-serif",
                    "font-size": "18px", "color": table_header_color,
                    "backgroundColor": table_header_bg,
                    "border": table_border
                },
                style_data={
                    "font-family": "Helvetica, Arial, sans-serif", "font-size": "16px",
                    "backgroundColor": table_bg,
                    "color": table_color
                },
                markdown_options={"link_target": "_blank", "html": True},
                sort_action="native",
                tooltip_data=tooltip_data,
                style_data_conditional=rating_style_rules,
                style_cell_conditional=alignment_rules,
                style_header_conditional=[
                    {'if': {'column_id': ['Rating', 'Price', 'Link']}, 'textAlign': 'center'},
                    {'if': {'column_id': ['Place Name', 'Distance']}, 'textAlign': 'center'}
                ]
            )

    top_row_style = {"paddingBottom": "20px"}
    bottom_row_style = {"flex": "0 1 auto", "display": "flex", "flexDirection": "column"}

    top_row = dbc.Row(
        [
            dbc.Col(left_box, width=6),
            dbc.Col(right_box, width=6),
        ],
        style=top_row_style,
        className="g-4"
    )

    bottom_row = dbc.Row(
        dbc.Col(bottom_box, style={"height": "100%"}),
        style=bottom_row_style
    )
    
    return html.Div(
        [
            top_row,
            bottom_row
        ],
        style={"display": "flex", "flexDirection": "column", "flex": 1, "minHeight": 0}
    )

prefecture_options = [{"label": p, "value": p} for p in pd.unique(dishes["prefecture"].dropna())]
season_order = ["all season", "spring", "summer", "fall", "winter"]
season_options = [{"label": s.title(), "value": s} for s in season_order if s in dishes["seasonality"].dropna().unique()]
type_options = [{"label": t.title(), "value": t} for t in sorted(pd.unique(dishes["type"].dropna()))]
dietary_columns = ["vegan","vegetarian","no_gluten","no_seafood","no_pork","no_dairy","no_nuts"]
dietary_labels = {
    "vegan": "Vegan", "vegetarian": "Vegetarian", "no_gluten": "No Gluten",
    "no_seafood": "No Seafood", "no_pork": "No Pork", "no_dairy": "No Dairy", "no_nuts": "No Nuts"
}
dietary_options = [{"label": dietary_labels[col], "value": col} for col in dietary_columns]
dish_search_options = [{"label": name, "value": name} for name in dishes["dish_name"]]

dish_search_dropdown = dcc.Dropdown(
    id="dish-search",
    options=dish_search_options,
    placeholder="Search",
    style={"width": "100%"},
    className="search-dropdown-style",
    optionHeight=120
)

filter_toggle_style = {
    "width": "100%", "display": "flex", "justifyContent": "space-between", "alignItems": "center",
    "fontSize": "14px", "fontWeight": "500", "padding": "0 12px", "height": "38px",
    "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"
}
app.layout = dbc.Container([
    
    dcc.Store(id="dark-mode", storage_type="session", data=False),
    
    dcc.Store(id="clicked-dish", storage_type="session"),
    dcc.Store(id="user-location", storage_type="session"),

    html.Div(
        [
            html.H1("Japanese Regional Cuisine", id="main-title", style={"margin": "0"}),
            html.Div(
                [
                    html.A(
                        html.I(className="fa fa-moon-o", id="theme-icon"),
                        id="theme-toggle-btn",
                        n_clicks=0,
                        style={
                            "textDecoration": "none", "color": "#A0A0A0",
                            "fontSize": "26px", "cursor": "pointer"
                        }
                    ),
                    html.A(
                        html.I(className="fa fa-share-alt"),
                        id="share-friend-icon",
                        href="mailto:?subject=Check out this Japanese Cuisine Dashboard&body=I found this cool dashboard, here is the link: [Paste Link Here]",
                        target="_blank",
                        style={
                            "textDecoration": "none", "color": "#A0A0A0",
                            "fontSize": "26px", "marginLeft": "20px"
                        }
                    ),
                    html.A(
                        html.I(className="fa fa-bug"),
                        id="bug-report-icon",
                        href="mailto:your-email@example.com?subject=Bug Report: Japanese Cuisine Dashboard",
                        target="_blank",
                        style={
                            "textDecoration": "none", "color": "#A0A0A0",
                            "fontSize": "26px", "marginLeft": "20px"
                        }
                    ),
                    html.A(
                        html.I(className="fa fa-envelope-o"),
                        id="open-contact-modal-btn",
                        n_clicks=0,
                        style={
                            "textDecoration": "none", "color": "#A0A0A0",
                            "fontSize": "26px", "marginLeft": "20px", "cursor": "pointer"
                        }
                    )
                ],
                style={"display": "flex", "alignItems": "center", "margin-left": "auto", "flex-shrink": 0}
            )
        ],
        id="top-bar",
        style={
            "display": "flex", "alignItems": "center",
            "padding": "10px 20px 0px 10px"
        }
    ),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Contact Us"), id="modal-header"),
            dbc.ModalBody([
                html.P("Have an enquiry or suggestion? Fill out the form below.", id="modal-p"),
                html.Div(id="contact-status", style={"marginBottom": "10px"}),
                dbc.Row([
                    dbc.Col(dbc.Label("Your Email:", id="modal-label-1"), width=12),
                    dbc.Col(dbc.Input(type="email", id="contact-email", placeholder="your.email@example.com"), width=12),
                ], style={"marginBottom": "10px"}),
                dbc.Row([
                    dbc.Col(dbc.Label("Your Message:", id="modal-label-2"), width=12),
                    dbc.Col(dbc.Textarea(id="contact-message", placeholder="Your message here...", style={"height": "120px"}), width=12),
                ]),
            ], id="modal-body"),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-contact-modal-btn", color="secondary"),
                dbc.Button("Send", id="send-contact-btn", color="primary", n_clicks=0),
            ], id="modal-footer"),
        ],
        id="contact-modal",
        is_open=False,
    ),

    dbc.Tooltip("Toggle Dark Mode", target="theme-toggle-btn", placement="bottom", id="theme-toggle-tooltip"),
    dbc.Tooltip("Report a bug or data error", target="bug-report-icon", placement="bottom"),
    dbc.Tooltip("Share with a friend", target="share-friend-icon", placement="bottom"),
    dbc.Tooltip("Contact Us", target="open-contact-modal-btn", placement="bottom"),

    html.Div(
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Row([
                        dbc.Col(
                            dbc.DropdownMenu(
                                label="Prefecture",
                                children=[
                                    html.Div(
                                        dbc.Checklist(id="prefecture-dropdown", options=prefecture_options),
                                        id="prefecture-checklist-container",
                                        style={"maxHeight": "150px", "overflowY": "auto", "padding": "5px 10px"}
                                    )
                                ],
                                id="prefecture-menu",
                                style={"width": "100%"}, color="light", toggle_style=filter_toggle_style,
                                className="filter-dropdown-menu"
                            ),
                            width=3
                        ),
                        dbc.Col(
                            dbc.DropdownMenu(
                                label="Season",
                                children=[
                                    html.Div(
                                        dbc.Checklist(id="season-dropdown", options=season_options),
                                        id="season-checklist-container",
                                        style={"maxHeight": "150px", "overflowY": "auto", "padding": "5px 10px"}
                                    )
                                ],
                                id="season-menu",
                                style={"width": "100%"}, color="light", toggle_style=filter_toggle_style,
                                className="filter-dropdown-menu"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dbc.DropdownMenu(
                                label="Type",
                                children=[
                                    html.Div(
                                        dbc.Checklist(id="type-dropdown", options=type_options),
                                        id="type-checklist-container",
                                        style={"maxHeight": "150px", "overflowY": "auto", "padding": "5px 10px"}
                                    )
                                ],
                                id="type-menu",
                                style={"width": "100%"}, color="light", toggle_style=filter_toggle_style,
                                className="filter-dropdown-menu"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dbc.DropdownMenu(
                                label="Dietary",
                                children=[
                                    html.Div(
                                        dbc.Checklist(id="dietary-dropdown", options=dietary_options),
                                        id="dietary-checklist-container",
                                        style={"maxHeight": "150px", "overflowY": "auto", "padding": "5px 10px"}
                                    )
                                ],
                                id="dietary-menu",
                                style={"width": "100%"}, color="light", toggle_style=filter_toggle_style,
                                className="filter-dropdown-menu"
                            ),
                            width=2
                        ),
                        dbc.Col(dish_search_dropdown, width=3),
                    ],
                    id="filter-panel",
                    style={
                        "position": "absolute", "top": "20px", "left": "20px", "right": "23px",
                        "zIndex": 1000, "backgroundColor": "rgba(255, 255, 255, 0.95)",
                        "padding": "10px 15px", "borderRadius": "10px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)", "alignItems": "center"
                    }),
                    
                    dcc.Graph(id="map", style={"flex": "1 1 auto", "border-radius": "15px","overflow": "hidden","minHeight": 0}),
                    
                    html.Button(
                        html.I(className="fa fa-map-marker"),
                        id="enable-location-btn",
                        n_clicks=0,
                        style={
                            "position": "absolute", "bottom": "75px", "right": "25px", "zIndex": "1000",
                            "backgroundColor": "white", "border": "1px solid #CCC",
                            "borderRadius": "50%", "width": "42px", "height": "42px",
                            "fontSize": "20px", "boxShadow": "0 2px 6px rgba(0,0,0,0.2)",
                            "cursor": "pointer", "display": "flex", "alignItems": "center",
                            "justifyContent": "center", "padding": "0"
                        }
                    ),
                    dbc.Tooltip("Enable Location", target="enable-location-btn", placement="left"),
                ],
                id="map-panel-wrapper",
                style={
                    "height": "100%", "border": "1px solid #E0E0E0",
                    "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.05)", "border-radius": "15px",
                    "padding": "20px", "box-sizing": "border-box", "display": "flex",
                    "flexDirection": "column", "backgroundColor": "#F8F9FA",
                    "position": "relative"
                }),
                width=5
            ),
            dbc.Col(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "Select a Dish",
                                    id="dish-title",
                                    style={
                                        "fontSize": "18px", "fontWeight": "600",
                                        "backgroundColor": "#e9ecef", "color": "#212529",
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "margin": 0,
                                        "flexShrink": 0
                                    }
                                ),
                                html.Span(
                                    "",
                                    id="dish-prefecture-badge",
                                    style={
                                        "fontSize": "18px", "fontWeight": "600",
                                        "backgroundColor": "#f8d7da",
                                        "color": "#721c24",
                                        "padding": "8px 16px", "borderRadius": "8px",
                                        "display": "none"
                                    }
                                )
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "flexWrap": "wrap",
                                "gap": "10px",
                                "marginBottom": "20px"
                            }
                        ),
                        
                        html.Div(
                            create_right_panel(dish_name=None),
                            id="dish-info",
                            style={
                                "display": "flex", "flexDirection": "column",
                                "flex": 1, "minHeight": 0
                            }
                        )
                    ],
                    id="info-panel-wrapper",
                    style={
                        "height": "100%", "border": "1px solid #E0E0E0",
                        "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                        "border-radius": "15px", "padding": "20px",
                        "box-sizing": "border-box", "display": "flex",
                        "flexDirection": "column", "backgroundColor": "#F8F9FA",
                        "overflowY": "auto"
                    }
                ),
                width=7
            )
        ], style={"flex": 1, "minHeight": 0, "margin": 0},className="g-4"),
        id="main-content",
        style={"display": "flex", "flexDirection": "column", "flex": 1,"padding": "0 20px 20px 20px"}
    )
],
fluid=True,
id="main-container",
style={"minHeight": "100vh", "display": "flex", "flexDirection": "column","backgroundColor": "#F0F2F5","fontFamily": "'Noto Sans JP', sans-serif"}
)

app.clientside_callback(
    """
    async function(n_clicks) {
        if (n_clicks > 0 && navigator.geolocation) {
            return new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        resolve({
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        });
                    },
                    function(error) {
                        resolve({'lat': null, 'lon': null});
                    }
                );
            });
        }
        return {'lat': null, 'lon': null};
    }
    """,
    Output("user-location", "data"),
    Input("enable-location-btn", "n_clicks")
)

@app.callback(
    Output("dark-mode", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("dark-mode", "data"),
    prevent_initial_call=True
)
def toggle_dark_mode(n_clicks, is_dark):
    return not is_dark

@app.callback(
    Output("main-container", "style"),
    Output("main-title", "style"),
    Output("top-bar", "style"),
    Output("bug-report-icon", "style"),
    Output("share-friend-icon", "style"),
    Output("open-contact-modal-btn", "style"),
    Output("theme-toggle-btn", "style"),
    Output("map-panel-wrapper", "style"),
    Output("info-panel-wrapper", "style"),
    Output("filter-panel", "style"),
    Output("dish-title", "style"),
    Output("enable-location-btn", "style"),
    Output("theme-icon", "className"),
    Output("theme-toggle-tooltip", "children"),
    Output("contact-modal", "style"),
    Output("modal-header", "style"),
    Output("modal-body", "style"),
    Output("modal-footer", "style"),
    Output("modal-p", "style"),
    Output("modal-label-1", "style"),
    Output("modal-label-2", "style"),
    Output("contact-email", "style"),
    Output("contact-message", "style"),
    Input("dark-mode", "data")
)
def update_theme_styles(is_dark):
    base_toggle_style = filter_toggle_style.copy()
    
    base_checklist_style = {"maxHeight": "150px", "overflowY": "auto", "padding": "5px 10px"}

    if is_dark:
        main_container_style = {"minHeight": "100vh", "display": "flex", "flexDirection": "column","backgroundColor": "#121212","fontFamily": "'Noto Sans JP', sans-serif"}
        main_title_style = {"margin": "0", "color": "#E0E0E0"}
        top_bar_style = {"display": "flex", "alignItems": "center", "padding": "10px 20px 0px 10px"}
        
        icon_style = {"textDecoration": "none", "color": "#888", "fontSize": "26px", "marginLeft": "20px"}
        toggle_icon_style = {"textDecoration": "none", "color": "#888", "fontSize": "26px", "cursor": "pointer"}
        
        map_panel_style = {
            "height": "100%", "border": "1px solid #3a3a3a", "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
            "border-radius": "15px", "padding": "20px", "box-sizing": "border-box", "display": "flex",
            "flexDirection": "column", "backgroundColor": "#1a1a1a", "position": "relative"
        }
        info_panel_style = {
            "height": "100%", "border": "1px solid #3a3a3a", "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
            "border-radius": "15px", "padding": "20px", "box-sizing": "border-box", "display": "flex",
            "flexDirection": "column", "backgroundColor": "#1a1a1a", "overflowY": "auto"
        }
        filter_panel_style = {
            "position": "absolute", "top": "20px", "left": "20px", "right": "23px", "zIndex": 1000,
            "backgroundColor": "rgba(43, 43, 43, 0.95)",
            "padding": "10px 15px", "borderRadius": "10px", "boxShadow": "0 2px 8px rgba(0,0,0,0.5)",
            "alignItems": "center"
        }
        
        dish_title_style = {
            "fontSize": "18px", "fontWeight": "600", "backgroundColor": "#3a3a3a", "color": "#E0E0E0",
            "padding": "8px 16px", "borderRadius": "8px",
            "margin": 0, "flexShrink": 0
        }

        location_btn_style = {
            "position": "absolute", "bottom": "75px", "right": "25px", "zIndex": "1000",
            "backgroundColor": "#3a3a3a", "border": "1px solid #4a4a4a",
            "borderRadius": "50%", "width": "42px", "height": "42px", "fontSize": "20px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.5)", "cursor": "pointer", "display": "flex",
            "alignItems": "center", "justifyContent": "center", "padding": "0", "color": "#E0E0E0"
        }
        theme_icon_class = "fa fa-sun-o"
        
        
        modal_style = {"backgroundColor": "#2b2b2b"}
        modal_header_style = {"borderBottom": "1px solid #3a3a3a", "color": "#E0E0E0"}
        modal_body_style = {"backgroundColor": "#2b2b2b"}
        modal_footer_style = {"backgroundColor": "#2b2b2b", "borderTop": "1px solid #3a3a3a"}
        modal_p_style = {"color": "#B0B0B0"}
        modal_label_style = {"color": "#E0E0E0"}
        modal_input_style = {"backgroundColor": "#3a3a3a", "color": "#E0E0E0", "border": "1px solid #4a4a4a"}
        modal_textarea_style = {"height": "120px", "backgroundColor": "#3a3a3a", "color": "#E0E0E0", "border": "1px solid #4a4a4a"}

        return (
            main_container_style, main_title_style, top_bar_style,
            icon_style, icon_style, icon_style, toggle_icon_style,
            map_panel_style, info_panel_style, filter_panel_style, dish_title_style, location_btn_style,
            theme_icon_class,
            "Toggle Light Mode",
            modal_style, modal_header_style, modal_body_style, modal_footer_style,
            modal_p_style, modal_label_style, modal_label_style,
            modal_input_style, modal_textarea_style
        )
        
    else:
        main_container_style = {"minHeight": "100vh", "display": "flex", "flexDirection": "column","backgroundColor": "#F0F2F5","fontFamily": "'Noto Sans JP', sans-serif"}
        main_title_style = {"margin": "0", "color": "black"}
        top_bar_style = {"display": "flex", "alignItems": "center", "padding": "10px 20px 0px 10px"}
        
        icon_style = {"textDecoration": "none", "color": "#A0A0A0", "fontSize": "26px", "marginLeft": "20px"}
        toggle_icon_style = {"textDecoration": "none", "color": "#A0A0A0", "fontSize": "26px", "cursor": "pointer"}

        map_panel_style = {
            "height": "100%", "border": "1px solid #E0E0E0", "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
            "border-radius": "15px", "padding": "20px", "box-sizing": "border-box", "display": "flex",
            "flexDirection": "column", "backgroundColor": "#F8F9FA", "position": "relative"
        }
        info_panel_style = {
            "height": "100%", "border": "1px solid #E0E0E0", "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
            "border-radius": "15px", "padding": "20px", "box-sizing": "border-box", "display": "flex",
            "flexDirection": "column", "backgroundColor": "#F8F9FA", "overflowY": "auto"
        }
        filter_panel_style = {
            "position": "absolute", "top": "20px", "left": "20px", "right": "23px", "zIndex": 1000,
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "padding": "10px 15px", "borderRadius": "10px", "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
            "alignItems": "center"
        }
        
        dish_title_style = {
            "fontSize": "18px", "fontWeight": "600", "backgroundColor": "#e9ecef", "color": "#212529",
            "padding": "8px 16px", "borderRadius": "8px",
            "margin": 0, "flexShrink": 0
        }

        location_btn_style = {
            "position": "absolute", "bottom": "75px", "right": "25px", "zIndex": "1000",
            "backgroundColor": "white", "border": "1px solid #CCC",
            "borderRadius": "50%", "width": "42px", "height": "42px", "fontSize": "20px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.2)", "cursor": "pointer", "display": "flex",
            "alignItems": "center", "justifyContent": "center", "padding": "0", "color": "black"
        }
        theme_icon_class = "fa fa-moon-o"
        
        
        modal_style = {}
        modal_header_style = {}
        modal_body_style = {}
        modal_footer_style = {}
        modal_p_style = {}
        modal_label_style = {}
        modal_input_style = {}
        modal_textarea_style = {"height": "120px"}
        
        return (
            main_container_style, main_title_style, top_bar_style,
            icon_style, icon_style, icon_style, toggle_icon_style,
            map_panel_style, info_panel_style, filter_panel_style, dish_title_style, location_btn_style,
            theme_icon_class,
            "Toggle Dark Mode",
            modal_style, modal_header_style, modal_body_style, modal_footer_style,
            modal_p_style, modal_label_style, modal_label_style,
            modal_input_style, modal_textarea_style
        )


@app.callback(
    Output("map", "figure"),
    Input("prefecture-dropdown", "value"),
    Input("season-dropdown", "value"),
    Input("type-dropdown", "value"),
    Input("dietary-dropdown", "value"),
    Input("dish-search", "value"),
    Input("user-location", "data"),
    Input("clicked-dish", "data"),
    Input("dark-mode", "data")
)
def update_map(selected_prefectures, selected_seasons, selected_types, selected_dietary, selected_dish, user_location, clicked_dish, is_dark):
    filtered = dishes.copy()
    
    map_center = {"lat": 36, "lon": 138}
    map_zoom = 4

    if selected_prefectures:
        filtered = filtered[filtered["prefecture"].isin(selected_prefectures)]
    if selected_seasons:
        filtered = filtered[filtered["seasonality"].isin(selected_seasons)]
    if selected_types:
        filtered = filtered[filtered["type"].isin(selected_types)]
    if selected_dietary:
        for col in selected_dietary:
            filtered = filtered[filtered[col] == True]
    
    if selected_dish:
        filtered = filtered[filtered["dish_name"] == selected_dish]
        
    fig = px.scatter_map(
        filtered,
        lat="area_lat",
        lon="area_lon",
        hover_name="dish_name",
        zoom=map_zoom,
        center=map_center,
        color_discrete_sequence=["#FFFA00"],
        size_max=20,
    )

    fig.update_traces(
        hovertemplate="%{hovertext}<extra></extra>"
    )
    fig.update_traces(marker=dict(size=20))
    
    if not selected_dish:
        fig.update_traces(cluster=dict(enabled=True))

    if user_location and user_location.get("lat") and user_location.get("lon"):
        fig.add_scattermap(
            lat=[user_location["lat"]],
            lon=[user_location["lon"]],
            mode="markers",
            marker=dict(size=15, color="#079DFF", symbol="circle"),
            hoverinfo="text",
            hovertext=["Current Location"],
            name="User Location",
            showlegend=False
        )

    if clicked_dish:
        selected_row = dishes[dishes["dish_name"] == clicked_dish]
        if not selected_row.empty:
            lat = selected_row.iloc[0]["area_lat"]
            lon = selected_row.iloc[0]["area_lon"]
            fig.add_scattermap(
                lat=[lat],
                lon=[lon],
                mode="markers",
                marker=dict(size=20, color="#FF6000", symbol="circle"),
                name="Selected Dish",
                showlegend=False,
                hoverinfo="none"
            )

    map_style = "dark" if is_dark else "light"

    fig.update_layout(map_style=map_style, margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(uirevision="keep-zoom")

    return fig


@app.callback(
    Output("dish-info", "children"),
    Output("dish-title", "children"),
    Output("dish-prefecture-badge", "children"),
    Output("dish-prefecture-badge", "style"),
    Input("map", "clickData"),
    Input("dark-mode", "data"),
    Input("user-location", "data"),
    State("clicked-dish", "data")
)
def display_dish_info(clickData, is_dark, user_location, clicked_dish_name):
    
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    dish_name_to_render = None
    
    if trigger_id == "map":
        if clickData:
            dish_name_to_render = clickData["points"][0]["hovertext"]
    
    elif trigger_id == "dark-mode" or trigger_id == "user-location":
        dish_name_to_render = clicked_dish_name
    
    if dish_name_to_render:
        row = dishes[dishes["dish_name"] == dish_name_to_render]
        if not row.empty:
            main_ingredients = row.iloc[0]["main_ingredients"]
            history = row.iloc[0]["history"]
            image_url = row.iloc[0]["image_url"] if "image_url" in row.columns else None
            prefecture = row.iloc[0]["prefecture"]
            
            colors = REGION_COLORS.get(prefecture, REGION_COLORS["default"])
            
            if is_dark:
                bg_color = colors["text"]
                text_color = colors["background"]
            else:
                bg_color = colors["background"]
                text_color = colors["text"]

            base_badge_style = {
                "fontSize": "18px",
                "fontWeight": "600",
                "padding": "8px 16px",
                "borderRadius": "8px"
            }
            
            badge_style_visible = {
                **base_badge_style,
                "backgroundColor": bg_color,
                "color": text_color,
                "display": "inline-block"
            }
            
            panel_content = create_right_panel(
                main_ingredients,
                history,
                dish_name=dish_name_to_render,
                image_url=image_url,
                user_location=user_location,
                is_dark_mode=is_dark
            )
            return panel_content, dish_name_to_render, f"{prefecture} Prefecture", badge_style_visible
    
    default_panel = create_right_panel(dish_name=None, is_dark_mode=is_dark)
    
    default_colors = REGION_COLORS["default"]
    
    if is_dark:
        default_bg = default_colors["text"]
        default_text = default_colors["background"]
    else:
        default_bg = default_colors["background"]
        default_text = default_colors["text"]
        
    badge_style_hidden_default = {
        "fontSize": "18px", "fontWeight": "600",
        "backgroundColor": default_bg,
        "color": default_text,
        "padding": "8px 16px", "borderRadius": "8px",
        "display": "none"
    }
    
    return default_panel, "Select a Dish", "", badge_style_hidden_default


@app.callback(
    Output("radar-chart", "figure"),
    Output("chart-subtitle-wrapper", "children"),
    Output("chart-annotation-box", "children"),
    Output("chart-annotation-box", "style"),
    Input("clicked-dish", "data"),
    Input("standardize-scale-checkbox", "value"),
    Input("dark-mode", "data"),
    prevent_initial_call=True
)
def update_radar_chart(dish_name, standardize_scale, is_dark):
    
    if dish_name is None:
        fig, subtitle, annotation_children, annotation_style, _ = \
            generate_radar_chart_elements(None, False, is_dark_mode=is_dark)
        return fig, subtitle, annotation_children, annotation_style

    fig, subtitle_children, annotation_box_children, annotation_box_style, _ = \
        generate_radar_chart_elements(dish_name, standardize_scale, is_dark_mode=is_dark)
    
    return fig, subtitle_children, annotation_box_children, annotation_box_style

@app.callback(
    Output("clicked-dish", "data"),
    Input("map", "clickData")
)
def store_clicked_dish(clickData):
    if clickData:
        return clickData["points"][0]["hovertext"]
    return None

@app.callback(
    Output("contact-modal", "is_open"),
    Output("contact-status", "children"),
    Output("contact-email", "value"),
    Output("contact-message", "value"),
    [
        Input("open-contact-modal-btn", "n_clicks"),
        Input("close-contact-modal-btn", "n_clicks"),
        Input("send-contact-btn", "n_clicks")
    ],
    [
        State("contact-modal", "is_open"),
        State("contact-email", "value"),
        State("contact-message", "value")
    ],
    prevent_initial_call=True
)
def handle_contact_modal(n_open, n_close, n_send, is_open, email, message):
    
    ctx = callback_context
    if not ctx.triggered:
        return is_open, None, email, message

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "open-contact-modal-btn":
        return True, None, "", ""
    
    if trigger_id == "close-contact-modal-btn":
        return False, None, "", ""

    if trigger_id == "send-contact-btn":
        if not email or not message:
            return (
                True,
                dbc.Alert("Please fill in both your email and message.", color="warning"),
                email,
                message
            )
        
        FORMSPREE_URL = "https://formspree.io/f/mdkplrqg"
        data = {"email": email, "message": message}

        try:
            response = requests.post(FORMSPREE_URL, data=data)
            
            if response.ok:
                return (
                    False,
                    dbc.Alert("Success! Your message has been sent.", color="success"),
                    "",
                    ""
                )
            else:
                return (
                    True,
                    dbc.Alert("Error: Could not send message. Please try again.", color="danger"),
                    email,
                    message
                )
        except requests.exceptions.RequestException as e:
            return (
                True,
                dbc.Alert(f"Network Error: {e}. Please check your connection.", color="danger"),
                email,
                message
            )

    return is_open, None, email, message


if __name__ == '__main__':
    app.run(debug=True)
