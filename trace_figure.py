import plotly.graph_objects as go
import pandas as pd 
import random
from datetime import datetime
from get_data import get_global_data

### GENERATE HEXCOLOR FUNCTION###
def generate_hexcolors(df):
    rgb = lambda: f"rgb({random.randint(140,255)},{random.randint(140,255)},{random.randint(140,255)})"
    return [rgb() for _ in range(len(df['country'].unique()))]

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

    # Set X values as recovery rate in percentage
    x_vals = round(df_bydate['recovered'] / df_bydate['confirmed'],4)

    data = go.Scatter(  x= x_vals,
                        y= df_bydate['deaths'],
                        mode='markers+text',
                        text= df_bydate['country'],
                        marker={'color': color_settings,
                                'size': df_bydate['confirmed'] * 0.001
                                }
                        )

    # Format Date
    parsed_date = datetime.strptime(str(date)[:10],"%m/%d/%Y")
    revised_date = datetime.strftime(parsed_date,"%B %-d, %Y")

    layout = go.Layout( title = f'COVID-19 Bubble Plot ({str(revised_date)})',
                        xaxis = dict(   title ='Recovery Rate in %',
                                        tickmode = 'array',
                                        tickvals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                                        ),
                        xaxis_tickformat = '%',
                        yaxis = dict(   title = 'Death Counts',
                                        tickmode = 'array',
                                        tickvals = [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000]
                                        ),
                        hovermode='x',
                        )

    return go.Figure(data=data,layout=layout)