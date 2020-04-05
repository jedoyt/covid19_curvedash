import pandas as pd

def revise_covid19_data():
  # Prepare Data
  filepath = 'covid_19_data.csv' # Download from: https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset#covid_19_data.csv
  df = pd.read_csv(filepath, index_col=0)

  # Group DataFrame by 'Country/Region'
  df_bycountry = df.groupby(['ObservationDate','Country/Region']).sum().copy()
  # Reset indices
  df_bycountry.reset_index(inplace=True)

  '''print(df_bycountry.head())
    ObservationDate  Country/Region  Confirmed  Deaths  Recovered
  0      01/22/2020       Hong Kong        0.0     0.0        0.0
  1      01/22/2020           Japan        2.0     0.0        0.0
  2      01/22/2020           Macau        1.0     0.0        0.0
  3      01/22/2020  Mainland China      547.0    17.0       28.0
  4      01/22/2020     South Korea        1.0     0.0        0.0
  '''

  data_dict = {'date': [],
              'country' : [],
              'confirmed': [],
              'deaths': [],
              'recovered': [] 
              }

  for date in df_bycountry['ObservationDate'].unique():
    for country in df_bycountry['Country/Region'].unique():
        data_dict['date'].append(date)
        data_dict['country'].append(country)

        try:
          filter = (df_bycountry['ObservationDate'] == date) & (df_bycountry['Country/Region'] == country)
          data_dict['confirmed'].append(int(df_bycountry[filter]['Confirmed']))
          data_dict['deaths'].append(int(df_bycountry[filter]['Deaths']))
          data_dict['recovered'].append(int(df_bycountry[filter]['Recovered']))
        except:
          data_dict['confirmed'].append(0)
          data_dict['deaths'].append(0)
          data_dict['recovered'].append(0)

  rev_df = pd.DataFrame(data_dict)
  rev_df.to_csv('revised_covid_19_data.csv',index=False)
  print(rev_df.head())
  print(rev_df.tail())

  return rev_df

revise_covid19_data()