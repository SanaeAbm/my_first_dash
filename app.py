import dash
from dash.dependencies import Input, Output, State

import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
import pandas as pd
import numpy as np
import plotly.express as px
import json



df_url = 'https://forge.scilab.org/index.php/p/rdataset/source/file/master/csv/ggplot2/msleep.csv'
df = pd.read_csv(df_url)
df = pd.read_csv(df_url).dropna(subset = ['vore'])


df_vore = df['vore'].sort_values().unique()
opt_vore = [{'label': x + 'vore', 'value': x} for x in df_vore]
col_vore = {}
for i, x in enumerate(df_vore):
    col_vore[x]= px.colors.qualitative.G10[i]

min_bodywt = min(df['bodywt'].dropna())
max_bodywt = max(df['bodywt'].dropna())





app = dash.Dash(__name__, title="My first Dash Python App")


markdown_text = '''
### Some references
- [Dash HTML Components](https://dash.plotly.com/dash-html-components)
- [Dash Core Components](https://dash.plotly.com/dash-core-components)  
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/)  
'''


def slider_map(min, max, steps=10):
    scale = np.logspace(np.log10(min), np.log10(max), steps, endpoint=False)
    return {i/10: '{}'.format(round(scale[i],2)) for i in range(steps)}


table_tab= dt.DataTable(
                id='my-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data= df.to_dict("records")
        )

graph_tab = dcc.Graph(id="my-graph", 
            figure= px.scatter(df,
            x="bodywt",
            y="sleep_total",
            color="vore",
            color_discrete_map=col_vore))

app.layout = html.Div([
    html.Div([html.H1(app.title,className="app-header-title")],
    className="app-header",
    ),
    html.Div([
       dcc.Markdown(markdown_text),
       html.Label(["Select types of feeding strategies:", 
         dcc.Dropdown('my-dropdown',
            options= opt_vore, 
            value= [opt_vore[0]['value']],
            multi=True
        )
    ]),

    html.Label(["Range of values for body weight:", 
                 dcc.RangeSlider(
                     id="range",
                     max=1,
                     min= 0,
                     step= 1/100,
                     marks= slider_map(min_bodywt, max_bodywt),
                     value= [0,1],
                 )
    ]),
     
    html.Div(id="data", style={'display':'none', "backgroundColor":"yellow"}),
    html.Div(id='dataRange', style={'display': 'none'}),
    dcc.Tabs(id="tabs", value='tab-t', children=[
            dcc.Tab(label='Table', value='tab-t'),
            dcc.Tab(label='Graph', value='tab-g'),
        ]),
    
    html.Div(id='tabs-content')
    ],
   className= "app-body")

    ])


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-t':
        return table_tab
    elif tab == 'tab-g':
        return graph_tab

@app.callback(
     Output('my-table', 'data'),
     Input('data', 'children'), 
     State('tabs', 'value'))
def update_table(data, tab):
    if tab != 'tab-t':
        return None
    dff = pd.read_json(data, orient='split')
    return dff.to_dict("records")

@app.callback(
     Output('my-graph', 'figure'),
     Input('my-dropdown', 'value'),
     State('tabs', 'value'))

def update_graph(data, tab):
    if tab != 'tab-g':
        return None
    dff = pd.read_json(data, orient='split')
    return px.scatter(dff, x="bodywt", y="sleep_total", color="vore",
    #color_discrete_sequence=px.colors.qualitative.G10
    color_discrete_map=col_vore)

@app.callback(Output('data', 'children'), 
    Input('range', 'value'), 
    State('my-dropdown', 'value'))
def filter(range, values):
     filter = df['vore'].isin(values) & df['bodywt'].between(min_bodywt * (max_bodywt/min_bodywt) ** range[0], min_bodywt * (max_bodywt/min_bodywt) ** range[1])

     # more generally, this line would be
     # json.dumps(cleaned_df)
     return df[filter].to_json(date_format='iso', orient='split')


@app.callback(Output('dataRange', 'children'), 
    Input('my-dropdown', 'value'))
def dataRange(values):
    filter = df['vore'].isin(values) 
    dff = df[filter]
    min_bodywt = min(dff['bodywt'].dropna())
    max_bodywt = max(dff['bodywt'].dropna())
    return json.dumps({'min_bodywt': min_bodywt, 'max_bodywt': max_bodywt})











if __name__ == '__main__':
    app.server.run(debug=True)
