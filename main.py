import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np

app = Dash(__name__)

df1 = pd.read_csv("Bee-Colony-Loss.csv")
# Need to have state_code for my graph which is missing from dataset. So mapping in new dataframe.
df2 = pd.read_csv("usa_states2.csv")

# ------ Data cleaning and data wrangling ---------
mapping = dict(zip(df2['state_name'], df2['state_code']))
df1['state_code'] = ""

for row in df1.iterrows():
    for state_name, state_code in mapping.items():
        if row[1]['state'] == state_name:
            df1.at[row[0], 'state_code'] = state_code

mydf = df1.copy()
mydf = mydf[mydf['percentage_total_annual_loss'].notna()]
mydf[mydf.columns[3]] = mydf[mydf.columns[3]].replace('[\$%,]', '', regex=True).astype(float)
mydf = mydf.groupby(['state', 'census_region_1', 'year', 'state_code'])[
    ['percentage_total_annual_loss', 'beekeepers', 'colonies']].mean()
mydf.reset_index(inplace=True)

# ------------ App layout -----------------------
app.layout = html.Div([
    html.H1('*** SAVE THE BEES ***', style={'text-align': 'center', 'color': 'Red'}),
    html.Br(),
    html.H3('MA705 Individual Project | Monika Meshram', style={'text-align': 'left', 'color': 'Navy', 'fontSize': 25}),
    html.H3('Introduction:', style={'text-align': 'left', 'color': 'Navy', 'fontSize': 20}),
    html.Header('Honey bees, both wild and domestic, perform roughly more than 70% of all pollination worldwide.'
                ' Everday, a single bee colony can pollinate 300 million flowers. Grains are pollinated primarily by wind,'
                ' but nuts, fruits, and vegetables are pollinated by bees. Bees pollinate 70 of the top 100 human food crops,'
                ' which supply around more than 85% of the worlds nutrition. Be the solution to assiting in the protection of bees'
                ' in crisis. And protect our pollinators from extinction.'),
    html.H3('What is this dashboard about ?', style={'text-align': 'left', 'color': 'Navy', 'fontSize': 20}),
    html.Header('This interactive dashboard displays information about Beekeeping (Apiculture),'
           ' which is maintenance of bee colonies, commonly in man-made hives. It offers visualization of loss'
           ' of bee colonies as a focus. User can choose reported annual period and region(s) to'
           ' visualize the annual percentage loss of bee colonies and also number of beekeepers'
           ' and colonies statistics per year and state-wise. There may be many reasons for the'
           ' loss like diseases in bees, finance and maintenance problem etc. which is'
           ' out-of-scope of this visualization dashboard.'),
    html.H5(' Note: For the protection of privacy, losses were reported as N/A if 10 or fewer' 
            ' beekeepers responded in that state and thus are ignored in displayed.'),

    dcc.Dropdown(id='select_year',
                 options=[{'label': yr, 'value': yr} for yr in sorted(mydf.year.unique())],
                 multi=False,
                 value='2016/17',
                 style={'width': '50%'}
                 ),
    html.Br(),
    dcc.Dropdown(id="select_region",
                 options=[{'label': x, 'value': x} for x in sorted(mydf.census_region_1.unique())],
                 multi=True,
                 value=mydf.census_region_1.unique(),
                 style={'width': "50%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='mymap', figure={}),
    html.Br(),

    html.Div([dcc.Graph(id='myline1')]),
    html.Br(),

    html.Div([dcc.Graph(id='myline2')]),

    html.H3('References:', style={'text-align': 'left', 'color': 'Navy', 'fontSize': 20}),
    html.P(['Here is a list of data sources and references used in this course project:',
            html.Br(),
            html.Label(['- Bee Colony Loss information: ',
                        html.A('https://data.world/finley/bee-colony-statistical-data-from-1987-2017',
                               href='https://data.world/finley/bee-colony-statistical-data-from-1987-2017')]),
            html.Br(),
            html.Label(['- USA state code: ',
                        html.A('https://www.kaggle.com/datasets/corochann/usa-state-code',
                               href='https://www.kaggle.com/datasets/corochann/usa-state-code')]),
            html.Br(),
            html.Label(['- Dash Plotly Callbacks: ',
                        html.A('https://dash.plotly.com/datatable/callbacks',
                               href='https://dash.plotly.com/datatable/callbacks')]),
            html.Br(),
            html.Label(['- Dash Plotly Choropleth maps: ',
                        html.A('https://plotly.com/python/choropleth-maps',
                               href='https://plotly.com/python/choropleth-maps')]),
            html.Br(),
            html.Label(['- Dash Plotly Line charts: ',
                        html.A('https://plotly.com/python/line-charts',
                               href='https://plotly.com/python/line-charts')])
            ]),
    html.H3('May 2022 | Monika Meshram', style={'text-align': 'left', 'color': 'Navy', 'fontSize': 15}),

])

# ---------------- Callback for the app --------------------------


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='mymap', component_property='figure'),
     Output(component_id='myline1', component_property='figure'),
     Output(component_id='myline2', component_property='figure')],
    [Input(component_id='select_year', component_property='value'),
     [Input(component_id='select_region', component_property='value')]])
def update_graph(select_year, select_region):
    # By default selected period is 2016/17 and all regions
    select_region = list(np.concatenate([select_region]).flat)

    container = 'You have chosen year : {} for region(s) : {}'.format(select_year, select_region)

    dff = mydf.copy()
    dff = dff[dff['year'] == select_year]
    print(f'User have chosen year: {select_year}')
    if len(select_region) > 0:
        print(f'User have chosen region: {select_region}')
        dff = dff[dff['census_region_1'].isin(select_region)]
    elif len(select_region) == 0:
        dff = dff[dff['census_region_1'].isin([''])]
    else:
        dff = dff[dff['census_region_1'].isin(['Northeast'])]

    # Choropleth graph
    fig1 = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope='usa',
        color='percentage_total_annual_loss',
        hover_data=['state', 'percentage_total_annual_loss'],
        color_continuous_scale='Reds',
        labels={'percentage_total_annual_loss': '% of Bee Colonies Loss'},
        template='plotly_dark'
    )
    fig1.update_layout(
        title_text="Bee Colonies Loss in USA",
        title_xanchor="center",
        title_font=dict(size=25),
        title_x=0.5,
        geo=dict(scope='usa'),
    )

    # Line Graph1
    fig2 = px.line(dff, y='colonies', x='state', height=400)
    fig2.update_layout(yaxis={'title': 'Number of Colonies'},
                       title={'text': 'Bee Colonies in USA',
                              'font': {'size': 25}, 'x': 0.5, 'xanchor': 'center'})

    # Line Graph2
    fig3 = px.line(dff, y='beekeepers', x='state', height=400)
    fig3.update_layout(yaxis={'title': 'Number of Beekeepers'},
                       title={'text': 'Beekeepers in USA',
                              'font': {'size': 25}, 'x': 0.5, 'xanchor': 'center'})

    return container, fig1, fig2, fig3

# ------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)
