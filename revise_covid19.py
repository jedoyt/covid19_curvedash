import pandas as pd
from bs4 import BeautifulSoup
import requests

def scrape_covid19_data():
  '''
  Concatenates all daily reports by using these internal functions:
    get_csv_links, get_day_report_df
  Finally, it generates a csv file with the filename 'covid_19_data.csv'
    This csv file is meant to be cleaned using the function revise_covid19_data()
  Returns a pandas dataframe containing the scraped raw dataset
  '''
  def get_csv_links():
    '''
    Fetches all links to csv files of daily reports
    and returns it as a list
    '''
    # URL containing list of csv files of daily reports
    url = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"

    # Create requests object: res
    res = requests.get(url)
    res.raise_for_status()

    # Create a Beautiful Soup object: soup
    soup = BeautifulSoup(res.text,'lxml')
    
    # Get table rows containing links to csv files
    table_rows = soup.table.tbody.find_all('tr', class_="js-navigation-item")[1:-1]
    
    # Set url prefix for the csv file links
    href_prefix = 'https://github.com'
    
    return [href_prefix + table_rows[i].span.a.get('href') for i in range(len(table_rows))]

  def get_day_report_df(csvpage_url):
    '''
    Scrapes the table content of a single csv page link
    to transform and return as a pandas dataframe
    '''
    print("GET request from",csvpage_url)

    # Create requests object: res
    res = requests.get(csvpage_url)
    res.raise_for_status()

    # Create a Beautiful Soup object: soup
    soup = BeautifulSoup(res.text,'lxml')
    
    # Read html string and generate a pandas dataframe
    df = pd.read_html(str(soup.table))[0]

    # Add additional column
    df['ObservationDate'] = '/'.join(csvpage_url[-14:-4].split('-'))
    
    # Rename column 'Country_Region' to 'Country/Region'
    df.rename(columns={'Country_Region':'Country/Region'},inplace=True)
    
    # Fill 'nan' with 0
    df.fillna(value=0,inplace=True)
    
    # Group DataFrame by 'Country/Region'
    df_bycountry = df.groupby(['ObservationDate','Country/Region']).sum().copy()
    df_bycountry.reset_index(inplace=True) # Reset index    
    df_bycountry = df_bycountry[['ObservationDate', # Reduce columns included
                                 'Country/Region',
                                 'Confirmed',
                                 'Deaths',
                                 'Recovered']]
    
    return df_bycountry
  print("Fetching links to daily reports...")
  csv_links = get_csv_links()

  print("Concatenating daily reports into a single dataframe...")
  df_list = [get_day_report_df(csv_links[i]) for i in range(len(csv_links))]

  df = pd.concat(df_list,axis=0)
  
  print("Dataframe complete!")
  print("Generated csv file: datasets/covid_19_data.csv")
  df.to_csv('datasets/covid_19_data.csv',index=False)

  #return df

def clean_covid19_data(df=pd.read_csv('datasets/covid_19_data.csv', index_col=0)):
  '''
  Cleans the newly scraped covid-19 data
  need only one parameter
  df - dataframe, This should be the output of scrape_covid19_data() function

  Returns a pandas dataframe containing the cleaned dataset
  '''
  print('Applying corrections on country names...')
  # Data Cleaning on Country Names
  df.replace({' Azerbaijan':'Azerbaijan',
              "('St. Martin',)":'Saint Martin',
              'St. Martin':'Saint Martin',
              'Bahamas, The':'Bahamas',
              'Czechia':'Czech Republic',
              'East Timor':'Timor-Leste',
              'Hong Kong SAR':'Hong Kong',
              'Iran (Islamic Republic of)':'Iran',
              'Korea, South':'South Korea',
              'Macao SAR':'Macau',
              'Mainland China':'China',
              'Republic of the Congo':'Congo (Brazzaville)',
              'Russian Federation':'Russia',
              'Republic of Korea':'South Korea',
              'Republic of Moldova':'Moldova',
              'Taipei and environs':'Taiwan',
              'Taiwan*':'Taiwan',
              'The Bahamas':'Bahamas',
              'UK': 'United Kingdom',
              'US': 'United States',
              'Viet Nam': 'Vietnam',
              'occupied Palestinian territory':'Palestine',
              'West Bank and Gaza':'Palestine'
              }, inplace=True)
  
  print("Temporary grouping of data by 'ObservationDate' and 'Country/Region'...")
  # Group DataFrame by 'Country/Region'
  df_bycountry = df.groupby(['ObservationDate','Country/Region']).sum().copy()
  
  print("Dropping invalid country data rows...")
  # Drop countries
  df_bycountry.reset_index(inplace=True)
  df_bycountry.set_index('Country/Region',inplace=True)
  df_bycountry.drop(labels=['North Ireland','Republic of Ireland','Cape Verde','Gambia, The',
                            'The Gambia','Guernsey','Jersey','Vatican City','Others'],axis=0,inplace=True)
  df_bycountry.reset_index(inplace=True)

  print("Adding the following columns: 'active', 'death_rate_float','recovery_rate_float...'")
  # Added columns
  df_bycountry['active'] = df_bycountry['Confirmed'] - df_bycountry['Deaths'] - df_bycountry['Recovered']
  df_bycountry['death_rate_float'] = df_bycountry['Deaths'] / df_bycountry['Confirmed']
  df_bycountry['recovery_rate_float'] = df_bycountry['Recovered'] / df_bycountry['Confirmed']
  
  print("Filling 'nan' values with 0...")
  # Fill 'nan' values by replacing with 0
  df_bycountry.fillna(0,inplace=True)

  print("Initially cleaned dataframe complete!")
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
  print("Reorganizing data in a dictioanary...")
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
    print("\tPopulating dictionary for this Observation Date:",date)
    for country in df_bycountry['Country/Region'].unique():
        print(f"\t\tFor {country}...")
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

  print("Final dataframe complete!")
  rev_df = pd.DataFrame(data_dict)

  # Added columns
  rev_df['death_rate'] = (rev_df['deaths'] / rev_df['confirmed']) * 100
  rev_df['death_rate'] = rev_df['death_rate'].round(2).astype(str) + " %"
  rev_df['recovery_rate'] = (rev_df['recovered'] / rev_df['confirmed']) * 100
  rev_df['recovery_rate'] = rev_df['recovery_rate'].round(2).astype(str) + " %"

  rev_df.to_csv('datasets/revised_covid_19_data.csv',index=False)
  print("Generated csv file: datasets/revised_covid_19_data.csv")
  print(rev_df.head())
  print(rev_df.tail())

  #return rev_df

def filter_asean_data(df=pd.read_csv('datasets/revised_covid_19_data.csv')):
  '''
  Filters the revised_covid_19_data by getting only the ASEAN countries
  returns a pandas dataframe containing only the data on ASEAN nations
  '''
  print("Filtering ASEAN Countries from 'revised_covid_19_data.csv'...")
  # Set index to country
  df.set_index('country',inplace=True)

  # ASEAN Countries
  asean_countries = ['Indonesia','Thailand','Singapore','Malaysia','Philippines',
                    'Vietnam','Cambodia','Laos','Brunei','Burma']

  asean_df = df.loc[asean_countries].copy()
  asean_df.reset_index(inplace=True)
  print("Dataframe for ASEAN Countries complete!")

  asean_df.to_csv('datasets/asean_covid_19_data.csv',index=False)
  print("Generated csv file: datasets/revised_covid_19_data.csv")
  print(asean_df.head())
  print(asean_df.tail())

  #return asean_df

# Unhash to run functions and update datasets manually
#scrape_covid19_data()
#clean_covid19_data()
#filter_asean_data()