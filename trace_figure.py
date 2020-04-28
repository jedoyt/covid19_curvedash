import plotly.graph_objects as go
import pandas as pd 
import random
from datetime import datetime
from get_data import get_global_data


### GENERATE HEXCOLOR FUNCTION###
def generate_hexcolors(counts=10):
    '''
    Generates a list of colors meant to be assigned for countries.
    Takes only one argument:
    counts -    int, the number of colors you need to generate that
                should also be equal to the number of unique countries
                from the dataframe.
    '''
    random.seed(8)
    rgb = lambda: f"rgb({random.randint(100,255)},{random.randint(100,255)},{random.randint(100,255)})"
    return [rgb() for _ in range(counts)]

def load_lineplot_fig(df,country):
    '''
    Load a lineplot figure to be filtered by country
    '''
    df_bycountry = df[df['country'] == country].copy()

    x_dates = [str(date)[:5] for date in df_bycountry['date']]

    confirmed_trace = go.Scatter(x= x_dates,
                                 y= df_bycountry['confirmed'],
                                 mode='lines', name='Confirmed',
                                 marker={'color':'green'}
                                 )
    deaths_trace = go.Scatter(x= x_dates,
                              y= df_bycountry['deaths'],
                              mode='lines', name='Deaths',
                              marker={'color':'red'}
                              )
    recovered_trace = go.Scatter(x= x_dates,
                                y= df_bycountry['recovered'],
                                mode='lines', name='Recovered',
                                marker={'color':'blue'}
                                )

    data = [confirmed_trace, deaths_trace, recovered_trace]

    layout = go.Layout(title= f"Cumulative Counts from {country}",
                    xaxis= {'title': 'Observation Dates'},
                    yaxis= {'title': 'Counts'},
                    hovermode= 'x'
                    )

    return go.Figure(data=data,layout=layout)

def load_bubbleplot_fig(df,date,color_settings):
    df_bydate = df[df['date'] == date].copy()
    #df_bydate = df_bydate[df_bydate['country'] != 'Others'] # Exlude the 'Others'
    # Limit display to only top 10 countries based on active cases
    #df_bydate = df_bydate.nlargest(10,'active')

    # Set X values as recovery rate in percentage
    #x_vals = round(df_bydate['recovered'] / df_bydate['confirmed'],4)
    #y_vals = round(df_bydate['deaths'] / df_bydate['confirmed'],4)

    data = go.Scatter(  x= df_bydate['recovery_rate_float'],
                        y= df_bydate['death_rate_float'],
                        mode='markers+text',
                        text= df_bydate['country'],
                        marker={'color': color_settings,
                                'size': df_bydate['confirmed'] * 0.015
                                }
                        )

    # Format Date
    parsed_date = datetime.strptime(str(date)[:10],"%m/%d/%Y")
    revised_date = datetime.strftime(parsed_date,"%B %-d, %Y")

    layout = go.Layout( title = f'COVID-19 Bubble Plot ({str(revised_date)})',
                        xaxis = dict(   title ='Recovery Rate in %',
                                        tickmode = 'array',
                                        tickvals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
                                        ),
                        xaxis_tickformat = '%',
                        yaxis = dict(   title = 'Fatality Rate in %',
                                        tickmode = 'array',
                                        tickvals = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
                                        ),
                        yaxis_tickformat = '%',
                        hovermode='x',
                        )

    return go.Figure(data=data,layout=layout)

# Test Functions
#fig = load_lineplot_fig(df=pd.read_csv('datasets/revised_covid_19_data.csv'),country='Malaysia')
#fig.show()