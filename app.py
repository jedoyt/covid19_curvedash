import dash 
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_table
from dash.dependencies import Input, Output
from get_data import get_global_data, get_asean_dailydf #, _top20_summary_desc, get_top20_summarydf , get_PH_topline_data
from trace_figure import load_lineplot_fig, load_bubbleplot_fig, generate_hexcolors
from ytnews_scraper import _news_channels_, get_latest_ytnewslinks, get_all_latestnews
from revise_covid19 import scrape_covid19_data, clean_covid19_data, filter_asean_data
import pandas as pd
import locale # Used for formatting large number to have commas
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Create Dash main instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.config.suppress_callback_exceptions = True
app.title = 'COVID-19 ASEAN Benchmarking Dashboard'
server = app.server

# FETCH ALL NEEDED DATA IN PANDAS DATAFRAMES
#ph_topline_data = get_PH_topline_data() # Latest data on PH from: https://ncovph.com/
#print('Fetched Topline Data from API (https://ncovph.com/):')
#print(ph_topline_data)
df = pd.read_csv('datasets/revised_covid_19_data.csv')
asean_df = pd.read_csv('datasets/asean_covid_19_data.csv')

# Generate color codes for each country bubble
#latest_asean_df = asean_df[asean_df['date'] == asean_df.iloc[-1]['date']]
color_settings = generate_hexcolors(counts=len(asean_df['country'].unique()))

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
                          brand="COVID-19 ASEAN Benchmarking Dashboard",
                          brand_href="https://nameless-crag-44586.herokuapp.com/",
                          color="light",
                          dark=False,
                          )

### UPPER CONTENT ###
# CONTENT 1: TOPLINE DATA ON PHILIPPINES
locale.setlocale(locale.LC_ALL, '')

PH_kaggle_filter = (df['country'] == 'Philippines') & (df['date'] == df.iloc[-1]['date'])
PH_kaggle_df = df[PH_kaggle_filter]

topline_header1 = [html.Thead(html.Tr([html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered")]))]
topline_body1 = [html.Tbody(children=[html.Tr(children = [
                                                         html.Td(html.H2(PH_kaggle_df['confirmed'])),   # From Kaggle
                                                         html.Td(html.H2(PH_kaggle_df['deaths'])),      # From Kaggle
                                                         html.Td(html.H2(PH_kaggle_df['recovered']))    # From Kaggle
                                                         ])                   
                                     ])]

topline_header2 = [html.Thead(html.Tr([html.Th("Active"), html.Th("Fatality Rate"), html.Th("Recovery Rate")]))]
topline_body2 = [html.Tbody(children=[html.Tr(children = [
                                                         html.Td(html.H2(PH_kaggle_df['active'])),          # From Kaggle
                                                         html.Td(html.H2(PH_kaggle_df['death_rate'])),      # From Kaggle
                                                         html.Td(html.H2(PH_kaggle_df['recovery_rate']))    # From Kaggle
                                                         ])                   
                                     ])]

topline_table1 = dbc.Table(topline_header1 + topline_body1, bordered=False)
topline_table2 = dbc.Table(topline_header2 + topline_body2, bordered=False)

topline_left = dbc.Col(children=[html.H5(f"Philippines as of {df.iloc[-1]['date']}", className="display-5"),
                                 html.Hr(className="my-2"),
                                 topline_table1,
                                 html.Hr(className="my-2"),
                                 topline_table2
                                 ])

# CONTENT 2: DATA SOURCE and ABOUT DASHBOARD
topline_right = dbc.Col(children=[html.H5("Data Source", className="display-5"),
                                  html.Hr(className="my-2"),
                                  dbc.Row([ #dbc.Col(html.Small("Current Source:")),
                                            dbc.Col(html.A('Github (provided by JHU CSSE)', href="https://github.com/CSSEGISandData/COVID-19"))]),
                                  dbc.Row([ #dbc.Col(html.Small("Previous Source:")),
                                            dbc.Col(html.A('Kaggle', href="https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset"))]),
                                  html.Br(),
                                  html.Hr(className="my-2"),
                                  html.H5("About Dashboard", className="display-5"),
                                  html.Hr(className="my-2"),
                                  html.Small("This page was made using a Python Framework, Plotly and Dash."),
                                  html.Small(" The purpose of this page is to be used as a benchmarking tool through exploration of data and looking for insights through the links to news headlines."),
                                  html.Br(),
                                  html.Small("It starts with the topline data from my home country Philippines then it goes down to looking at the daily standings with our neigbors in the South East Asia."),
                                  html.Br(),
                                  html.Small("For qualitative benchmarking, I've also added the links to the latest news coming from these Asian countries through news-oriented YouTube channels."),
                                  html.Br(),
                                  html.Small("The figure at the bottom is a global-scoped interactive line plot where you can check the COVID-19 data from all other countries.")
                                  ])

upper_content_row = dbc.Row(children=[topline_left,topline_right])
#############################################################
upper_content = dbc.Jumbotron(children=[upper_content_row], #
                              id='upper-content')           #
#############################################################

### MIDDLE CONTENT ###
# CONTENT 1: DAILY STANDINGS OF ASEAN COUNTRIES
asean_date = asean_df['date'].iloc[-1] # Initially selected date
asean_datefiltered = get_asean_dailydf(date=asean_date,df=asean_df)

# Using Bootstrap Table
asean_header = [html.Thead(html.Tr([html.Th('Rank'),html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered"), html.Th('Active Cases'), html.Th('Death Rate'), html.Th('Recovery Rate')]))] 
asean_rows = [html.Tr([ html.Td(html.Small(i)), \
                        html.Td(html.Small(asean_datefiltered.loc[i]['country'])), \
                        html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['confirmed'], grouping=True))), \
                        html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['deaths'], grouping=True))), \
                        html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['recovered'], grouping=True))), \
                        html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['active'], grouping=True))), \
                        html.Td(html.Small(asean_datefiltered.loc[i]['death_rate'])), \
                        html.Td(html.Small(asean_datefiltered.loc[i]['recovery_rate']))]) for i in asean_datefiltered.index
             ]
