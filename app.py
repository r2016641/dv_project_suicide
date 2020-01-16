import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
# INTERATIVE MAP
import plotly.express as px
import numpy as np
from dash import Dash
from dash.dependencies import Input, Output, State
from plotly.offline import init_notebook_mode, iplot
from IPython.display import display, HTML

######## DATASET IMPORT #######
from matplotlib import ticker


def import_data(path, extension):
    if extension == 'csv':
        df = pd.read_csv(path)
        return df
    elif extension == 'xlsx':
        df = pd.read_excel(path)
        return df


dataworld = import_data('annual-number-of-deaths-by-cause.csv', 'csv')
path_continents = 'continents_.xlsx'
continents = import_data(path_continents, 'xlsx')
continents = continents.rename(columns={'ISO3v10': 'Code'})
spyear_path = 'suicide-rates-by-age-detailed.csv'
deathrate_path = 'suicide-death-rates.csv'
suicidesex_path = 'suicide-death-rates-by-sex.csv'
path_fire = 'suicide-rate-by-firearm.csv'
pop = 'API_SP.POP.TOTL_DS2_en_excel_v2_713231.xls'

########### PRE-PROCESSING #########
# Delete duplicates
def drop_dupl(dataframe):
    df = dataframe.drop_duplicates()
    return df

drop_dupl(dataworld)
dataworld.isnull().sum(axis=0)
dataworld.drop('Execution', axis=1, inplace=True)

def missing(dataframe):
    dataframe['Countnan'] = dataframe.apply(lambda x: x.count(), axis=1)
    return dataframe

# Delete row with more than 3 null/nan values
def delete_rows(dataframe):
    indexnames = dataframe[dataframe['Countnan'] <= 30].index
    dataframe.drop(indexnames, inplace=True)
    dataframe.reset_index(drop=True, inplace=True)
    return dataframe


dataworld = missing(dataworld)
dataworld = delete_rows(dataworld)

# Delete the column created to count the null values
def delete_countnan(dataframe):
    df = dataframe.drop('Countnan', 1)
    return df

dataworld = delete_countnan(dataworld)

def nan_por_zero(dataframe):
    value = 0
    for i, col in enumerate(dataframe):
        dataframe.iloc[:, i] = dataframe.iloc[:, i].fillna(value)
    return dataframe


dataworld = nan_por_zero(dataworld)
dataworld.iloc[:, 2:36] = dataworld.iloc[:, 2:36].astype(int)
dataworld['Suicide (deaths)'].describe()

# Merge the Continents dataframe with the the dataset that is being treated, so that the rows that don't
# belong to countries are automatically deleted
def continent(dataframe, continents):
    dataframe = pd.DataFrame.merge(dataframe, continents, on='Code')
    return dataframe


dataworld = continent(dataworld, continents)
dataworld.drop('CountryEnglish', axis=1, inplace=True)
dataworld.drop('ContinentName', axis=1, inplace=True)


spyear = import_data(spyear_path, 'csv')
spyear = nan_por_zero(spyear)
spyear = continent(spyear, continents)
spyear.drop('CountryEnglish', axis=1, inplace=True)
spyear.drop('ContinentName', axis=1, inplace=True)
spyear = spyear[spyear['Entity'] == 'Portugal']

deathrate = import_data(deathrate_path, 'csv')
drop_dupl(deathrate)
def delete_rows_rate(dataframe):
    indexnames = dataframe[dataframe['Countnan'] <= 1].index
    dataframe.drop(indexnames, inplace=True)
    dataframe.reset_index(drop=True, inplace=True)
    return dataframe
deathrate = missing(deathrate)
deathrate = delete_rows_rate(deathrate)

deathrate = delete_countnan(deathrate)
deathrate = nan_por_zero(deathrate)

deathrate = continent(deathrate, continents)
deathrate.columns = ['Country','Code','Year','Suicide_rate','CountryEnglish','ContinentName']

actual = pd.DataFrame(deathrate.loc[deathrate['Year'] == 2017])

old = pd.DataFrame(deathrate.loc[deathrate['Year'] == 1990])
suicide_rate = pd.merge(actual, old[["Code", "Suicide_rate", "Year"]], on="Code", how="left")
suicide_rate.columns = ['Country', 'Code', 'Year_x', 'Suicide_rate_2017','CountryEnglish','ContinentName', 'Suicide_rate_1990', 'Year_y',]



