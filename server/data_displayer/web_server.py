from flask import Flask, render_template
import json
import pandas as pd
import plotly
import plotly.express as px

from pymongo import MongoClient

app = Flask(__name__)

def connect_to_db(msclient):
	client = MongoClient("mongodb://127.0.0.1:27017/")
	col = "Client_127_0_0_1"
	return client["test"][col]

@app.route('/')
def plots():
   
   df = pd.DataFrame(dict(
    x = ["a", "b", "c", "d"],
    y = [1, 2, 3, 4]))
   
   fig = px.line(df, x="x", y="y", title="Unsorted Input") 
   fig.show()
   df = df.sort_values(by="x")
   fig = px.line(df, x="x", y="y", title="Sorted Input") 
   #fig.show()
   #Use render_template to pass graphJSON to html
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('bar.html', graphJSON=graphJSON)
 
 
if __name__ == '__main__':
    app.run(debug=True)