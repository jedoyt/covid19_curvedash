import dash 
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output
from get_data import get_PH_topline_data, get_global_data, _top20_summary_desc, get_top20_summarydf
from trace_figure import load_lineplot_fig, load_bubbleplot_fig, generate_hexcolors
import pandas as pd

# Create Dash main instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.config.suppress_callback_exceptions = True
server = app.server

# FETCH ALL NEEDED DATA IN PANDAS DATAFRAMES
ph_topline_df = get_PH_topline_data() # Latest data on PH
df = get_global_data() # Global Data

# DASHBOARD COMPONENTS #
### NAVIGATION BAR ###
navbar = dbc.NavbarSimple(dbc.NavItem(children=[html.A(html.Img(src="https://image.flaticon.com/icons/svg/1077/1077041.svg",
                                                                height="30px"), href="https://www.facebook.com/jed.unalivia"),
                                                html.Span("  "),
                                                html.A(html.Img(src="https://image.flaticon.com/icons/svg/1051/1051382.svg",
                                                                height="30px"), href="https://twitter.com/JedUnalivia"),
                                                html.Span("  "),
                                                html.A(html.Img(src="https://image.flaticon.com/icons/svg/1384/1384046.svg",
                                                                height="30px"), href="https://www.linkedin.com/in/jed-u%C3%B1alivia/")
                                                ], className='navbar-dark'),
                          brand="COVID-19 Dashboard",
                          brand_href="#",
                          color="light",
                          dark=False,
                          )