suicidesex = import_data(suicidesex_path , 'csv')
drop_dupl(suicidesex)
suicidesex = missing(suicidesex)
suicidesex = delete_rows_rate(suicidesex)

suicidesex = delete_countnan(suicidesex)
suicidesex = nan_por_zero(suicidesex)
suicidesex.columns = ['Entity','Code','Year','Female','Male','Both']
suicidesex = continent(suicidesex, continents)
suicidesex.drop('CountryEnglish', axis=1, inplace=True)
suicidesex.drop('ContinentName', axis=1, inplace=True)

available_indicator = []
for i in suicidesex['Entity']:
    if i not in available_indicator:
        available_indicator.append(i)
suicidesex = pd.melt(suicidesex, id_vars = ['Entity', 'Code', 'Year'], value_vars= ['Female', 'Male'])
print(suicidesex)

portugaldf= pd.DataFrame(dataworld.loc[dataworld['Entity'] == 'Portugal'])
portugaldf.set_index('Entity', inplace=True)
pt = portugaldf[['Year','Cardiovascular diseases (deaths)','Cancers (deaths)','Dementia (deaths)', 'Lower respiratory infections (deaths)', 'Respiratory diseases (deaths)'
,'Digestive diseases (deaths)', 'Diabetes (deaths)', 'Kidney disease (deaths)', 'Liver diseases (deaths)', 'Suicide (deaths)',
'Parkinson disease (deaths)', 'Road injuries (deaths)', 'HIV/AIDS (deaths)','Alcohol use disorders (deaths)']].copy()

pt.columns =['Year','Cardiovascular diseases','Cancers', 'Dementia', 'Lower respiratory infections', 'Respiratory diseases ', 'Digestive diseases',
     'Diabetes', 'Kidney disease','Liver diseases','Suicide','Parkinson diseases','Road injuries','HIV/AIDS','Alcohol use disorders']



init_notebook_mode(connected = True)




fire = import_data(path_fire, 'csv')

def delete_rows_1(dataframe):
    indexnames = dataframe[dataframe['Countnan'] <= 1].index
    dataframe.drop(indexnames, inplace=True)
    dataframe.reset_index(drop=True, inplace=True)
    return dataframe

fire = missing(fire)
fire = delete_rows_1(fire)

fire = delete_countnan(fire)
fire = nan_por_zero(fire)

fire = continent(fire, continents)
fire.columns = ['Country','Code','Year','Firearm_rate','CountryEnglish','ContinentName']


dataaa = pd.concat([fire[['Country','Code','Year','Firearm_rate','ContinentName']],deathrate['Suicide_rate']], axis=1, ignore_index=True)

dataaa.columns = ['Country','Code','Year','Firearm_rate','Continent', 'Suicide_rate']


pop = import_data(pop, 'xlsx')

pop = pop.rename(columns={'Country Code': 'Code'})


pop = continent(pop, continents)

pop = pd.melt(pop, id_vars=['Country Name','Code','CountryEnglish','ContinentName'], value_vars=['1990', '1991','1992','1993','1994', '1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005', '2006', '2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017'])

pop = pop.rename(columns={'variable': 'Year'})

poped = pd.merge(dataaa, pop[['Code','value','Year']], on = ['Code'], how='inner')
poped['eee'] = np.where(poped.Year_x == poped.Year_y.astype(int), 'True', 'False')
poped.drop(poped[poped['eee'] == 'False'].index, inplace = True)

poped['Continent'].replace(to_replace ="Europe ",
                 value ="Europe", inplace=True)

poped = poped.rename(columns={'value': 'Population'})

df = px.data.gapminder()

firearm = px.scatter(poped, x="Firearm_rate", y="Suicide_rate", animation_frame="Year_x", animation_group="Country",
           size="Population", color="Continent", hover_name="Country",color_discrete_sequence= [ '#7f9900', '#63175a' , '#992362', '#d95153', '#ed825d',' #f7b880']
                     )


