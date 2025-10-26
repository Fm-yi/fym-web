from plotly.data import gapminder
from dash import dcc, html, Dash, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors

css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css", ]
app = Dash(name="Gapminder Dashboard", external_stylesheets=css)

################### DATASET ####################################
gapminder_df = gapminder(datetimes=True, centroids=True, pretty_names=True)
gapminder_df["Year"] = gapminder_df.Year.dt.year

#################### CHARTS #####################################
def create_table():
    fig = go.Figure(data=[go.Table(
        header=dict(values=gapminder_df.columns, align='left',
                   fill_color='#2E86AB', font=dict(color='white', size=14),
                   height=40),
        cells=dict(values=gapminder_df.values.T, align='left',
                  fill_color='#F8F9FA', font=dict(size=12),
                  height=30))
    ])
    fig.update_layout(paper_bgcolor="#e5ecf6", margin={"t":0, "l":0, "r":0, "b":0}, height=700)
    return fig

def create_population_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="Population", ascending=False)

    # 豪华3D饼图
    fig = px.pie(filtered_df, values="Population", names="Country",
                 title=f"🌍 Population Distribution - {continent} {year}",
                 hover_data=["Population"],
                 color_discrete_sequence=px.colors.qualitative.Vivid)
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        pull=[0.05 if i < 3 else 0 for i in range(len(filtered_df))],  # 前三名稍微突出
        marker=dict(line=dict(color='white', width=2)),
        opacity=0.9,
        hovertemplate="<b>%{label}</b><br>Population: %{value:,.0f}<br>Share: %{percent}<extra></extra>"
    )
    
    fig.update_layout(
        paper_bgcolor="#e5ecf6",
        height=700,
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        title_font=dict(size=20, color="#2c3e50", family="Arial, sans-serif"),
        annotations=[dict(text=f"Total: {filtered_df['Population'].sum():,}", 
                         x=0.5, y=-0.1, font_size=14, showarrow=False)]
    )
    
    return fig

def create_gdp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="GDP per Capita", ascending=False)

    # 豪华气泡图
    fig = px.scatter(filtered_df, 
                     x="Country", 
                     y="GDP per Capita", 
                     size="Population",
                     size_max=60,
                     color="Life Expectancy",
                     color_continuous_scale="Viridis",
                     hover_name="Country",
                     hover_data={"GDP per Capita": ":.2f", "Population": ":,", "Life Expectancy": ":.1f"},
                     title=f"💰 GDP per Capita & Life Expectancy - {continent} {year}")
    
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='DarkSlateGrey'),
            sizemode='diameter',
            opacity=0.8
        )
    )
    
    fig.update_layout(
        paper_bgcolor="#e5ecf6",
        height=700,
        xaxis=dict(
            title="Country",
            tickangle=45,
            tickfont=dict(size=10),
            gridcolor='lightgrey',
            gridwidth=0.5
        ),
        yaxis=dict(
            title="GDP per Capita ($)",
            gridcolor='lightgrey',
            gridwidth=0.5
        ),
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        title_font=dict(size=20, color="#2c3e50", family="Arial, sans-serif"),
        coloraxis_colorbar=dict(
            title="Life Expectancy",
            thickness=20,
            len=0.75
        )
    )
    
    return fig

def create_life_exp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="Life Expectancy", ascending=True)

    # 豪华水平条形图
    fig = px.bar(filtered_df, 
                 y="Country", 
                 x="Life Expectancy",
                 color="Life Expectancy",
                 color_continuous_scale="RdYlBu_r",
                 orientation='h',
                 hover_data={"GDP per Capita": ":.2f", "Population": ":,"},
                 title=f"❤️ Life Expectancy Ranking - {continent} {year}")
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white')
        ),
        hovertemplate="<b>%{y}</b><br>Life Expectancy: %{x:.1f} years<br>GDP per Capita: $%{customdata[0]:.2f}<br>Population: %{customdata[1]:,}<extra></extra>"
    )
    
    fig.update_layout(
        paper_bgcolor="#e5ecf6",
        height=700,
        xaxis=dict(
            title="Life Expectancy (Years)",
            gridcolor='lightgrey',
            gridwidth=0.5,
            range=[0, filtered_df['Life Expectancy'].max() * 1.1]
        ),
        yaxis=dict(
            title="Country",
            autorange="reversed"  # 最高值在顶部
        ),
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        title_font=dict(size=20, color="#2c3e50", family="Arial, sans-serif"),
        coloraxis_colorbar=dict(
            title="Years",
            thickness=20,
            len=0.75
        )
    )
    
    # 添加平均值线
    avg_life_exp = filtered_df['Life Expectancy'].mean()
    fig.add_vline(x=avg_life_exp, line_dash="dash", line_color="red", 
                  annotation_text=f"Average: {avg_life_exp:.1f}", 
                  annotation_position="top right")
    
    return fig

