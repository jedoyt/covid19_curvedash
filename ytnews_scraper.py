# import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Create a dictionary of urls
_news_channels_ = [{'base': 'Singapore',
                  'channel':'Channel News Asia',
                  'yturl': 'https://www.youtube.com/user/channelnewsasia/videos',
                  'img-src': 'https://yt3.ggpht.com/a/AATXAJyNO1OasteohNJvuwpHJEV6-wN9nt1rofR0Rg=s100-c-k-c0xffffffff-no-rj-mo'
                 }, 
                 {'base': 'Singapore',
                  'channel':'The Strait Times',
                  'yturl': 'https://www.youtube.com/user/StraitsTimesOnline/videos'},
                 {'base': 'Singapore',
                  'channel':'Today Online',
                  'yturl': 'https://www.youtube.com/user/TODAYdigital/videos'},
                 {'base': 'Malaysia',
                  'channel':'The Star Online',
                  'yturl': 'https://www.youtube.com/user/thestaronline/videos'},
                 {'base': 'Malaysia',
                  'channel':'The Malaysian Insight',
                  'yturl': 'https://www.youtube.com/user/incitemytv/videos'},
                 {'base': 'Thailand',
                  'channel':'Bangkok Post',
                  'yturl': 'https://www.youtube.com/user/bangkokpostvideos/videos'},
                 {'base': 'Philippines',
                  'channel':'Rappler',
                  'yturl': 'https://www.youtube.com/user/rapplerdotcom/videos'},
                 {'base': 'Indonesia',
                  'channel':'The Jakarta Post',
                  'yturl': 'https://www.youtube.com/channel/UC2zhLSPeHaH7fFBsRLf2Z0w/videos'},
                 {'base': 'Philippines',
                  'channel':'ANC',
                  'yturl':'https://www.youtube.com/user/ANCalerts/videos'},
                 {'base': 'Thailand',
                  'channel': 'NBT World',
                  'yturl': 'https://www.youtube.com/channel/UCprW3qy6P2AU_nG-EwS4aRg/videos'},
                 {'base': 'Vietnam',
                  'channel': 'Vietnam News Agency',
                  'yturl': 'https://www.youtube.com/channel/UCN9em1FY03nO7tMV4D2lb-g/videos'},
                 {'base': 'Thailand',
                  'channel': 'The Thaiger',
                  'yturl': 'https://www.youtube.com/user/PGTVPhuket/videos'   
                 }
                ]

def get_latest_ytnewslinks(channel_url):
    '''
    Scrapes YouTube for the URLs of the latest video uploads(news) from a news channel
    Returns a pandas dataframe containing the info on the news.
    '''
    # Create requests object
    res = requests.get(channel_url)
    res.raise_for_status()

    # Create a BeautifulSoup object: soup
    soup = BeautifulSoup(res.text,'lxml')
    
    # Get 5 recent news data
    contents = soup.find_all('h3', class_="yt-lockup-title")[:5]
    
    # Setup dictionary
    news_dict = {'channel': [],
                 'title': [],
                 'url': [],
                 'date': [],
                 'img-src': []
                }
    
    # Populate dictionary
    for content in contents:
        news_dict['channel'].append(soup.find('meta').get('content'))
        news_dict['title'].append(content.find('a').get('title'))
        news_dict['url'].append('https://www.youtube.com' + content.find('a').get('href'))
        print('Added on news_dict:')
        print(soup.find('meta').get('content'),'|',content.find('a').get('title'),'\n')
    
    # Add publish date of the videos
    for item in news_dict['url']:
        video_url = item

        # Create requests object
        vid_res = requests.get(video_url)
        vid_res.raise_for_status()

        # Create a BeautifulSoup object: soup
        vid_soup = BeautifulSoup(vid_res.text,'lxml')
        
        # Parse the soup for the publish date
        for meta in vid_soup.html.body.find_all('meta'):
            if meta.get('itemprop') == 'datePublished':
                news_dict['date'].append(meta.get('content'))
                # Add thumbnail of channel logo
                news_dict['img-src'].append(vid_soup.find('a',class_="yt-user-photo yt-uix-sessionlink spf-link").find('img').get('data-thumb'))
    
    news_df = pd.DataFrame(news_dict)
    news_df['sortkey'] = news_df['date'] + ':' + news_df['title']
    print('DataFrame Completed!')
    
    return news_df

def get_all_latestnews():
    '''
    Uses the get_latest_ytnewslinks function to iterate throughout _news_channels_
    Returns a pandas dataframes containing all the news headlines from the chosen news channels
    listed within _news_channels_
    '''
    df_list = []

    for i in range(len(_news_channels_)):
        try:
            df_list.append(get_latest_ytnewslinks(channel_url=_news_channels_[i]['yturl']))
        except:
            print("\nUnable to scrape from", _news_channels_[i]['channel'],'...\n')
            pass

    df = pd.concat(df_list, axis=0)
    df.sort_values(by='sortkey',ascending=False,inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=['index'],inplace=True)
    #df.to_csv('datasets/news' + ''.join(str(datetime.utcnow()).split(":")[:-1]) + '.csv')
    df.to_csv('datasets/news.csv')
    print("News Dataframe complete!")
    print("Generated csv file: datasets/news.csv")

    #return df

#df = get_all_latestnews()
#print(df)