from flask import Flask, jsonify, request
from REFAIR import getDomain
from REFAIR import getMLTask
from REFAIR import feature_extraction

app = Flask(__name__)

@app.route("/")
def homepage():
    return "Welcome to ReFair!"

@app.route('/refair', methods = ['POST','GET'])
def analysis():
    
    if request.method == 'POST':
        story = request.form['story']   
        domain = getDomain(story)
        ml_tasks = getMLTask(story, domain)

        features = feature_extraction(domain, ml_tasks)

        return jsonify(
            domain=domain,
            tasks=ml_tasks,
            features=features
        )
    else: return "Not Allowed"
    