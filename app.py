"""
Global Development Explorer
An interactive multi-view dashboard built with Plotly + Dash.

Four visualizations (choropleth map, bubble scatter plot, bar chart,
and line chart) share two controls (a Year slider and a Continent
filter) and are additionally filtered by click events- clicking a
country on the map, in the scatter plot, or in the bar chart updates the
line chart to show that country's life-expectancy trend over time.

Run locally:
    python app.py
Then open http://127.0.0.1:8050 in your browser.

"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, ctx


raw = px.data.gapminder()

df = raw.copy()
df = df.rename(columns={
    "country": "Country",
    "continent": "Continent",
    "year": "Year",
    "lifeExp": "LifeExpectancy",
    "pop": "Population",
    "gdpPercap": "GDPperCapita",
    "iso_alpha": "ISOAlpha",
    "iso_num": "ISONumeric",
})
df = df.dropna(subset=["Country", "Continent", "Year", "LifeExpectancy",
                        "Population", "GDPperCapita"])
df["PopulationMillions"] = df["Population"] / 1_000_000
df["Year"] = df["Year"].astype(int)

YEARS = sorted(df["Year"].unique())
CONTINENTS = sorted(df["Continent"].unique())
DEFAULT_COUNTRY = "United States"


app = Dash(__name__)
app.title = "Global Development Explorer"
server = app.server  

app.layout = html.Div(
    style={"fontFamily": "Helvetica, Arial, sans-serif", "margin": "20px"},
    children=[
        html.H1("Global Development Explorer"),
        html.P(
            "An interactive dashboard exploring life expectancy, GDP per "
            "capita, and population across countries and time (Gapminder "
            "dataset, 1952-2007). Use the controls below to filter every "
            "chart at once, or click a country on any chart to see its "
            "trend line."
        ),

        html.Div(
            style={"display": "flex", "gap": "40px", "flexWrap": "wrap",
                   "marginBottom": "10px"},
            children=[
                html.Div(
                    style={"minWidth": "400px", "flex": "2"},
                    children=[
                        html.Label("Year"),
                        dcc.Slider(
                            id="year-slider",
                            min=min(YEARS),
                            max=max(YEARS),
                            step=None,
                            value=max(YEARS),
                            marks={int(y): str(y) for y in YEARS},
                        ),
                    ],
                ),
                html.Div(
                    style={"minWidth": "250px", "flex": "1"},
                    children=[
                        html.Label("Continent"),
                        dcc.Dropdown(
                            id="continent-filter",
                            options=[{"label": c, "value": c} for c in CONTINENTS],
                            value=CONTINENTS,
                            multi=True,
                        ),
                    ],
                ),
            ],
        ),

        dcc.Store(id="selected-country", data=DEFAULT_COUNTRY),

        html.Div(
            style={"display": "grid",
                   "gridTemplateColumns": "1fr 1fr",
                   "gap": "10px"},
            children=[
                dcc.Graph(id="map-chart"),
                dcc.Graph(id="scatter-chart"),
                dcc.Graph(id="bar-chart"),
                dcc.Graph(id="line-chart"),
            ],
        ),

        html.P(
            "Tip: click any country (on the map, in the bubble chart, or "
            "in the bar chart) to update the trend line in the "
            "bottom-right panel.",
            style={"fontStyle": "italic", "color": "#555"},
        ),
    ],
)


def _filter(year, continents):
    return df[(df["Year"] == year) & (df["Continent"].isin(continents))]


@app.callback(
    Output("map-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
)
def update_map(year, continents):
    dff = _filter(year, continents)
    fig = px.choropleth(
        dff, locations="ISOAlpha", color="LifeExpectancy",
        hover_name="Country", color_continuous_scale="Viridis",
        range_color=(df["LifeExpectancy"].min(), df["LifeExpectancy"].max()),
        title=f"Life Expectancy by Country ({year})",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


@app.callback(
    Output("scatter-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
)
def update_scatter(year, continents):
    dff = _filter(year, continents)
    fig = px.scatter(
        dff, x="GDPperCapita", y="LifeExpectancy",
        size="PopulationMillions", color="Continent",
        hover_name="Country", log_x=True, size_max=55,
        title=f"GDP per Capita vs. Life Expectancy ({year})",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


@app.callback(
    Output("bar-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
)
def update_bar(year, continents):
    dff = _filter(year, continents).nlargest(15, "GDPperCapita")
    fig = px.bar(
        dff.sort_values("GDPperCapita"),
        x="GDPperCapita", y="Country", orientation="h",
        color="Continent",
        title=f"Top 15 Countries by GDP per Capita ({year})",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


@app.callback(
    Output("selected-country", "data"),
    Input("map-chart", "clickData"),
    Input("scatter-chart", "clickData"),
    Input("bar-chart", "clickData"),
    State("selected-country", "data"),
)
def update_selected_country(map_click, scatter_click, bar_click, current):
    triggered = ctx.triggered_id
    if triggered == "map-chart" and map_click:
        return map_click["points"][0]["hovertext"]
    if triggered == "scatter-chart" and scatter_click:
        return scatter_click["points"][0]["hovertext"]
    if triggered == "bar-chart" and bar_click:
        return bar_click["points"][0]["y"]
    return current


@app.callback(
    Output("line-chart", "figure"),
    Input("selected-country", "data"),
    Input("continent-filter", "value"),
)
def update_line(country, continents):
    dff = df[(df["Country"] == country) & (df["Continent"].isin(continents))]
    if dff.empty:
        dff = df[df["Country"] == country]
    fig = px.line(
        dff.sort_values("Year"), x="Year", y="LifeExpectancy",
        markers=True,
        title=f"Life Expectancy Trend: {country}",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


if __name__ == "__main__":
    app.run(debug=True)