### UPPER CONTENT ###
# CONTENT 1: TOPLINE DATA ON PHILIPPINES
topline_header = [html.Thead(html.Tr([html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered")]))]
topline_body = [html.Tbody(children=[html.Tr(children = [html.Td(html.H2(ph_topline_df.loc['confirmed']['count'])),
                                                         html.Td(html.H2(ph_topline_df.loc['deaths']['count'])),
                                                         html.Td(html.H2(ph_topline_df.loc['recovered']['count']))])
                                     ])]
topline_table = dbc.Table(topline_header + topline_body, bordered=False)

topline_left = dbc.Col(children=[html.H5("Philippines Latest Counts", className="display-5"),
                               html.Hr(className="my-2"),
                               topline_table
                               ])

# CONTENT 2: DATA SOURCES
topline_right = dbc.Col(children=[html.H5("Data Sources", className="display-5"),
                                  html.Hr(className="my-2"),
                                  dbc.Row([ dbc.Col(html.Small("On latest PH counts:")),
                                            dbc.Col(html.A('Github', href="https://github.com/jasontalon/ncov-tracker"))]),
                                  dbc.Row([ dbc.Col(html.Small("On global data for visualizations:")),
                                            dbc.Col(html.A('Kaggle', href="https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset"))])
                                  ])
upper_content_row = dbc.Row(children=[topline_left,topline_right])
#############################################################
upper_content = dbc.Jumbotron(children=[upper_content_row]) #
#############################################################

### LOWER CONTENT ###
# CONTENT 1: LINE PLOT OF GLOBAL DATA
country = 'US' # Initially Selected Country
# Setup Dropdown Menu
country_list = list(df['country'].unique().copy())
country_list.sort(reverse=False) # Sort list in ascending order
country_dictlist = [{'label': country, 'value': country} for country in country_list] # Create a list of dictionary as reference for the dropdown menu
country_dropdown = dcc.Dropdown(options=country_dictlist, value=country, id='country-selection')

# Setup Initial Graph
#lineplot_fig = load_lineplot_fig(df=df,country=country)
line_graph = dcc.Graph(figure=load_lineplot_fig(df=df,country=country), id='selected-country')
line_graph_container = dbc.Jumbotron(children=[ html.H4("COVID-19 Global Data: Line Plot"),
                                                html.H5("Select Country from dropdown", className="display-5"),
                                                country_dropdown,
                                                line_graph,
                                                html.Small(f"Data on this graph is as of {df.iloc[-1]['date']}")
                                                ])

# CONTENT 2: BUBBLE PLOT OF GLOBAL DATA
date = df['date'].unique()[-1] # Initially Selected Date
color_settings = generate_hexcolors() # Generate color codes for each country bubble
day0 = df['date'].unique()[0][:5]
dayN = df['date'].unique()[-1][:5]
# Construct Bubble Plot
bubble_slider = dbc.Card(children=[ html.Br(),
                                    dcc.Slider(min=0, max=len(df['date'].unique()) - 1,
                                    marks={ 0: day0,
                                            len(df['date'].unique()) - 1 : dayN  
                                            },
                                    id='day-slider')
                                    ],
                         className='mb-3'
                         )

bubble_graph = dcc.Graph(figure=load_bubbleplot_fig(df=df,date=date,color_settings=color_settings),id='selected-date')

# Construct Daily Top 20 Countries
top20_df = get_top20_summarydf(df=df,date=date) # A Dataframe containing the top 20 countries
top20_header = [html.Thead(html.Tr([html.Th('Rank'),html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered")]))] 
top20_rows = [html.Tr([html.Td(i), html.Td(top20_df.loc[i]['country']), html.Td(top20_df.loc[i]['confirmed']), html.Td(top20_df.loc[i]['deaths']), html.Td(top20_df.loc[i]['recovered'])]) for i in top20_df.index]
top20_body = [html.Tbody(children=top20_rows)]
top20_table = dbc.Table(top20_header + top20_body, bordered=False)

top20_summary = dbc.Jumbotron(children=[html.H6(_top20_summary_desc(date=date)),
                                        top20_table
                                        ], id='top20-date')

bubble_graph_container = dbc.Jumbotron(children=[   html.H4("COVID-19 Global Data: Bubble Plot"),
                                                    html.P("This graph only shows the daily top 10 countries based on number of confirmed cases. The size of the bubble indicates the number of confirmed cases. Use slider below the graph to see daily changes.", className="display-7"),
                                                    bubble_graph,
                                                    bubble_slider,
                                                    html.Small(f"Data on this graph is as of {df.iloc[-1]['date']}"),
                                                ])

lower_content = dbc.Container(children=[line_graph_container,
                                        bubble_graph_container,
                                        top20_summary
                                        ])

### FOOTER CONTENT ###
# Setup Footer Content
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

footer_col1 =  [html.Hr(className="my-2"),       
                html.Small(children=[   "Visualization was made using: ",
                                        html.A(html.Img(src=PLOTLY_LOGO, height="30px"),href="https://plot.ly")
                                        ]),
                ]

footer_col2 =  [html.Hr(className="my-2"),
                html.P(children=["Contact me:  ",
                html.A(html.Img(src="https://image.flaticon.com/icons/svg/174/174848.svg",
                                height="30px"), href="https://www.facebook.com/jed.unalivia"),
                html.Span("  "),
                html.A(html.Img(src="https://image.flaticon.com/icons/svg/145/145812.svg",
                                height="30px"), href="https://twitter.com/JedUnalivia"),
                html.Span("  "),
                html.A(html.Img(src="https://image.flaticon.com/icons/svg/145/145807.svg",
                                height="30px"), href="https://www.linkedin.com/in/jed-u%C3%B1alivia/")
                                ]),
                html.Br(),
                html.Small(children=["Attribution for Social Media Icons: ",
                                     html.A(html.Small("https://image.flaticon.com"),href="https://image.flaticon.com")
                                     ])
                ]                      

footer_row = dbc.Row([dbc.Col(footer_col1),dbc.Col([html.Hr(className="my-2")]), dbc.Col(footer_col2)])

footer = dbc.Container(footer_row)

##### MAIN LAYOUT OF WHOLE DASHBOARD PAGE ##############
app.layout = dbc.Container(children=[navbar,           #
                                     upper_content,    #
                                     lower_content,    #
                                     footer            #
                                     ])                #
########################################################


# CALLBACK SECTION #
# Line Plot Callback
@app.callback(Output(component_id='selected-country', component_property='figure'),
              [Input(component_id='country-selection', component_property='value')])
def update_linefig(selected_country):

    return load_lineplot_fig(df=df,country=selected_country)

# Bubble Plot Callback
@app.callback(Output(component_id='selected-date', component_property='figure'),
              [Input(component_id='day-slider', component_property='value')])
def update_bubblefig(date_index):
    date = df['date'].unique()[date_index]
    return load_bubbleplot_fig(df=df,date=date,color_settings=color_settings)

@app.callback(Output(component_id='top20-date', component_property='children'),
              [Input(component_id='day-slider', component_property='value')])
def update_top20_summary(date_index):
    date = df['date'].unique()[date_index]
    top20_df = get_top20_summarydf(df=df,date=date) # A Dataframe containing the top 20 countries
    top20_header = [html.Thead(html.Tr([html.Th('Rank'),html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered")]))] 
    top20_rows = [html.Tr([html.Td(i), html.Td(top20_df.loc[i]['country']), html.Td(top20_df.loc[i]['confirmed']), html.Td(top20_df.loc[i]['deaths']), html.Td(top20_df.loc[i]['recovered'])]) for i in top20_df.index]
    top20_body = [html.Tbody(children=top20_rows)]
    top20_table = dbc.Table(top20_header + top20_body, bordered=False)

    return [html.H6(_top20_summary_desc(date=date)),top20_table]

# APP TRIGGER #
if __name__ == '__main__':
    app.run_server()