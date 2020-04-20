import pandas as pd

def revise_covid19_data():
  # Prepare Data
  filepath = 'covid_19_data.csv' # Download from: https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset#covid_19_data.csv
  df = pd.read_csv(filepath, index_col=0)

  # Data Cleaning on Country Names
  df.replace({' Azerbaijan':'Azerbaijan',
              "('St. Martin',)":'Saint Martin',
              'St. Martin':'Saint Martin',
              'Bahamas, The':'Bahamas',
              'Mainland China':'China',
              'Republic of the Congo':'Congo (Brazzaville)',
              'UK': 'United Kingdom',
              'US': 'United States',
              'occupied Palestinian territory':'Palestine',
              'West Bank and Gaza':'Palestine'
              }, inplace=True)

  # Group DataFrame by 'Country/Region'
  df_bycountry = df.groupby(['ObservationDate','Country/Region']).sum().copy()
  
  # Drop countries
  df_bycountry.reset_index(inplace=True)
  df_bycountry.set_index('Country/Region',inplace=True)
  df_bycountry.drop(labels=['North Ireland','Republic of Ireland','Cape Verde','Gambia, The',
                            'The Gambia','Guernsey','Jersey','Vatican City'],axis=0,inplace=True)
  df_bycountry.reset_index(inplace=True)

  # Added columns
  df_bycountry['active'] = df_bycountry['Confirmed'] - df_bycountry['Deaths'] - df_bycountry['Recovered']
  df_bycountry['death_rate_float'] = df_bycountry['Deaths'] / df_bycountry['Confirmed']
  df_bycountry['recovery_rate_float'] = df_bycountry['Recovered'] / df_bycountry['Confirmed']
  
  # Fill 'nan' values by replacing with 0
  df_bycountry.fillna(0,inplace=True)

  # Reset indices
  df_bycountry.reset_index(inplace=True)
  print(df_bycountry.info())
  print(df_bycountry.head())
  '''print(df_bycountry.head())
   index Country/Region ObservationDate  Confirmed  Deaths  Recovered  active  death_rate_float  recovery_rate_float
       0          China      01/22/2020      548.0    17.0       28.0   503.0          0.031022             0.051095
       1      Hong Kong      01/22/2020        0.0     0.0        0.0     0.0          0.000000             0.000000
       2          Japan      01/22/2020        2.0     0.0        0.0     2.0          0.000000             0.000000
       3    South Korea      01/22/2020        1.0     0.0        0.0     1.0          0.000000             0.000000
       4         Taiwan      01/22/2020        1.0     0.0        0.0     1.0          0.000000             0.000000
  '''

  data_dict = {'date':[],
               'country':[],
               'confirmed':[],
               'deaths':[],
               'recovered':[],
               'active':[],
               'death_rate_float':[],
               'recovery_rate_float':[]
              }

  for date in df_bycountry['ObservationDate'].unique():
    for country in df_bycountry['Country/Region'].unique():
        data_dict['date'].append(date)
        data_dict['country'].append(country)

        try:
          df_filter = (df_bycountry['ObservationDate'] == date) & (df_bycountry['Country/Region'] == country)
          data_dict['confirmed'].append(int(df_bycountry[df_filter]['Confirmed']))
          data_dict['deaths'].append(int(df_bycountry[df_filter]['Deaths']))
          data_dict['recovered'].append(int(df_bycountry[df_filter]['Recovered']))
          data_dict['active'].append(int(df_bycountry[df_filter]['active']))
          data_dict['death_rate_float'].append(float(df_bycountry[df_filter]['death_rate_float']))
          data_dict['recovery_rate_float'].append(float(df_bycountry[df_filter]['recovery_rate_float']))
        except:
          data_dict['confirmed'].append(0)
          data_dict['deaths'].append(0)
          data_dict['recovered'].append(0)
          data_dict['active'].append(0)
          data_dict['death_rate_float'].append(0)
          data_dict['recovery_rate_float'].append(0)          

  rev_df = pd.DataFrame(data_dict)

  # Added columns
  rev_df['death_rate'] = (rev_df['deaths'] / rev_df['confirmed']) * 100
  rev_df['death_rate'] = rev_df['death_rate'].round(2).astype(str) + " %"
  rev_df['recovery_rate'] = (rev_df['recovered'] / rev_df['confirmed']) * 100
  rev_df['recovery_rate'] = rev_df['recovery_rate'].round(2).astype(str) + " %"

  rev_df.to_csv('revised_covid_19_data.csv',index=False)
  print(rev_df.head())
  print(rev_df.tail())

  return rev_df

revise_covid19_data()