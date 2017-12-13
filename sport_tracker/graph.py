import matplotlib
import matplotlib.pyplot as plt 
import cufflinks as cf 
import pandas as pd 
import folium
import warnings
import os

"""
read_file()
Input: name of file to read data from 
Output: lists of data for the UI to interpret
Algorithm:
Figure out the filepath of the chosen file
Read the csv data from the file that was produced
Get lists of data for each series of data from the newly created Dataframe
'Delist' the elements from the old DataFrame structure to return just a list of values, not a list of lists
Return those new lists of the Opponenets, number of tweets and the wins/losses to be used in the Chart.js UI implementation

Lucas was in charge of implementing the data visualization section as we were initilizing going to use plotly, but then decided to use Chart.js because it was easier to format into an html structure which seems to only function well enough for Jupyter notebook
"""
def read_file(file):
    file_name = os.path.abspath("data/{}".format(file))
    football_data = pd.read_csv(file_name, encoding="latin1")
    num_tweets = football_data[["Opponent","Number of Tweets"]]
    opponents = football_data['Opponent']
    wls = football_data[['W/L']].values.tolist()
    num_tweets = football_data['Number of Tweets']
    football_df = pd.DataFrame( { "Opponent" : opponents,  "Tweet Count" : num_tweets})
    opponentz = football_data[['Opponent']].values.tolist()
    number_tweets = football_data[['Number of Tweets']].values.tolist()
    new_opponents = []
    for x in opponentz:
        x = ("").join(x)
        new_opponents.append(x)
    number_tweet = []
    for x in number_tweets:
        x = map(str,x)
        x = "".join(x)
        x = int(x)
        number_tweet.append(x)
    new_wls = []
    for x in wls:
        x = ("").join(x)
        new_wls.append(x)    
    return new_opponents, number_tweet, new_wls