asean_body = [html.Tbody(children=asean_rows)]
asean_table = dbc.Table(asean_header + asean_body, bordered=False)

# Change Date Format
parsed_aseandate = datetime.strptime(str(asean_date)[:10],"%m/%d/%Y")
revised_aseandate = datetime.strftime(parsed_aseandate,"%B %-d, %Y")

# Construct Slider
asean_days = len(asean_df['date'].unique())

# Slider marks
asean_day0 = df['date'].unique()[round(asean_days*0)][:5]
asean_dayQ1= df['date'].unique()[round(asean_days*0.1)][:5]
asean_dayQ2= df['date'].unique()[round(asean_days*0.2)][:5]
asean_dayQ3= df['date'].unique()[round(asean_days*0.3)][:5]
asean_dayQ4= df['date'].unique()[round(asean_days*0.4)][:5]
asean_dayQ5= df['date'].unique()[round(asean_days*0.5)][:5]
asean_dayQ6= df['date'].unique()[round(asean_days*0.6)][:5]
asean_dayQ7= df['date'].unique()[round(asean_days*0.7)][:5]
asean_dayQ8= df['date'].unique()[round(asean_days*0.8)][:5]
asean_dayQ9= df['date'].unique()[round(asean_days*0.9)][:5]
asean_dayN = df['date'].unique()[round(asean_days*1)-1][:5]

# Attempt to create a dictionary comprehension
#cents = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
#slider_marks = { round(asean_days*cent) : df['date'].unique()[round(asean_days*cent)][:5] \
#                 for cent in cents }

asean_slider = dbc.Card(children=[html.Br(),
                                  dcc.Slider(min=0, max=len(asean_df['date'].unique()) - 1,
                                  marks={0: asean_day0,
                                         round(asean_days*0.1,): asean_dayQ1,
                                         round(asean_days*0.2,): asean_dayQ2,
                                         round(asean_days*0.3,): asean_dayQ3,
                                         round(asean_days*0.4,): asean_dayQ4,
                                         round(asean_days*0.5,): asean_dayQ5,
                                         round(asean_days*0.6,): asean_dayQ6,
                                         round(asean_days*0.7,): asean_dayQ7,
                                         round(asean_days*0.8,): asean_dayQ8,
                                         round(asean_days*0.9,): asean_dayQ9,
                                         len(asean_df['date'].unique()) - 1 : asean_dayN  
                                        },
                                  #marks=slider_marks,
                                  id='asean-slider')
                                  ],
                         className='mb-3'
                         )

asean_table_container = dbc.Container(children=[html.H5(f"ASEAN Daily Standings ({str(revised_aseandate)})"),
                                                html.P("Use slider below to see daily changes. The slider affects both the table and the bubble plot.",
                                                       className="display-7"),
                                                asean_table
                                                ],id='asean-table'
                                     )

# Construct Bubble Plot
asean_bubble_graph = dcc.Graph(figure=load_bubbleplot_fig(df=asean_df,date=asean_date,color_settings=color_settings),
                               id='asean-bubble')

# Construct News Headlines Section
news_df = pd.read_csv('datasets/news.csv')

