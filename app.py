from dash import Dash, dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import ast
import numpy as np

# Haversine 距离计算函数
def haversine(lat1, lon1, lat2, lon2):
    # 既然您确认所有餐厅都有经纬度，这里的检查是为用户位置(如果还没获取到)
    if any(pd.isna([lat1, lon1, lat2, lon2])):
        return np.nan

    R = 6371  # 地球半径 (公里)

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = R * c
    return km

# Load your data
dishes = pd.read_csv("all_dishes.csv")
places = pd.read_csv("all_places.csv")

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Box style
box_style = {
    "border": "3px solid black",
    "border-radius": "15px",
    "padding": "10px",
    "box-sizing": "border-box",
    "display": "flex",
    "flexDirection": "column",
    "height": "100%",
    "overflow": "hidden"
}

# Right panel generator
def create_right_panel(main_ingredients="", history="", dish_name=None, image_url=None, user_location=None):
    if dish_name is None:
        return html.Div(
            html.P("Please select a dish on the map"),
            style={"margin": "auto", "textAlign": "center", "fontSize": "20px"}
        )

    left_box = html.Div(
        [
            html.Div([
                html.Img(
                    src=image_url,
                    style={"width": "100%", "margin-bottom": "10px", "border-radius": "5px"}
                ) if image_url else None,
                html.Div(history, style={"overflowY": "auto", "flex": "1"})
            ], style={"display": "flex", "flexDirection": "column", "height": "100%"} )
        ],
        style=box_style
    )

    right_box = html.Div(
        [
            html.H5("Main Ingredients"),
            html.Div(main_ingredients, style={"overflowY": "auto", "flex": "1"})
        ],
        style=box_style
    )

 # --- [!!新代码!!] ---
    # 为 "无餐厅" 情况定义消息框
    message_box_style = {
        "border": "3px solid black",
        # "background-color": "black", 
        # "color": "white",
        "border-radius": "15px",
        "padding": "10px",
        # "height": "100%", # <-- [!!修改!!] 移除这一行
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",
        "textAlign": "center"
    }


    message_box = html.Div(
        html.P([  # <-- [!!修改!!] 改为列表以支持换行
            "Sorry, no restaurants are recommended at the moment.", # <-- 第一行
            html.Br(), # <-- [!!修改!!] 添加换行符
            "We’ll be updating soon, stay tuned!" # <-- 第二行
        ], style={"margin": "auto", "fontSize": "18px", "fontWeight": "bold"}),
        style=message_box_style
    )
    # --- [!!新代码结束!!] ---

