from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import ast

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
def create_right_panel(main_ingredients="", history="", dish_name=None, image_url=None):
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

    top_row = dbc.Row(
        [
            dbc.Col(left_box, width=6, style={"height": "100%"}),
            dbc.Col(right_box, width=6, style={"height": "100%"})
        ],
        style={"height": "50%", "margin-bottom": "10px"}
    )

    row = dishes[dishes["dish_name"] == dish_name]
    if not row.empty and "places" in row.columns:
        places_str = row.iloc[0]["places"]
        try:
            place_ids = ast.literal_eval(places_str) if places_str else []
        except Exception:
            place_ids = []

        if place_ids:
            place_rows = places[places["id"].isin(place_ids)].copy()
            place_rows["rating"] = place_rows["rating"].apply(lambda x: x if pd.notna(x) else "?")
            place_rows["distance"] = "?"
            table_df = place_rows[["name", "distance", "rating", "price_level", "googleMapsUri"]]
            table_df.columns = ["Place Name", "Distance", "Rating", "Price", "Link"]

            bottom_box = dash_table.DataTable(
                columns=[{"name": c, "id": c, "presentation": "markdown"} for c in table_df.columns],
                data=table_df.to_dict("records"),
                style_table={"height": "100%", "overflowY": "auto"},
                style_cell={"textAlign": "left", "padding": "5px"},
                style_header={"fontWeight": "bold"},
                markdown_options={"link_target": "_blank"},
                sort_action="native"
            )
        else:
            bottom_box = html.Div("This dish has no places", style={"margin": "auto", "textAlign": "center"})
    else:
        bottom_box = html.Div("This dish has no places", style={"margin": "auto", "textAlign": "center"})

    bottom_row = dbc.Row(dbc.Col(bottom_box), style={"height": "50%"})

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
                                placeholder="Select prefecture(s)",
                                multi=True
                            ), width=2
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="season-dropdown",
                                options=season_options,
                                placeholder="Select season(s)",
                                multi=True,
                                searchable=False,
                            ), width=2
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="type-dropdown",
                                options=type_options,
                                placeholder="Select type(s)",
                                multi=True,
                                searchable=False,
                            ), width=2
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="dietary-dropdown",
                                options=dietary_options,
                                placeholder="Select dietary restriction(s)",
                                multi=True,
                                searchable=False,
                            ), width=2
                        ),
                        dbc.Col(dish_search_dropdown, width=4),
                    ], style={"margin-bottom": "10px"}),

                    dcc.Graph(id="map", style={"height": "calc(100% - 90px)", "border-radius": "15px"})
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
    Input("map", "clickData")
)
def display_dish_info(clickData):
    if clickData:
        dish_name = clickData["points"][0]["hovertext"]
        row = dishes[dishes["dish_name"] == dish_name]
        if not row.empty:
            main_ingredients = row.iloc[0]["main_ingredients"]
            history = row.iloc[0]["history"]
            image_url = row.iloc[0]["image_url"] if "image_url" in row.columns else None
            return create_right_panel(main_ingredients, history, dish_name=dish_name, image_url=image_url)
    return create_right_panel()

if __name__ == '__main__':
    app.run(debug=True)
