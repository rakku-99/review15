from flask import Flask, render_template, request, jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

# Assign a variable app containing Flask Object
app = Flask(__name__)

# route to display the home page
@app.route('/',methods=['GET'])  
@cross_origin()
def homePage():
    return render_template("index.html")

# route to show the review comments in a web UI
@app.route('/review',methods=['POST','GET']) 

# decorator @cross_origin
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            dbConn= pymongo.MongoClient("mongodb://localhost:27017/")
            db=dbConn['crawlDB']
            reviews= db[searchString].find({})
            if review.count()>0:
                return render_template('results.html', reviews=reviews)
            else:
                searchString = request.form['content'].replace(" ","")
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()

                flipkart_html = bs(flipkartPage, "html.parser")
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prodRes.encoding='utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                #print(prod_html)
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

                table=db[searchString]
                #filename = searchString + ".csv"
                #fw = open(filename, "w")
                #headers = "Product, Customer Name, Rating, Heading, Comment \n"
                #fw.write(headers)
                #reviews = []
                for commentbox in commentboxes:
                    try:
                        price = prod_html.find_all('div', {'class': "_16Jk6d"})[0].text
                    except:
                        price = 'no price available'

                    try:
                        #name.encode(encoding='utf-8')
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        #rating.encode(encoding='utf-8')
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        #commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        #custComment.encode(encoding='utf-8')
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)

                    mydict = {"Price" : price, "Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}
                    reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
            
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