def create_choropleth_map(variable, year):
    filtered_df = gapminder_df[gapminder_df.Year==year]

    # 豪华等值线地图
    fig = px.choropleth(filtered_df, 
                        color=variable,
                        locations="ISO Alpha Country Code", 
                        locationmode="ISO-3",
                        color_continuous_scale="Plasma",
                        hover_name="Country",
                        hover_data={variable: ":.2f", "Continent": True},
                        title=f"🗺️ {variable} World Map - {year}",
                        projection="natural earth")

    fig.update_layout(
        dragmode=False, 
        paper_bgcolor="#e5ecf6", 
        height=700, 
        margin={"l":0, "r":0, "t":80, "b":0},
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)'
        ),
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        title_font=dict(size=20, color="#2c3e50", family="Arial, sans-serif")
    )
    
    return fig

##################### WIDGETS ####################################
continents = gapminder_df.Continent.unique()
years = gapminder_df.Year.unique()

cont_population = dcc.Dropdown(id="cont_pop", options=continents, value="Asia", clearable=False,
                              style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})
year_population = dcc.Dropdown(id="year_pop", options=years, value=1952, clearable=False,
                              style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})

cont_gdp = dcc.Dropdown(id="cont_gdp", options=continents, value="Asia", clearable=False,
                       style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})
year_gdp = dcc.Dropdown(id="year_gdp", options=years, value=1952, clearable=False,
                       style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})

cont_life_exp = dcc.Dropdown(id="cont_life_exp", options=continents, value="Asia", clearable=False,
                            style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})
year_life_exp = dcc.Dropdown(id="year_life_exp", options=years, value=1952, clearable=False,
                            style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})

year_map = dcc.Dropdown(id="year_map", options=years, value=1952, clearable=False,
                       style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})
var_map = dcc.Dropdown(id="var_map", options=["Population", "GDP per Capita", "Life Expectancy"],
                      value="Life Expectancy", clearable=False,
                      style={'borderRadius': '8px', 'border': '2px solid #2E86AB'})

