
# coding: utf-8

# # Final Project
# 
# Create a Dashboard taking data from [Eurostat, GDP and main components (output, expenditure and income)](http://ec.europa.eu/eurostat/web/products-datasets/-/nama_10_gdp). 
# The dashboard will have two graphs: 
# 
# * The first one will be a scatterplot with two DropDown boxes for the different indicators. It will have also a slide for the different years in the data. 
# * The other graph will be a line chart with two DropDown boxes, one for the country and the other for selecting one of the indicators. (hint use Scatter object using mode = 'lines' [(more here)](https://plot.ly/python/line-charts/) 

# In[4]:


## 1. Import all relevant libraries 

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

## 2. Initialize the Dash app

app = dash.Dash(__name__)
server = app.server
    
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

## 3. Read data and drop unnecessary rows 

df = pd.read_csv('nama_10_gdp_1_Data.csv')
df=df[df['UNIT']=="Current prices, million euro"] # Filter for unit which is'current prices..', because we dont want to have the other values (how do we know that?)
print(df.head())
euro=[]
for country in df['GEO']:
    if 'euro' in country.lower():
        euro.append(False)
    else:
        euro.append(True)
df=df[euro]
## 4. Set value for all indicators which are the x and y values and GEOS as the input variable (?)

indicators = df['NA_ITEM'].unique() # Indicators are the values we can choose from in the drop down and unique eliminates duplicates
GEOS=df['GEO'].unique() # Not filtering (?) but dropping duplicates 
app.layout = html.Div([ # Start working on the layout from top to bottom and from left to right
    
## 5. Start defining the layout
    
    html.Div([ # Upper part of the window
        html.Div([ 
            dcc.Dropdown( # First dropdown in first row
                id='1_xaxis', # Give it a unique id to avoid layovers in the graphic
                options=[{'label': i, 'value': i} for i in indicators], # Dictionary that shows label and value are equal, it could be that we want to use abbreviations or similar 
                value='Gross domestic product at market prices' # Taken from the csv file, do I always just take the first one(?) 
            ),
            
        ],
        style={'width': '48%', 'display': 'inline-block'}), # Placement of the dropdown menu, takes up almost half of the window, inline block means that its next to each other (?) 

        html.Div([ 
            dcc.Dropdown( # Second dropdown in first row
                id='1_yaxis', 
                options=[{'label': i, 'value': i} for i in indicators],
                value='Value added, gross'
            ),
            
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}) # Float right to avoid overlap
    ]),

    dcc.Graph(id='1_graph'), # Graph occupiyng the complete second row is created, data not yet displayed as it is not static and is defined by @app.callback

    dcc.Slider( # Slider in row three 
        id='year_slider',
        min=df['TIME'].min(), # Minimum value filter for the time value and select min
        max=df['TIME'].max(), # Minimum value filter for the time value and select max
        value=df['TIME'].max(), # Defines the value to start off with, not necessarily needed
        step=None, # Only makes it possible to choose the suggested values
        marks={str(year): str(year) for year in df['TIME'].unique()} # Marks are the values that can be selected which are the years to be found in the time column (they obviously need to be unqiue)
    ),

    
html.H1('\n'), # Creates a space in between the rows which makes the year value visible
    
    html.Div([ # Bottom part of the window whith one dropdown with indicators and one with countries, no slider necessary
        html.Div([
            dcc.Dropdown(
                id='2_xaxis',
                options=[{'label': i, 'value': i} for i in GEOS],
                value='Belgium'
            ),
            
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='2_yaxis',
                options=[{'label': i, 'value': i} for i in indicators],
                value='Gross domestic product at market prices'
            ),
            
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    dcc.Graph(id='2_graph') # Create a second graph
    
])

## 6. Start defining the interactivity 

@app.callback(
    dash.dependencies.Output('1_graph', 'figure'), # ('where to plot the data', 'what to plot') (?) / How do we know that this is about the countries?
    
    [dash.dependencies.Input('1_xaxis', 'value'), # Three input values, none of these is static (?)
     dash.dependencies.Input('1_yaxis', 'value'),
     dash.dependencies.Input('year_slider', 'value')])

def update_graph(xaxis_value_1, yaxis_value_1, # Define the functions' input with variables you just make up yourself, its constantly updated
                 year_value):
    dff = df[df['TIME'] == year_value] # Define what year_value is 
    
    return {
        'data': [go.Scatter( # Create a scatterplot, why do we call it data, we dont use it later (?)
            x=dff[(dff['NA_ITEM'] == xaxis_value_1) &( dff['GEO']==str(i) )]['Value'],
            y=dff[(dff['NA_ITEM'] == yaxis_value_1) &( dff['GEO']==str(i))]['Value'],
            text=dff[dff['GEO']==str(i)]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i[:20]
            
        )for i in dff.GEO.unique()
                ],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_value_1,
                'type': 'linear' 
            },
            yaxis={
                'title': yaxis_value_1,
                'type': 'linear' 
            },
            margin={'l': 60, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('2_graph', 'figure'),
    
    [dash.dependencies.Input('2_xaxis', 'value'),
     dash.dependencies.Input('2_yaxis', 'value')])

def update_graph_b(xaxis_value_2, yaxis_value_2):
    dff = df[df['GEO'] == xaxis_value_2]
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == yaxis_value_2]['TIME'],
            y=dff[dff['NA_ITEM'] == yaxis_value_2]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_value_2]['Value'],
            mode='lines'
            
            
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'YEAR',
                'type': 'linear' 
            },
            yaxis={
                'title': yaxis_value_2,
                'type': 'linear' 
            },
            margin={'l': 60, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

## 7. Make it run 

if __name__ == '__main__':
    app.run_server()

