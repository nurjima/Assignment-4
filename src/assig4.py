from datetime import datetime, timedelta
from functools import wraps
from flask import Flask
from flask.helpers import make_response
from flask import request
from flask import render_template
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0000@localhost/python"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class currency_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)

    def __init__(self, *args, **kwargs):
        super(currency_info, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Post id: {}\nTitle: {}\nDescription: {}\nLink: {}>'.format(self.id, self.title, self.description, self.link)


class WebScrapper:
    def search_for_google(self, query, number_result):
        query = query.replace(' ', '+')
        ua = UserAgent()
        db.create_all()

        google_url = "https://www.google.com/search?q=" + query + "&num=" + str(number_result)
        response = requests.get(google_url, {"User-Agent": ua.random})
        soup = BeautifulSoup(response.text, "html.parser")

        result_div = soup.find_all('div', attrs={'class': 'ZINbbc'})

        titles = []
        descriptions = []
        links = []

        for r in result_div:
            try:
                link = r.find('a', href=True)
                title = r.find('div', attrs={'class': 'vvjwJb'}).get_text()
                description = r.find('div', attrs={'class': 's3v9rd'}).get_text()

                if link != '' and title != '' and description != '':
                    links.append(link['href'])
                    titles.append(title)
                    descriptions.append(description)
            except:
                continue

        for i in range(len(descriptions)):
            c_i = currency_info(id=i+1, title=titles[i], description=descriptions[i], link=links[i])
            db.session.add(c_i)
            db.session.commit()

        coins = currency_info.query.all()
        return coins


@app.route('/')
def home():
    return render_template('searchbar.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    q = request.form['q']
    newWebScrapper = WebScrapper()
    number_of_results = 10
    if q:
        newWebScrapper.search_for_google(q, number_of_results)
        coins = currency_info.query.all()
        return render_template("output.html", coins=coins)
    else:
        return make_response('Could not find this kind of coins')
