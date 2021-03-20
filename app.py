import dash
from dash.dependencies import Input, Output, State

import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
import pandas as pd


df_url = 'https://forge.scilab.org/index.php/p/rdataset/source/file/master/csv/ggplot2/msleep.csv'
df = pd.read_csv(df_url)

df_vore = df['vore'].dropna().sort_values().unique()
opt_vore = [{'label': x + 'vore', 'value': x} for x in df_vore]

colors = {
     'background': '#7FDBFF',
     'text': '#745D34',
     'special': 'purple'
 }




app = dash.Dash(__name__, title="My first Dash Python App")


markdown_text = '''
### Some references
- [Dash HTML Components](https://dash.plotly.com/dash-html-components)
- [Dash Core Components](https://dash.plotly.com/dash-core-components)  
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/)  
'''

app.layout = html.Div([
    html.Div([html.H1(app.title,className="app-header-title")],
    className="app-header"),
    html.Div([
    dcc.Markdown(markdown_text),
    html.Label(["Select types of feeding strategies:", 
       dcc.Dropdown('my-dropdown',
            options= opt_vore, 
            value= [opt_vore[0]['value']],
            multi=True
        )
    ]),
    dt.DataTable(
        id='my-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data= df.to_dict("records")
        )
     ], className= "app-body")
    ])

 




@app.callback(
     Output('my-table', 'data'),
     Input('my-dropdown', 'value'))
def update_data(values):
    filter = df['vore'].isin(values)
    return df[filter].to_dict("records")

if __name__ == '__main__':
    app.server.run(debug=True)