##################### APP LAYOUT ####################################
app.layout = html.Div([
    html.Div([
        html.H1("🌍 Gapminder Data Visualization Dashboard", 
                className="text-center fw-bold m-2",
                style={'color': '#2E86AB', 'fontFamily': 'Arial, sans-serif', 'fontSize': '2.5rem'}),
        html.Br(),
        html.Div([
            # 左侧垂直选项卡
            html.Div([
                html.Button("📊 Dataset", id="dataset-tab", 
                           className="p-3 border-bottom tab-label w-100 text-start", 
                           n_clicks=0, 
                           style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                                  'border': 'none', 'cursor': 'pointer', 'color': 'white', 
                                  'fontWeight': 'bold', 'borderRadius': '0'}),
                html.Button("👥 Population", id="population-tab", 
                           className="p-3 border-bottom tab-label w-100 text-start", 
                           n_clicks=0,
                           style={'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 
                                  'border': 'none', 'cursor': 'pointer', 'color': 'white', 
                                  'fontWeight': 'bold', 'borderRadius': '0'}),
                html.Button("💰 GDP", id="gdp-tab", 
                           className="p-3 border-bottom tab-label w-100 text-start", 
                           n_clicks=0,
                           style={'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 
                                  'border': 'none', 'cursor': 'pointer', 'color': 'white', 
                                  'fontWeight': 'bold', 'borderRadius': '0'}),
                html.Button("❤️ Life Expectancy", id="life_expectancy-tab", 
                           className="p-3 border-bottom tab-label w-100 text-start", 
                           n_clicks=0,
                           style={'background': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', 
                                  'border': 'none', 'cursor': 'pointer', 'color': 'white', 
                                  'fontWeight': 'bold', 'borderRadius': '0'}),
                html.Button("🗺️ World Map", id="choropleth_map-tab", 
                           className="p-3 border-bottom tab-label w-100 text-start", 
                           n_clicks=0,
                           style={'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 
                                  'border': 'none', 'cursor': 'pointer', 'color': 'white', 
                                  'fontWeight': 'bold', 'borderRadius': '0'}),
            ], className="col-2", style={'border-right': '2px solid #dee2e6', 'height': '700px', 
                                       'background': '#f8f9fa', 'boxShadow': '2px 0 5px rgba(0,0,0,0.1)'}),
            
            # 右侧内容区域
            html.Div([
                # Dataset 内容
                html.Div([
                    html.Br(),
                    dcc.Graph(id="dataset", figure=create_table())
                ], id="dataset-content", className="tab-content"),
                
                # Population 内容
                html.Div([
                    html.Br(), 
                    html.Div(["🌍 Continent: ", cont_population, "   📅 Year: ", year_population], 
                            style={'padding': '10px', 'background': 'white', 'borderRadius': '10px', 
                                  'marginBottom': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    html.Br(),
                    dcc.Graph(id="population")
                ], id="population-content", className="tab-content", style={'display': 'none'}),
                
                # GDP Per Capita 内容
                html.Div([
                    html.Br(),
                    html.Div(["🌍 Continent: ", cont_gdp, "   📅 Year: ", year_gdp], 
                            style={'padding': '10px', 'background': 'white', 'borderRadius': '10px', 
                                  'marginBottom': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    html.Br(),
                    dcc.Graph(id="gdp")
                ], id="gdp-content", className="tab-content", style={'display': 'none'}),
                
                # Life Expectancy 内容
                html.Div([
                    html.Br(),
                    html.Div(["🌍 Continent: ", cont_life_exp, "   📅 Year: ", year_life_exp], 
                            style={'padding': '10px', 'background': 'white', 'borderRadius': '10px', 
                                  'marginBottom': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    html.Br(),
                    dcc.Graph(id="life_expectancy")
                ], id="life_expectancy-content", className="tab-content", style={'display': 'none'}),
                
                # Choropleth Map 内容
                html.Div([
                    html.Br(),
                    html.Div(["📊 Variable: ", var_map, "   📅 Year: ", year_map], 
                            style={'padding': '10px', 'background': 'white', 'borderRadius': '10px', 
                                  'marginBottom': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    html.Br(),
                    dcc.Graph(id="choropleth_map")
                ], id="choropleth_map-content", className="tab-content", style={'display': 'none'}),
            ], className="col-10", style={'padding': '20px'})
        ], className="row", style={'minHeight': '700px'})
    ], className="col-12"),
], style={"background": "linear-gradient(135deg, #e5ecf6 0%, #f8f9fa 100%)", "minHeight": "100vh", "padding": "20px"})

# 回调部分保持不变...
##################### CALLBACKS ####################################
# 选项卡切换回调
@app.callback(
    [Output(f"{tab}-content", "style") for tab in ["dataset", "population", "gdp", "life_expectancy", "choropleth_map"]],
    [Input(f"{tab}-tab", "n_clicks") for tab in ["dataset", "population", "gdp", "life_expectancy", "choropleth_map"]]
)
def switch_tab(dataset_clicks, population_clicks, gdp_clicks, life_clicks, map_clicks):
    from dash import callback_context
    ctx = callback_context
    if not ctx.triggered:
        return [{'display': 'block'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]
    
    tab_id = ctx.triggered[0]['prop_id'].split('.')[0].replace('-tab', '')
    styles = []
    for tab in ["dataset", "population", "gdp", "life_expectancy", "choropleth_map"]:
        if tab == tab_id:
            styles.append({'display': 'block'})
        else:
            styles.append({'display': 'none'})
    return styles

# 原有图表更新回调
@callback(Output("population", "figure"), [Input("cont_pop", "value"), Input("year_pop", "value")])
def update_population_chart(continent, year):
    return create_population_chart(continent, year)

@callback(Output("gdp", "figure"), [Input("cont_gdp", "value"), Input("year_gdp", "value")])
def update_gdp_chart(continent, year):
    return create_gdp_chart(continent, year)

@callback(Output("life_expectancy", "figure"), [Input("cont_life_exp", "value"), Input("year_life_exp", "value")])
def update_life_exp_chart(continent, year):
    return create_life_exp_chart(continent, year)

@callback(Output("choropleth_map", "figure"), [Input("var_map", "value"), Input("year_map", "value")])
def update_map(var_map, year):
    return create_choropleth_map(var_map, year)

if __name__ == "__main__":
    app.run(debug=True)