asean_news_rows = html.Div([dbc.Row(dbc.Col(html.Small(children=[html.A(news_df.iloc[i]['title'], href=news_df.iloc[i]['url']), \
                                                                 html.Small(' -- '), \
                                                                 html.Img(src=news_df.iloc[i]['img-src'], alt=news_df.iloc[i]['channel'], width=20, height=20), \
                                                                 html.Small(' | ' + news_df.iloc[i]['date'])]))) \
                                                                 for i in news_df.index],
                            id='asean-news')

asean_news_container = dbc.Container(children = [asean_news_rows,
                                                 #dcc.Interval(id='news-interval-component',
                                                 #interval=1800000,
                                                 #n_intervals=0)
                                                 ])

#################################################################
middle_content = dbc.Jumbotron(children=[asean_table_container, #
                                         asean_slider,          #
                                         asean_bubble_graph,    #
                                         html.Small("NOTE: The size of the bubble indicates the number of confirmed cases."),
                                         html.Hr(className="my-2"),
                                         html.H5(f"Asian News Headlines"),
                                         asean_news_container   #
                                         ])                     #
#################################################################

### LOWER CONTENT ###
# CONTENT 1: LINE PLOT OF GLOBAL DATA
country = 'Philippines' # Initially Selected Country
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
                                                html.Small(f"Data on this graph is as of {df.iloc[-1]['date']}"),                                                
                                                ])

# SUBCONTENT: Layout of Country Summary under the line plot
summary_filter = (df['date'] == df.iloc[-1]['date']) & (df['country'] == country)
latest_confirmed = locale.format_string("%d", df[summary_filter]['confirmed'], grouping=True)
latest_deaths = locale.format_string("%d", df[summary_filter]['deaths'], grouping=True)
latest_recovered = locale.format_string("%d", df[summary_filter]['recovered'], grouping=True)
latest_active = locale.format_string("%d", df[summary_filter]['active'], grouping=True)
latest_deathrate = str(df[summary_filter]['death_rate'] * 100) + " %"
latest_recoveryrate = str(df[summary_filter]['recovery_rate'] * 100) + " %"

summary_header = [html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered"), html.Th('Active Cases'), html.Th('Death Rate'), html.Th('Recovery Rate')] 
summary_row = [ html.Tr([html.Td(country),
                         html.Td(latest_confirmed),
                         html.Td(latest_deaths),
                         html.Td(latest_recovered),
                         html.Td(latest_active),
                         html.Td(latest_deathrate),
                         html.Td(latest_recoveryrate)
                         ])]
summary_body = [html.Tbody(children=summary_row)]
summary_table = dbc.Table(summary_header + summary_body, bordered=False)
country_summary = dbc.Jumbotron(children=[html.P(f"Latest Statistics on {country} as of {df.iloc[-1]['date']}"),
                                          summary_table
                                          ],
                                          id='country-summary')

lower_content = dbc.Container(children=[line_graph_container,
                                        country_summary,
                                        #bubble_graph_container,
                                        #top20_summary,
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

dash_contents = html.Div(children=[ navbar,           
                                    upper_content,    
                                    middle_content,   
                                    lower_content,    
                                    footer],
                         id='dash-contents'
                        )

##### MAIN LAYOUT OF WHOLE DASHBOARD PAGE ##############
app.layout = dbc.Container(children=[dash_contents,    #
                                     #dcc.Interval(id='interval-component',
                                     #             interval=28800000,
                                     #             n_intervals=0)
                                     ])                #
########################################################


# CALLBACK SECTION #
# Line Plot Callback
@app.callback(Output(component_id='selected-country', component_property='figure'),
              [Input(component_id='country-selection', component_property='value')])
def update_linefig(selected_country):
    return load_lineplot_fig(df=df,country=selected_country)

@app.callback(Output(component_id='country-summary', component_property='children'),
              [Input(component_id='country-selection', component_property='value')])
def update_country_summary(selected_country):
    global country
    country = selected_country
    summary_filter = (df['date'] == df.iloc[-1]['date']) & (df['country'] == country)
    latest_confirmed = locale.format_string("%d", df[summary_filter]['confirmed'], grouping=True)
    latest_deaths = locale.format_string("%d", df[summary_filter]['deaths'], grouping=True)
    latest_recovered = locale.format_string("%d", df[summary_filter]['recovered'], grouping=True)
    latest_active = locale.format_string("%d", df[summary_filter]['active'], grouping=True)
    latest_deathrate = df[summary_filter]['death_rate']
    latest_recoveryrate = df[summary_filter]['recovery_rate']

    summary_header = [html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered"), html.Th('Active Cases'), html.Th('Death Rate'), html.Th('Recovery Rate')] 
    summary_row = [html.Tr([html.Td(country), html.Td(latest_confirmed), html.Td(latest_deaths), html.Td(latest_recovered), html.Td(latest_active), html.Td(latest_deathrate), html.Td(latest_recoveryrate),])]
    summary_body = [html.Tbody(children=summary_row)]
    summary_table = dbc.Table(summary_header + summary_body, bordered=False)

    return [html.P( f"Latest Statistics on {country} as of {df.iloc[-1]['date']}"),
                    summary_table
                    ]

# ASEAN Table Callback
@app.callback(Output(component_id='asean-table', component_property='children'),
              [Input(component_id='asean-slider', component_property='value')])
def update_asean_table(date_index):
    global asean_date
    global asean_datefiltered
    asean_date = asean_df['date'].unique()[date_index]
    asean_datefiltered = get_asean_dailydf(date=asean_date,df=asean_df)

    # Using Bootstrap Table
    asean_header = [html.Thead(html.Tr([html.Th('Rank'),html.Th('Country'),html.Th("Confirmed"), html.Th("Deaths"), html.Th("Recovered"), html.Th('Active Cases'), html.Th('Death Rate'), html.Th('Recovery Rate')]))] 
    asean_rows = [  html.Tr([html.Td(html.Small(i)), \
                    html.Td(html.Small(asean_datefiltered.loc[i]['country'])), \
                    html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['confirmed'], grouping=True))), \
                    html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['deaths'], grouping=True))), \
                    html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['recovered'], grouping=True))), \
                    html.Td(html.Small(locale.format_string("%d", asean_datefiltered.loc[i]['active'], grouping=True))), \
                    html.Td(html.Small(asean_datefiltered.loc[i]['death_rate'])), \
                    html.Td(html.Small(asean_datefiltered.loc[i]['recovery_rate']))]) for i in asean_datefiltered.index ]
    asean_body = [html.Tbody(children=asean_rows)]
    asean_table = dbc.Table(asean_header + asean_body, bordered=False)

    # Change Date Format
    parsed_aseandate = datetime.strptime(str(asean_date)[:10],"%m/%d/%Y")
    revised_aseandate = datetime.strftime(parsed_aseandate,"%B %-d, %Y")

    return [html.H5(f"ASEAN Daily Standings ({str(revised_aseandate)})"),
            html.P("Use slider below to see daily changes. The slider affects both the table and the bubble plot.", 
                    className="display-7"),
            asean_table
            ]

