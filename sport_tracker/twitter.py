import datetime, time
import json
import pandas as pd
import got3
import urllib
import app
import requests, bs4, re, json
import sys, linecache

#storing this value for use in the overall app
sport_url = ""

#Chris also implemented this functions and helper methods to help manipulate and scrape the needed data for the gameday tweet analysis 
"""
formatDate()
Input: list of unformmated correctly dates 
Output: list of correctly formatted tweets for using the "GetOldTweets" tool
Algorithm:
Go through dates and format date based on what needed sport
If we run into an exception in the first case, then then the other formatting algorthm will occur
Replace values with new format
Return date data with new format
"""
def formatDate(dates):
    for i, date in enumerate(dates.values):
        try:           
            new_date = ("").join(date)[:11]
            d = datetime.datetime.strptime(new_date, "%b %d, %Y").strftime("%Y-%m-%d")
            dates.at[i, "Date"] = d
        except ValueError:
            new_date = ("").join(date)[5:]
            if new_date == "":
                continue
            d = datetime.datetime.strptime(new_date, "%b %d, %Y").strftime("%Y-%m-%d")
            dates.at[i, "Date"] = d
    return dates
"""
url_format()
Input: part of url, sport from user, year from user
Output: A dataframe contaning the information about how the team did that season (Games, Opponents, Wins/Losses)
Algorithm:
Figure out which sport the user wants, and use that to determine what html table to scrape from 
Make call to formatted url based on input from function
If successful, then return the requested data to be shown in the UI
"""
def url_format(url,sport,year):
    df = None
    if sport == "cfb":
        table = "Games"
        column = {"Unnamed: 8": "W/L", "Unnamed: 7": "W/L"}
    elif sport == "cbb":
        table = "Schedule and Results"
        column = {"\xa0.1": "W/L"}
    try:
        url = "https://www.sports-reference.com/{}{}{}-schedule.html".format(sport,url[4:],year)
        print("Schedule URL: {}".format(url))
        df = pd.read_html(url, match=table)[0]
        df.rename(columns=column,inplace=True)
        df = df[["Date","Opponent", "W/L"]]
    except requests.exceptions.HTTPError as e:
        print("ERROR: Response from ", url, 'was not ok.')
        print("DETAILS:", e)
    except urllib.error.HTTPError as e:
        print("ERROR: Response from ", url, 'was not ok.')
        print("DETAILS:", e)   
    return df
"""
getTweets()
Input:  dates in needed format to search for tweets, the school name to use as a keyword to search
Output: List of the number of tweets for each specific game day with mentions of the school
Algorithm:
Iterate through and use the dates to search for tweets on those days with keyword of school
Add every number of tweets to a list
Return that list at the endr
"""
def getTweets(dates, school):
    tweet_counts = []
    for date in dates.values:
        date = "".join(date)
        next_day = datetime.datetime.strptime(date, "%Y-%m-%d")
        next_day = next_day + datetime.timedelta(days=1)
        next_day = datetime.datetime.strftime(next_day, "%Y-%m-%d")
        tweetCriteria = got3.manager.TweetCriteria().setQuerySearch(school).setSince(date).setUntil(next_day).setMaxTweets(10000)
        tweets = got3.manager.TweetManager.getTweets(tweetCriteria)
        number_of_tweets = len(tweets)
        for i in range(5):
            print("")
        print("DATE: {} TWEETS: {}".format(date, number_of_tweets))
        for i in range(5):
            print("")
        tweet_counts.append(number_of_tweets)
    return tweet_counts
"""
process_sports()
Input: Object of data that includes file name as key to save data to and number of tweets as value, school name
Output: New dataframe with number of tweets attached, also a csv with the data
Algorithm:
Convert the dates data from a string into dictionary (json) format 
Get data in dataframe to be ready to be written to a csv
Write data to csv with name of sport, school, and year in file name
Return the tweet data as well
"""
def process_sports(data, school, opps):
    final_data = None
    for key, d in data.items():
        d = json.loads(d)
        d = list(d["Date"].values())
        d = pd.DataFrame(d, columns=['Date'])
        d["Oppenents"] = pd.DataFrame({"Opponents": list(json.loads(opps)["Opponent"].values())})
        d["W/L"] = pd.DataFrame({"W/L": list(json.loads(opps)["W/L"].values())})
        print(d)
        num_tweets = pd.DataFrame({"num_tweets": getTweets(d[["Date"]], school)})
        d["Number of Tweets"] = num_tweets
        final_data = d
        with open("data/{}.csv".format(key), 'w') as file:
            file.write(d.to_csv())
    return final_data
"""
cleanhtml()
Input: misformed html
Output: Clean text 
Algorithm: clean the html to be functionality to browsers and the dropdown in UI
"""
def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
"""
get_schools()
Input: all the schools available from dataset
Output: part of links for all the schools to get data from sports and seasons
Algorithm: 
Helper function to format all the links correctly
Input all the schools
Filter out poorly formatted data
Get the link for the school out of the 'href' in the 'a' tag
Format a dictionary of key values associating the school name with the part of the url for that school
Return dictionary of associations of those values
"""
def get_schools(schools):
    schools_links = {}
    for school_name in schools:
        name = cleanhtml(school_name.prettify())
        name = name.replace("\n","")[1:]
        if name.startswith("adjust"):
            continue
        school_short_name = school_name['href']
        schools_links[school_short_name] = name
    return schools_links
"""
scrape_a()
Input: None
Output: All the schools available to scrape data from
Algorithm: 
Scrape data from master list of schools
Get all of the 'a' tags and get the links from them
Return that list of links
"""
def scrape_a():
    page = requests.get('https://www.sports-reference.com/cfb/schools/')
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    school_list = soup.find(class_='sortable')
    school_list_items = school_list.find_all('a', href=True)
    return school_list_items
"""
print_exeception()
Input: None
Output: Details about why the exception occured
Algorithm: 
Nifty little method I found to find out more information about why bad things are happpening
"""
def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
