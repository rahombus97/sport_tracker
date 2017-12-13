from flask import Flask, request, redirect, session
from flask import render_template
from graph import read_file
from twitter import get_schools, scrape_a, sport_url, url_format, print_exception, process_sports, formatDate
import json

#app name to intialize by (secret_key was need to apparently keep 'session' variables)
#Chris was in charge of implemeting the the view models for the flask application. I thought this was pretty neat to design my Python logic around using a UI. It was pretty a sweet experience and now I feel like I can apply this to so many other areas whereas I can now make a fully functioning UI with a backend easily with Python
#In the UI, I (Chris) also got to flex some of my skills with Javascript and JQuery manipulating DOM elements. I've used JQuery pretty extensively beforehand so I wanted to add a little bit of my own flavor once I knew I was going to be creating the UI with HTML
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#initial variables needed to render templates such as the dropdown and describe overall state such as no errors or data
option_list = get_schools(scrape_a())
error = ""
data = None

#Start page just putting option list into UI
@app.route('/')
def hello(option_list=option_list):
    return render_template('startPage.html',option_list=option_list)

#Once user enters their query, the data is taken from the UI and manipulated to get the information about that school, sport, and year
#Checks are done to determine what sport, year, and school to format the url with. Error handling is also used to handle the cases when the school doesn't have data for that sport or year, or the user doesn't enter all of the inputs 
@app.route('/search',methods=['GET','POST'])
def run(option_list=option_list):
    if request.method == 'POST':
        try:
            sport = request.form.getlist('sport')
            if 'cfb' in sport:
                sport = 'cfb'
            elif 'cbb' in sport:
                sport = 'cbb'
            sport_url = request.form.get('options')
            year = request.form['year']
            data = url_format(sport_url,sport,year)
            table = data
            session['load'] = False
            school_name = option_list[sport_url]
            load = session.get('load', None)
            if data is None:
                error = "Sorry, there are no statistics for {} for ".format(year)
                return render_template('index.html',option_list=option_list, error=error,data=data,school_name=school_name,year=year,load=load)
            else:
                error = "" 
                session["load"] = True
                file_name = "{}_{}{}".format(sport,school_name,year)
                session['table'] = data.to_json()
                other = data[["Opponent"]]
                other[["W/L"]] = data[["W/L"]]
                session['opps'] = other.to_json()
                data = data[["Date"]]
                data = {file_name : data}
                data[file_name] = formatDate(data[file_name]).to_json()
                session["data"] = data
                session["school_name"] = school_name
                return render_template('index.html',option_list=option_list,data=table.to_html(),school_name=school_name,year=year,load=load)
        except UnboundLocalError as e:
            print_exception()
            error = "Please enter all of the inputs"
            school_name = ""
            return render_template('index.html',option_list=option_list,error=error,school_name=school_name)   
    elif request.method == 'POST' and session['load'] == True:
        process_sports(data,school,opps)
        return render_template('index.html',option_list=option_list,data=table.to_html(),school_name=school_name,year=year,load=load)
    elif request.method == 'GET':
        session['load'] = False
        load = session.get('load', None)
        return render_template('index.html',option_list=option_list,load=load)

#When the user wants to find about about the number of tweets for that school, year, and sport. The UI will not seem like it's doing anything, but in the backend the script is running to scrape the tweets from Twitter. 
#Unfortunately this takes a very long time to scrape the data due to the sheer amount of processing the DOM elements that's needed to scrape all of this data.
@app.route('/submit', methods=['GET','POST'])
def command():
    the_data = session.get("data", None)
    the_opps = session.get('opps', None)
    school = session.get('school_name', None)
    load = session.get('load', None)
    session["results"] = process_sports(the_data, school, the_opps)
    return render_template('index.html',option_list=option_list,data=table.to_html(),school_name=school_name,year=year,load=load)

#This is for the page to visualize the data once the tweet scraping is done. The user just have to simply upload the csv file that was created from our application and that data will be visualized in our UI through the use of a Javascript library called Chart.js that interacts beautifully with Flask
@app.route('/graph', methods=['GET','POST'])
def graph():
    results = session.get('results', None)
    school = session.get('school_name', None)
    file_name = request.form.get('file')
    if file_name:
        labels, values, wls = read_file(file_name)
        print(wls)
        return render_template('graph.html',labels=labels, values=values,wls=wls)
    else:
        return render_template('graph.html',data=results, school=school)

#Intilizing the application if it's called by a script, once again we'll need that secret key for the app to store session variables apparently
if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run()
