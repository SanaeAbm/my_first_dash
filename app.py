import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
import pandas as pd
import plotly.express as px
import json

df_url = 'https://forge.scilab.org/index.php/p/rdataset/source/file/master/csv/ggplot2/msleep.csv'
df = pd.read_csv(df_url).dropna(subset=['vore'])

df_cols = [{"name": i, "id": i} for i in df.columns]
df_vore = df['vore'].sort_values().unique()
opt_vore = [{'label': x + 'vore', 'value': x} for x in df_vore]
col_vore = {x:px.colors.qualitative.Pastel[i] for i, x in enumerate(df_vore)}

min_bodywt = min(df["bodywt"].dropna()) 
max_bodywt = max(df["bodywt"].dropna()) 
step_bodywt = (max_bodywt - min_bodywt)/10

app = dash.Dash(__name__, title="Dash App")

markdown_text = '''
## Some references
- [Dash HTML Components](dash.plotly.com/dash-html-components)
- [Dash Core Components](dash.plotly.com/dash-core-components)  
- [Dash Bootstrap Components](dash-bootstrap-components.opensource.faculty.ai/docs/components)  
'''

table_tab = html.Div([
    dt.DataTable(id="my_table",
        columns = df_cols,
        data= df.to_dict("records")
    ),
    dcc.Graph(id="my_boxplot",
        figure= px.box(df,
            y="bodywt",
            color="vore",
            color_discrete_map= col_vore)
    )
])

graph_tab = html.Div([
    dcc.Graph(id="my_graph",
        figure= px.scatter(df,
            x="bodywt",
            y="sleep_total",
            color="vore",
            color_discrete_map= col_vore)
    ),
    dt.DataTable(id="selected_data",
        columns = df_cols
    )
])

app.layout = html.Div([
    html.Div([
        html.H1(app.title, className= "app-header--title")
    ], className= "app-header"),
    html.Div([
        dcc.Markdown(markdown_text),
        html.Label(["Select types of feeding strategies:",
            dcc.Dropdown('my-dropdown',
                options= opt_vore,
                value= [df_vore[0]],
                multi= True
            )
        ]),
        html.Div(id="data", style={'display':'none'}),
        dcc.RangeSlider(id="range",
            min=min_bodywt,
            max=max_bodywt,
            step=step_bodywt,
            marks={min_bodywt + i * step_bodywt: '{}'.format(round(min_bodywt + i * step_bodywt,2)) for i in range(10)},
            value=[min_bodywt, max_bodywt]
        ),
        dcc.Tabs(id="tabs", value='tab-t', children=[
            dcc.Tab(label='Table', value='tab-t'),
            dcc.Tab(label='Graph', value='tab-g'),
        ]),
        html.Div(id="tabs-content")
    ], className = "app-body")
])


@app.callback(
     Output('my_table', 'data'),
     Output('my_boxplot', 'figure'),
     Input('data', 'children'),
     State('tabs','value'))
def update_table(data, tab):
    if tab != 'tab-t':
        return None
    dff = pd.read_json(data)
    return dff.to_dict("records"), px.box(dff, y="sleep_total", custom_data=["name"], color="vore", color_discrete_map= col_vore)

@app.callback(
     Output('my_graph', 'figure'),
     Input('data', 'children'),
     State('tabs','value'))
def update_figure(data, tab):
    if tab != 'tab-g':
        return None
    dff = pd.read_json(data)
    return px.scatter(dff, x="bodywt", y="sleep_total", custom_data=["name"], color="vore", color_discrete_map= col_vore)

@app.callback(
    Output('selected_data', 'data'),
    Input('my_graph', 'selectedData'))
def display_selected_data(selectedData):
    if selectedData is None:
        return None
    names = [o["customdata"][0] for o in selectedData["points"]]
    filter = df['name'].isin(names)
    return df[filter].to_dict("records")

@app.callback(
     Output('data', 'children'),
     Input('range', 'value'),
     Input('my-dropdown', 'value'))
def update_data(range, values):
    filter = df['vore'].isin(values) & df['bodywt'].between(range[0], range[1])
    return df[filter].to_json()

@app.callback(
     Output('tabs-content', 'children'),
     Input('tabs', 'value'))
def update_tabs(v):
    if v == 'tab-g':
        return graph_tab
    return table_tab

if __name__ == '__main__':
    app.server.run(debug=True)