# ASEAN Bubble Plot Callback
@app.callback(Output(component_id='asean-bubble', component_property='figure'),
              [Input(component_id='asean-slider', component_property='value')])
def update_asean_bubble(date_index):
    global asean_date
    asean_date = asean_df['date'].unique()[date_index]
    return load_bubbleplot_fig(df=asean_df,date=asean_date,color_settings=color_settings)

# LIVE-UPDATING CALLBACKS
"""
@app.callback(Output(component_id='asean-news', component_property='children'),
              [Input(component_id='news-interval-component', component_property='n_intervals')])
def live_update_news(n):
    '''
    Updates news headlines every 30 minutes
    '''
    get_all_latestnews()

    global news_df
    news_df = pd.read_csv('datasets/news.csv')

    return [dbc.Row(dbc.Col(html.Small(children=[html.A(news_df.iloc[i]['title'], href=news_df.iloc[i]['url']), \
                                                 html.Small(' -- '), \
                                                 html.Img(src=news_df.iloc[i]['img-src'], alt=news_df.iloc[i]['channel'], width=20, height=20), \
                                                 html.Small(' | ' + news_df.iloc[i]['date'])]))) \
                                                 for i in news_df.index]

@app.callback(Output(component_id='dash-contents', component_property='children'),
              [Input(component_id='interval-component', component_property='n_intervals')])
def live_update_layout(n):
    '''
    Updates layout every 8 hours
    '''
    print(f"Live update commence: {str(datetime.now())}")
    scrape_covid19_data()
    clean_covid19_data()
    filter_asean_data()
    get_all_latestnews()

    print("Reassigning variables of dataframes by reading updated csv files...")
    global df
    df = pd.read_csv('datasets/revised_covid_19_data.csv')
    global asean_df
    asean_df = pd.read_csv('datasets/asean_covid_19_data.csv')
    global asean_date
    asean_date = asean_df['date'].iloc[-1]
    global news_df
    news_df = pd.read_csv('datasets/news.csv')
    print(f"Live update completed last {str(datetime.now())}!")
    return [navbar, upper_content, middle_content, lower_content, footer]
"""
# APP TRIGGER #
if __name__ == '__main__':
    app.run_server()