######################################### APP ############################################################
#external_stylesheets = ['https://r2016641.github.io/dark.css']
#external_stylesheets = external_stylesheets
app: Dash = dash.Dash(__name__)

server = app.server

## PLOT 1 ##

fig = px.choropleth(deathrate, locations='Code',
                    color='Suicide_rate',
                    hover_name='Year',
                    animation_frame='Year',
                    color_continuous_scale= px.colors.cmocean.matter,
                    projection="natural earth"
#[ '#CCFF99', '#CCFF33', '#99CC00', '#669900', '#336600', '#003300']
#px.colors.cmocean.amp
#px.colors.sequential.YlOrRd
)
fig_comp = px.scatter(suicide_rate, x='Suicide_rate_2017',
                      y='Suicide_rate_1990',
                      hover_data=['Country'], color_discrete_sequence= [ '#f08e62','#7f9900', '#63175a' , '#992362', '#d95153', '#ed825d',' #f7b880'],

)
fig_comp.update_traces(marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': '#111'},
                'color' : '#f08e62'
            },)

fig_comp.add_trace(
    go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=False
    )
)

#c76675, #edb7bc, #f2dadb , #f2f2ea,#aecdc4
#'#8cac90','#c8d7ca','#ddd4d3','#d7909b','#a0344e'
#'#a0344e','#d7909b','#ddd4d3','#c8d7ca','#8cac90'
# The App itself
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H1(children = "DATA VISUALIZATION PROJECT | Suicide Around the world",
                            style={
                                'textAlign': 'left',
                                  'color': '#fff',
                                 'font-family': 'sans-serif',
                                'padding': '10px',
                                'backgroundColor': '#111'
                            }),
                    html.H3(children="")
                ],
            ),
        ],
    )
colors = {
    'background': '#111',
    'text': '#ffffff'
}
tabs_styles = {
    'height': '51px'
}
tab_style = {
    'borderTop': '1px solid #fff',
    'borderBottom': '1px solid ',
    'fontWeight': 'bold',
    'color': '#fff',
    'backgroundColor': '#111',
    'font-family':'sans-serif', 'padding' : '10px'

}

tab_selected_style = {
    'borderTop': '1px solid',
    'borderBottom': '1px solid #fff',
    'backgroundColor': '#fff',
    'color': '#111',
    'font-family':'sans-serif',  'padding' : '10px'
}

app.layout = html.Div(style={'backgroundColor': '#111'},
    id="big-app-container",
    children=[html.Div(
        build_banner()),
        html.Div(style={'backgroundColor': '#fff', 'width': '100%', 'display': 'inline-block'},
            id="app-container",
            children=[
                # Main app
                html.Div(style={'backgroundColor': '#fff'},
                    id="app-content",
                    children = [dcc.Tabs(vertical = False, id="all-tabs-inline", value='tab-1', children=[
                            dcc.Tab(label='SUICIDE RATE AROUND THE WORLD', value='tab-1',
                                    style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='SUICIDE RATE BY GENDER', value='tab-2', style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='SUICIDE RATE COMPARATION', value='tab-3', style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='FIREARM SUICIDE RATE', value='tab-4', style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='CAUSES OF DEATH IN PORTUGAL', value='tab-5', style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='PORTUGAL SUICIDE RATES BY AGE', value='tab-6', style=tab_style,
                                    selected_style=tab_selected_style),
                        ], style=tabs_styles,
                                 colors={
                                     "border": "#6D6A75",
                                     "primary": "red",
                                     "background": '#fff'
                                 }),
                        html.Div(id='tabs-content')

                    ]

                ),


            ],
        ),
    ],
)

@app.callback(Output('tabs-content', 'children'),
              [Input("all-tabs-inline", 'value')])
