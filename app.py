from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import logging
import urllib.request

MongoDB Database Connection


from pymongo.mongo_client import MongoClient



uri = "mongodb+srv://<username>:<password>@cluster0.gmusdjr.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
# my_mongo_db = client['webscrapper_api']
# my_collection = my_mongo_db['product_reviews_data']
logging.basicConfig(filename="web_scrapper.log", level=logging.INFO, format="%(asctime)s")
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/review', methods=['POST'])
def result():
    if request.method == 'POST':
        name = request.form['name'].replace(' ', "")
        flipkart = "https://www.flipkart.com/search?q=" + name
        flipkart_page = urllib.request.urlopen(flipkart)
        flipkart_html = BeautifulSoup(flipkart_page, 'html.parser')
        bigbox = flipkart_html.find_all('div', {"class": "_1AtVbE col-12-12"})
        del bigbox[0:3]
        product_link = "https://www.flipkart.com" + bigbox[0].div.div.div.a['href']
        product_req = requests.get(product_link)
        if product_req.status_code == 200:
            product_html = BeautifulSoup(product_req.text, 'html.parser')
            product_review = product_html.find_all('div', {'class': "_16PBlm"})
            reviews = []
            for i in product_review:
                try:
                    customer_name = i.div.div.find_all('p', {'class': "_2sc7ZR _2V5EHH"})[0].text
                except Exception as e:
                    customer_name = 'No Customer Name'
                try:
                    rating = i.div.div.div.div.text
                except Exception as e:
                    rating = "No rating"
                try:
                    comment_head = i.div.div.find_all('p', {"class": "_2-N8zT"})[0].text
                except Exception as e:
                    comment_head = 'No commentHead'
                try:
                    comtag = i.div.div.find_all('div', {"class": ""})[0].div.text
                except Exception as e:
                    comtag = "No customer tag"
                mydict = {"Product": name, "Name": customer_name, "Rating": rating, "CommentHead": comment_head,
                          "Comment": comtag}
                reviews.append(mydict)
                
            if reviews:
                logging.info(reviews)
                my_collection.insert_many(reviews)
                return render_template('result.html', reviews=reviews)
            else:
                return "No Reviews Found"   
        else:
            return render_template("home.html")
    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