# [最终代码块 - 开始]
    row = dishes[dishes["dish_name"] == dish_name]
    
    # --- [!!关键修改!!] ---
    # 默认样式：假设没有餐厅
    top_row_style = {"height": "70%"}
    bottom_row_style = {"height": "30%"}
    bottom_box = message_box # 默认显示消息

    # [!!新!!] 默认 bottom_col 样式：用于居中小消息框
    bottom_col_style = {
        "height": "100%", 
        "display": "flex", 
        "align-items": "center", 
        "justify-content": "center"
    }
    # --- [!!关键修改结束!!] ---

    if not row.empty and "places" in row.columns:
        places_str = row.iloc[0]["places"]
        try:
            place_ids = ast.literal_eval(places_str) if places_str else []
        except Exception:
            place_ids = []

        if place_ids:
            # --- [!!关键修改!!] ---
            # 发现有餐厅！覆盖样式
            top_row_style = {"height": "50%"}
            bottom_row_style = {"height": "50%"}
            
            # [!!新!!] 覆盖 bottom_col 样式：让表格占满 100%
            bottom_col_style = {"height": "100%"}
            # --- [!!关键修改结束!!] ---

            place_rows = places[places["id"].isin(place_ids)].copy()
            place_rows["rating"] = place_rows["rating"].apply(lambda x: x if pd.notna(x) else "?")
            
            # 距离计算
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
            table_df["Price"] = table_df["Price"].map(price_mapping).fillna("?")
            table_df["Link"] = table_df["googleMapsUri"].apply(
                lambda x: f"[📍]({x})" if pd.notna(x) else ""
            )
            final_columns = ["Place Name", "Distance", "Rating", "Price", "Link"]
            table_df = table_df[final_columns]
            rating_style_rules = [
                {
                    'if': {
                        'column_id': 'Rating',
                        'filter_query': '{Rating} >= 4 && {Rating} is num'
                    },
                    'color': 'green',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'column_id': 'Rating',
                        'filter_query': '{Rating} >= 3 && {Rating} < 4 && {Rating} is num'
                    },
                    'color': 'orange',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'column_id': 'Rating',
                        'filter_query': '{Rating} < 3 && {Rating} is num'
                    },
                    'color': 'red',
                    'fontWeight': 'bold'
                }
            ]
            alignment_rules = [
                {
                    'if': {'column_id': ['Rating', 'Price', 'Link']}, 
                    'textAlign': 'center' 
                },
                {
                    'if': {'column_id': ['Place Name', 'Distance']},
                    'textAlign': 'center'  
                }
            ]
            columns_config = []
            for col_name in final_columns:
                if col_name == "Link":
                    columns_config.append({
                        "name": "Map", 
                        "id": col_name,
                        "presentation": "markdown"
                    })
                else:
                    columns_config.append({"name": col_name, "id": col_name})
            
            # 用表格内容填充 bottom_box
            bottom_box = dash_table.DataTable(
                columns=columns_config, 
                data=table_df.to_dict("records"),
                style_table={"height": "100%", "overflowY": "auto"},
                style_cell={"padding": "5px"}, 
                style_header={"fontWeight": "bold"},
                markdown_options={"link_target": "_blank"},
                sort_action="native",
                style_data_conditional=rating_style_rules,
                style_cell_conditional=alignment_rules,
                style_header_conditional=[
                    {
                        'if': {'column_id': ['Rating', 'Price', 'Link']},
                        'textAlign': 'center'
                    },
                    {
                        'if': {'column_id': ['Place Name', 'Distance']},
                        'textAlign': 'center'
                    }
                ]
            )
        # (如果 place_ids 为空, bottom_box 保持默认的 message_box, bottom_col_style 保持居中)
    # (如果 row 为空, bottom_box 保持默认的 message_box, bottom_col_style 保持居中)

    # --- [!!关键修改!!] ---
    # 现在（在所有 if/else 逻辑之后）根据动态样式创建 top_row 和 bottom_row
    top_row = dbc.Row(
        [
            dbc.Col(left_box, width=6, style={"height": "100%"}),
            dbc.Col(right_box, width=6, style={"height": "100%"})
        ],
        style=top_row_style  # <-- 使用动态样式
    )

    bottom_row = dbc.Row(
        dbc.Col(bottom_box, style=bottom_col_style), # <-- [!!修改!!] 使用动态列样式
        style=bottom_row_style
    ) 
# [最终代码块 - 结束]
    return html.Div(
        [
            dbc.Row(dbc.Col(html.H4(dish_name), style={"margin-bottom": "10px"})),
            top_row,
            bottom_row
        ],
        style={"height": "100%", "display": "flex", "flexDirection": "column", "gap": "10px"}
    )

right_content = html.Div(create_right_panel(), id="dish-info",
                         style={"height": "100%", "padding": "10px", "box-sizing": "border-box"})

prefecture_options = [{"label": p, "value": p} for p in pd.unique(dishes["prefecture"].dropna())]

season_order = ["all season", "spring", "summer", "fall", "winter"]
season_options = [{"label": s.title(), "value": s} for s in season_order if s in dishes["seasonality"].dropna().unique()]

type_options = [{"label": t, "value": t} for t in sorted(pd.unique(dishes["type"].dropna()))]

dietary_columns = ["vegan","vegetarian","no_gluten","no_seafood","no_pork","no_dairy","no_nuts"]
dietary_labels = {
    "vegan": "Vegan",
    "vegetarian": "Vegetarian",
    "no_gluten": "No Gluten",
    "no_seafood": "No Seafood",
    "no_pork": "No Pork",
    "no_dairy": "No Dairy",
    "no_nuts": "No Nuts"
}
dietary_options = [{"label": dietary_labels[col], "value": col} for col in dietary_columns]

dish_search_options = [{"label": name, "value": name} for name in dishes["dish_name"]]
dish_search_dropdown = dcc.Dropdown(
    id="dish-search",
    options=dish_search_options,
    placeholder="Search for a dish",
    multi=False,
    searchable=True,
    clearable=True,
    style={"width": "100%"},
    optionHeight=50
)