def render_content(tab):
    if tab == 'tab-1':

        return html.Div([
           html.Div([
               html.Div(dcc.Graph(
                   id='example-graph',
                   figure=fig),
                   style={'width': '55%', 'display': 'inline-block', 'height': '190px', 'backgroundColor': '#fff'}
               ),
               html.Div(dcc.Markdown('## SUICIDE RATE AROUND THE WORLD'
                                     '\n\nSuicide, as expected, has a ripple effect that can affect not only family and friends but also entire societies and communities. Maybe this topic is underestimated but 800,000 people die from suicide every year and because of this information, we’ve decided to develop our project on this theme. '
                                     '\n\nDue to the fact that it´s still a "taboo" in many countries, the aim of this project is to explore **Suicide Rate**, possible causes and its distribution over the world. '
                                     '\n\nAs a group, we thought that it would be interesting or at least helpful to explore one of the leading causes of death globally with the data available in World Health Organization (WHO).'
                        )
                        ,style ={'width': '40%', 'display': 'inline-block', 'height': '190px', 'color' : '#111', 'font-family':'sans-serif', 'text-align': 'justify','vertical-align': 'middle', 'padding': '10px'}),
            ], style={'width': '100%', 'display': 'inline-block','backgroundColor': '#fff' })])

    elif tab == 'tab-2':
        return html.Div([html.Div(dcc.Markdown('\n ## SUICIDE RATE BY GENDER'), style ={ 'display': 'inline-block',  'color' : '#111', 'font-family':'sans-serif', 'padding' : '10px'}),
            html.Div([
            html.Div([
                dcc.Graph(
                    id='crossfilter-indicator-scatter',
                    hoverData={'points': [{'customdata': 'Portugal'}]}
                )
            ], style={'width': '49%', 'display': 'inline-block', 'padding': '10 px', 'borderTop' : '10px'}),
            html.Div([
                html.Div('\n\n\n\n'),
                dcc.Graph(id='x-time-series'),
                dcc.Graph(id='y-time-series'),
            ], style={'display': 'inline-block', 'width': '49%', 'padding': '5px', 'borderTop' : '10px'}),
        ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px'}),
            html.Div(dcc.Slider(
                id='crossfilter-year--slider',
                min=suicidesex['Year'].min(),
                max=suicidesex['Year'].max(),
                value=suicidesex['Year'].max(),
                marks={str(year) : str(year)  for year in suicidesex['Year'].unique()},
                step=None
            ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
        ])

    elif tab == 'tab-3':
        return html.Div([html.Div([html.Div(dcc.Markdown("\n\n ## SUICIDE RATE COMPARATION "
                                                         "\n\n This analysis lies on the comparison between suicide rate from 1990 and 2017. \n\n The purpose of this visualization is to evaluate if suicide rate is increasing or decreasing. The line represents the number of suicides that were equal on 1990 and 2017 (y=x). \n\n We can conclude that the majority of the country´s suicide rates are decreasing but also there is a few that keep on increasing. Reasons to this increase can be due to social media, domestic violence, depression, stress, bullying, mental health, economic matters, etc."),
                                            style={ 'width': '40%', 'display': 'inline-block', 'height': '190px', 'color' : '#111', 'font-family':'sans-serif', 'text-align': 'justify','vertical-align': 'middle', 'padding': '20px'}),
                                   html.Div(dcc.Graph(id='comparation',
                                                figure = fig_comp ),
                                            style={'width': '49%', 'display': 'inline-block', 'height': '190px',}
                    )], style={'width': '100%', 'display': 'inline-block', 'padding': '20px'})])
    elif tab == 'tab-4':
        return html.Div([html.Div(dcc.Markdown('\n ## FIREARM SUICIDE RATE'), style={ 'width': '40%', 'display': 'inline-block',  'color' : '#111', 'font-family':'sans-serif', 'text-align': 'justify','vertical-align': 'middle', 'padding': '20px'}),dcc.Graph(id='firearm',
                                figure = firearm )])
    elif tab == 'tab-5':
        years = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
                 '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015',
                 '2016', '2017']
        items = ['Cardiovascular diseases', 'Cancers', 'Dementia', 'Lower respiratory infections',
                 'Respiratory diseases ', 'Digestive diseases',
                 'Diabetes', 'Kidney disease', 'Liver diseases', 'Suicide', 'Parkinson diseases', 'Road injuries']
        count = pd.DataFrame(pt.iloc[:, 1:15].values.transpose())
        figure = {
            'data': [{
                'type': 'bar',
                'x': items,
                'y': count[0],
                'marker': {
                    'color': ['#7f9900', '#63175a', '#992362', '#d95153', '#ed825d', ' #f7b880', '#7f9900', '#63175a',
                              '#992362', '#d95153', '#ed825d', ' #f7b880', '#7f9900', '#63175a']
                }
            }],
            'layout': {
                'xaxis': {
                    'gridcolor': '#FFFFFF',
                    'linecolor': '#000',
                    'linewidth': 1,
                    'zeroline': False,
                    'autorange': True
                },
                'yaxis': {
                    'title': 'Number of deaths',
                    'gridcolor': '#FFFFFF',
                    'linecolor': '#000',
                    'linewidth': 1,
                    'range': [0, 50000],  # [0,5]
                    'autorange': False
                },
                'hovermode': 'closest',
                'updatemenus': [{
                    'type': 'buttons',
                    'buttons': [{
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {
                                'duration': 500,
                                'redraw': True
                            },
                            'fromcurrent': True,
                            'transition': {
                                'duration': 300,
                                'easing': 'quadratic-in-out'
                            }
                        }]
                    },

                    ],
                    'direction': 'left',
                    'pad': {
                        'r': 10,
                        't': 87
                    },
                    'showactive': False,
                    'type': 'buttons',
                    'x': 0.1,
                    'xanchor': 'right',
                    'y': 0,
                    'yanchor': 'top'
                }]
            },
            'frames': []
        }

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {
                    'size': 20
                },
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right',

            },
            'transition': {
                'duration': 300,
                'easing': 'cubic-in-out'
            },
            'pad': {
                'b': 10,
                't': 50
            },
            'len': 0.9,
            'x': 0.05,
            'y': -0.2,
            'steps': []
        }

        for index, year in enumerate(years):
            frame = {
                'data': [{
                    'type': 'bar',
                    'x': items,
                    'y': count[index]
                }],
                'name': str(year)
            }
            figure['frames'].append(frame)

            slider_step = {
                'args': [
                    [year],
                    {
                        'frame': {
                            'duration': 300,
                            'redraw': True
                        },
                        'mode': 'immediate',
                        'transition': {
                            'duration': 300
                        }
                    }
                ],
                'label': year,
                'method': 'animate'
            }
            sliders_dict['steps'].append(slider_step)

        figure['layout']['sliders'] = [sliders_dict]

        return html.Div([html.Div(dcc.Markdown('\n ## CAUSE OF DEATH IN PORTUGAL'), style={ 'width': '40%', 'display': 'inline-block', 'color' : '#111', 'font-family':'sans-serif', 'text-align': 'justify','vertical-align': 'middle', 'padding': '20px'}),
                         dcc.Graph(id='comparation',
                                figure = figure )])
    elif tab == 'tab-6':
        return html.Div([
            html.Div(
                html.Div([html.Div([dcc.Markdown("\n\n ## PORTUGAL SUICIDE RATE BY AGE \n\n")], style={ 'width': '40%', 'display': 'inline-block', 'color' : '#111', 'font-family':'sans-serif', 'text-align': 'justify','vertical-align': 'middle', 'padding': '20px'}),
                          html.Div([dcc.Dropdown(id="selected-value", multi=True,
                                                 value=["All ages (deaths per 100,000)"],
                                                 options=[{"label": "All Ages",
                                                           "value": "All ages (deaths per 100,000)"},
                                                          {"label": "5-14 Years",
                                                           "value": "5-14 years (deaths per 100,000)"},
                                                          {"label": "15-49 Years",
                                                           "value": "15-49 years (deaths per 100,000)"},
                                                          {"label": "50-69 Years",
                                                           "value": "50-69 years (deaths per 100,000)"},
                                                          {"label": "+70 Years",
                                                           "value": "70+ years (deaths per 100,000)"}])],
                                   className="row",
                                   style={"display": "block", "width": "70%", "margin-left": "auto",
                                          "margin-right": "auto", 'textAlign': 'center'}),
                          html.Div([dcc.Graph(id="my-graph", style= {'Align': 'center'})]),
                          html.Div(
                              [dcc.RangeSlider(id="year-range", min=1990, max=2017, step=1, value=[1990, 2017],
                                               marks={1990: str(1990), 1992: str(1992), 1994: str(1994),
                                                      1996: str(1996), 1998: str(1998), 2000: str(2000),
                                                      2002: str(2002), 2004: str(2004), 2006: str(2006),
                                                      2008: str(2008), 2010: str(2010), 2012: str(2012),
                                                      2014: str(2014), 2016: str(2016), 2017: str(2017)})])
                          ], className="ages"), style={'width': '90%', 'display': 'inline-block', 'padding ': '20px'})

        ])


