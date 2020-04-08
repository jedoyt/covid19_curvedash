import requests
import json
import pandas as pd


def get_PH_topline_data():
    '''
    Read JSON Data from API: https://github.com/jasontalon/ncov-tracker
    OUTPUT: returns a dataframe of latest data on this format
                count error
    type                  
    tests       5530  None
    deaths       144  None
    PUIs        1323  None
    PUMs           0  None
    recovered     57  None
    confirmed   3094  None
    '''
    api_key = 'https://ncov-tracker-slexwwreja-de.a.run.app/numbers'

    res = requests.get(api_key)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    topline_dictlist = json.loads(res.text)
    print('Extracted JSON Data:\n',topline_dictlist)

    # Reorganize dictionary
    topline_dict = {key: [] for key in topline_dictlist[0].keys()}
    for dict_item in topline_dictlist:
        for key in dict_item.keys():
            topline_dict[key].append(dict_item[key])    

    # Build DataFrame out of the dictionary
    df = pd.DataFrame(topline_dict)
    df.set_index('type', inplace=True)

    return df

# Data on Hospitals in the Philippines
def get_PH_hospital_data():
    '''
    Read JSON Data from API: https://github.com/jasontalon/ncov-tracker
                                                        facility   latitude   longitude  count_
    ObjectId                                                                                  
    124                                          For Validation  14.615867  120.980991    2025
    1                     St. Luke's Medical Center-Global City  14.555128  121.048256      85
    2                                 St. Luke's Medical Center  14.622677  121.023532      76
    3                                     Makati Medical Center  14.559177  121.014546      66
    4                            Lung Center Of The Philippines  14.647821  121.045763      62
    '''
    api_key = 'https://ncov-tracker-slexwwreja-de.a.run.app/hospital'

    res = requests.get(api_key)
    try:
        res.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' % (exc))

    dictlist = json.loads(res.text)
    print('Extracted JSON Data:')
    for item in dictlist:
        print(item)

    # Reorganize dictionary
    ph_hospital_dict = {key: [] for key in dictlist[0].keys()}
    for dict_item in dictlist:
        for key in dict_item.keys():
            ph_hospital_dict[key].append(dict_item[key])

    # Build DataFrame out of the dictionary
    df = pd.DataFrame(ph_hospital_dict)
    df.set_index('ObjectId', inplace=True)

    return df

# GET GLOBAL DATA
def get_global_data():
    df = pd.read_csv('datasets/revised_covid_19_data.csv')
    latest_date = df['date'].unique()[-1]
    print(f'Global Data updated last {latest_date}')

    return df

def _top20_summary_desc(date):
    return f"Top 20 Countries as of {date} based on number of confirmed cases"

def get_top20_summarydf(df,date):
    df_bydate = df[df['date'] == date].copy()
    df_bydate = df_bydate[df_bydate['country'] != 'Others'] # Exlude the 'Others'
    df_top20 = df_bydate.nlargest(20,'confirmed')
    df_top20.reset_index(inplace=True)
    df_top20.drop(columns=['index','date'],inplace=True)
    df_top20.index = [ i+1 for i in range(20)]

    return df_top20