app.layout = dbc.Container([
    html.H1("Japanese Regional Cuisine", style={"margin": "10px"}),

    # Store for user location
    dcc.Store(id="user-location", storage_type="session"),

    # Enable location button
    html.Button("Enable Location", id="enable-location-btn", n_clicks=0, style={
        "position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"
    }),

    html.Div(
        dbc.Row([
            dbc.Col(
                html.Div([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id="prefecture-dropdown",
                                options=prefecture_options,
                                placeholder="Prefecture",
                                multi=True
                            ), width=2  # <-- 当前宽度
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="season-dropdown",
                                options=season_options,
                                placeholder="Season",
                                multi=True,
                                searchable=False,
                            ), width=2  # <-- 当前宽度
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="type-dropdown",
                                options=type_options,
                                placeholder="Type",
                                multi=True,
                                searchable=False,
                            ), width=2  # <-- 当前宽度
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="dietary-dropdown",
                                options=dietary_options,
                                placeholder="Dietary",
                                multi=True,
                                searchable=False,
                            ), width=2  # <-- 当前宽度
                        ),
                        dbc.Col(dish_search_dropdown, width=4), # <-- 当前宽度
                    ], style={"margin-bottom": "10px"}),
                    
                    # --- [!!修改!!] 调整地图高度以适应两行下拉框 ---
                    dcc.Graph(id="map", style={"height": "calc(100% - 140px)", "border-radius": "15px"})
                ],
                style={
                    "height": "100%",
                    "border": "3px solid black",
                    "border-radius": "15px",
                    "padding": "10px",
                    "box-sizing": "border-box",
                    "display": "flex",
                    "flexDirection": "column"
                }),
                width=6
            ),
            dbc.Col(right_content, width=6)
        ], style={"height": "100%", "margin": 0}),
        style={"display": "flex", "flexDirection": "column", "flex": 1}
    )
], fluid=True, style={"height": "100vh", "display": "flex", "flexDirection": "column"})

#JS
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
                        resolve({'lat': null, 'lon': null}); // fallback if permission denied
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


# Update map callback
@app.callback(
    Output("map", "figure"),
    Input("prefecture-dropdown", "value"),
    Input("season-dropdown", "value"),
    Input("type-dropdown", "value"),
    Input("dietary-dropdown", "value"),
    Input("dish-search", "value"),
    Input("user-location", "data")
)
def update_map(selected_prefectures, selected_seasons, selected_types, selected_dietary, selected_dish, user_location):
    filtered = dishes.copy()
    
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
        zoom=4,
        color_discrete_sequence=["white"],
        size_max=20,
    )

    # Only show dish name in hover
    fig.update_traces(
        hovertemplate="%{hovertext}<extra></extra>"  # use hovertext (dish_name) and remove extra info
    )
    fig.update_traces(marker=dict(size=20))
    fig.update_traces(cluster=dict(enabled=True))

    # Add user marker
    if user_location and user_location.get("lat") and user_location.get("lon"):
        fig.add_scattermap(
            lat=[user_location["lat"]],
            lon=[user_location["lon"]],
            mode="markers",
            marker=dict(size=15, color="blue", symbol="circle"),
            hoverinfo="text",
            hovertext=["Current Location"],
            name="User Location",
            showlegend=False
        )

    fig.update_layout(map_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Right panel update
@app.callback(
    Output("dish-info", "children"),
    Input("map", "clickData"),
    State("user-location", "data")  # <-- [!!修改!!] 添加 State
)
def display_dish_info(clickData, user_location): # <-- [!!修改!!] 添加 user_location 参数
    if clickData:
        dish_name = clickData["points"][0]["hovertext"]
        row = dishes[dishes["dish_name"] == dish_name]
        if not row.empty:
            main_ingredients = row.iloc[0]["main_ingredients"]
            history = row.iloc[0]["history"]
            image_url = row.iloc[0]["image_url"] if "image_url" in row.columns else None
            # [!!修改!!] 将 user_location 传递给 create_right_panel
            return create_right_panel(
                main_ingredients, 
                history, 
                dish_name=dish_name, 
                image_url=image_url, 
                user_location=user_location 
            )
    


if __name__ == '__main__':
    app.run(debug=True)