app.config['suppress_callback_exceptions']=True
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('selected-value', 'value'), dash.dependencies.Input('year-range', 'value')])
def update_figure(selected, year):
    text = {"All ages (deaths per 100,000)": "All Ages",  "5-14 years (deaths per 100,000)": "5-14 Years",
            "15-49 years (deaths per 100,000)": "15-49 Years" , "50-69 years (deaths per 100,000)": "50-69 Years","70+ years (deaths per 100,000)": "70_Years" }
    dff = spyear[(spyear["Year"] >= year[0]) & (spyear["Year"] <= year[1])]
    print ('year',year)
    trace = []
    for type in selected:
        trace.append(go.Scatter(x=dff["Year"], y=dff[type], name=text[type], mode='lines',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}))
    return {"data": trace,
            "layout": go.Layout(title="Suicide Rates by age", colorway=['#C0C0C0', '#7f9900', ' #f7b880' , '#992362', '#d95153'],
                                yaxis={"title": "Suicide Rate"}, xaxis={"title": "Date"})}



@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(year_value):
    #dff = suicidesex[(suicidesex['Year'] >= year_value[0]) & (spyear["Year"] <= year_value[1])]
    dff = suicidesex[suicidesex['Year'] == year_value]
    return {
        'data': [dict(
            x=dff[ (dff['variable'] == 'Female')]['value'],
            y=dff[ (dff['variable'] == 'Male')]['value'],
            text= dff[dff['variable'] == 'Male']['Entity'],
            customdata=dff[dff['variable'] == 'Male']['Entity'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': '#111'},
                'color' : '#f08e62'
            }
        )],
        'layout': dict(
            xaxis={
                'title': 'Female',
                'type': 'linear',
                'color': '#111'
            },
            yaxis={
                'title': 'Male',
                'type': 'linear',
                'color': '#111'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest',
            plot_bgcolor = '#fff',
            paper_bgcolor = '#fff'


        )
    }


def create_time_series(dff, title):
    if('Male' in title ):
        return {
            'data': [dict(
                x=dff['Year'],
                y=dff['value'],
                mode='lines+markers',
                marker={
                    'color': '#7f9900'
                }
            )],
            'layout': {
                'height': 225,
                'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
                'annotations': [{
                    'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                    'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                    'align': 'left', 'bgcolor': 'white',
                    'text': title
                }],
                'yaxis': {'type': 'linear', 'color': 'white'},
                'xaxis': {'showgrid': False},
                'plot_bgcolor' : '#fff',
                'paper_bgcolor' : '#fff'
            }
        }
    elif( 'Female' in title):
            return {
                'data': [dict(
                    x=dff['Year'],
                    y=dff['value'],
                    mode='lines+markers',
                    marker={
                        'color': '#c83d58'
                    }
                )],
                'layout': {
                    'height': 225,
                    'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
                    'annotations': [{
                        'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                        'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                        'align': 'left', 'bgcolor': 'white',
                        'text': title
                    }],
                    'yaxis': {'type': 'linear', 'color': '#111'},
                    'xaxis': {'showgrid': False},
                    'plot_bgcolor': '#fff',
                    'paper_bgcolor': '#fff'
                }
            }


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_y_timeseries(hoverData):
    country_name = hoverData['points'][0]['customdata']
    dff = suicidesex[suicidesex['Entity'] ==country_name]
    dff = dff[dff['variable'] == 'Male']
    title = '<b>{}</b><br>{}'.format(country_name, 'Male')
    return create_time_series(dff, title)


@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_x_timeseries(hoverData):
    country_name = hoverData['points'][0]['customdata']
    dff = suicidesex[suicidesex['Entity'] ==country_name]
    dff = dff[dff['variable'] == 'Female']
    title = '<b>{}</b><br>{}'.format(country_name, 'Female')
    return create_time_series(dff, title)

if __name__ == '__main__':
    app.run_server(debug=True)


