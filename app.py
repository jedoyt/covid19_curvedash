import dash
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from covid_data import CountryCovidData
import pandas as pd

# Create Dash Main Instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# DATA PREPARATIONS

# Read the COVID-19 Dataset
csv_path = 'covid_data/novel-corona-virus-2019-dataset/covid_19_data.csv'
covid = pd.read_csv(csv_path,index_col=0)

# Generate data for visualization
country = 'US' # Choose country
country_data = CountryCovidData(covid_df = covid,
                                country = country,
                                x_dates = covid['ObservationDate'].unique()
                                )
data_dict = country_data.get_dict()

# Make a sorted list of countries for the Dropdown Menu
country_list = list(covid['Country/Region'].unique()) # Get list of countries
country_list.sort(reverse=False) # Sort list in ascending order

# Other variables
latest_stats = country_data.get_latest_summary(data_dict = data_dict) # Get latest statistics
source_link = "https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset"
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# DASH COMPONENTS

# Navigation Bar Setup
navbar = dbc.NavbarSimple(dbc.NavItem(children=[html.A(html.Img(src="https://image.flaticon.com/icons/svg/1077/1077041.svg",
                                                                height="30px"), href="https://www.facebook.com/jed.unalivia"),
                                                html.Span("  "),
                                                html.A(html.Img(src="https://image.flaticon.com/icons/svg/1051/1051382.svg",
                                                                height="30px"), href="https://twitter.com/JedUnalivia"),
                                                html.Span("  "),
                                                html.A(html.Img(src="https://image.flaticon.com/icons/svg/1384/1384046.svg",
                                                                height="30px"), href="https://www.linkedin.com/in/jed-u%C3%B1alivia/")
                                                ], className='navbar-dark'),
                          brand="COVID-19 Curve Monitoring Dashboard",
                          brand_href="#",
                          color="light",
                          dark=False,
                          )

# Dropdown Menu Setup for selecting countries
country_dictlist = [{'label': country, 'value': country} for country in country_list] # Create a list of dictionary as reference for the dropdown menu
country_dropdown = dcc.Dropdown(options=country_dictlist, value=country, id='country-selection')

# Setup Graph
fig = country_data.make_go_figure(data_dict=data_dict)
graph = dcc.Graph(figure=fig,id='selected-country')

# Setup content field under jumbotron
jumbotron = dbc.Jumbotron(
                          dbc.Container([
                                         html.H5("Select Country", className="display-5"),
                                         country_dropdown,
                                         html.Hr(className="my-2"),
                                         graph,
                                         html.Div(className='jumbotron', id='country-summary'),
                                               
                                         ])
                          )
footer_col1 =  [html.Hr(className="my-2"),
                html.Small(children=[   "Data Source Link: ",
                                        html.A(html.Small("Dataset from Kaggle"),href=source_link)
                                        ]),
                html.Br(),        
                html.Small(children=[   "Visualization was made using: ",
                                        html.A(html.Img(src=PLOTLY_LOGO, height="30px"),href="https://plot.ly")
                                        ]),
                ]

# Setup Footer Content
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

app.layout = dbc.Container(children=[navbar,jumbotron,footer])

@app.callback(Output(component_id='selected-country', component_property='figure'),
              [Input(component_id='country-selection', component_property='value')])
def update_figure(selected_country):
        country = selected_country
        country_data = CountryCovidData(covid_df = covid,
                                        country = country,
                                        x_dates = covid['ObservationDate'].unique()
                                        )
        data_dict = country_data.get_dict()
        fig = country_data.make_go_figure(data_dict=data_dict)
        return fig

@app.callback(Output(component_id='country-summary', component_property='children'),
              [Input(component_id='country-selection', component_property='value')])
def update_summary_stats(selected_country):
        country = selected_country
        country_data = CountryCovidData(covid_df = covid,
                                        country = country,
                                        x_dates = covid['ObservationDate'].unique()
                                        )
        data_dict = country_data.get_dict()
        latest_stats = country_data.get_latest_summary(data_dict = data_dict)
        return [html.H6(f"Summary Statistics as of {latest_stats['date']} from {latest_stats['country']}", className="display-5"),
                html.Hr(className="my-2"),
                html.P(f"Total Confirmed Cases: {latest_stats['confirmed']}"),
                html.P(f"Death Toll: {latest_stats['deaths']} ,  {latest_stats['death_rate']} of confirmed cases"),
                html.P(f"Recovered: {latest_stats['recovered']} ,  {latest_stats['recovery_rate']} of confirmed cases")]

if __name__ == '__main__':
    app.run_server()