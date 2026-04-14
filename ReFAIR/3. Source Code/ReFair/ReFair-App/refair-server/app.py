from flask import Flask, Response, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS


from REFAIR import getDomain
from REFAIR import getMLTask
from REFAIR import feature_extraction

import pandas as pd
import json

ALLOWED_EXTENSIONS = {'xlsx'}


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/storiesload', methods=['POST'])
def load_stories():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'stories' not in request.files:
            return jsonify({
                'status': 'failure',
                'motivation': "No file \"stories.xlsx\" loaded"
            })
        
        file = request.files['stories']
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'failure',
                'motivation': "No file \"stories.xlsx\" loaded"
            })


        stories = pd.read_excel(file)

        if 'User Story' in stories:
            return jsonify({
                'status': 'success',
                'stories': stories["User Story"].tolist()
            })
        else:  return jsonify({
                'status': 'failure',
                'motivation': "No column \"User Story\" found"
            })


@app.route('/analyzeStory', methods = ['POST','GET'])
def analysis():
    
    if request.method == 'POST':
        story = request.form['story']  
        domain = getDomain(story)
        ml_tasks = getMLTask(story, domain)

        tasks_features = feature_extraction(domain, ml_tasks)

        unique_features = {}
        for features in tasks_features.values():
            for feature in features:
                if feature in unique_features:
                    unique_features[feature] = unique_features[feature] + 1 
                else:
                     unique_features[feature] = 1


        return jsonify(
            domain=domain,
            tasks=ml_tasks,
            tasks_features=tasks_features,
            features_counts = unique_features
        )
    else: return "Not Allowed"
    


@app.route('/reportStories', methods = ['POST','GET'])
def reportStories():
    
    if request.method == 'POST':
        analyzed_stories = []

        stories = json.loads(request.form['stories']) 

        
        for story in stories:
            domain = getDomain(story)
            ml_tasks = getMLTask(story, domain)

            features = feature_extraction(domain, ml_tasks)

            analyzed_stories.append({"story": story, "domain":domain, "tasks":ml_tasks,"features":features})

        content = str(analyzed_stories)
        return Response(content, 
                mimetype='application/json',
                headers={'Content-Disposition':'attachment;filename=zones.geojson'})

        
    else: return "Not Allowed"


@app.route('/reportStory', methods = ['POST','GET'])
def reportStory():
    
    if request.method == 'POST':
        analyzed_stories = []

        story = json.loads(request.form['story']) 

        
        domain = getDomain(story)
        ml_tasks = getMLTask(story, domain)

        features = feature_extraction(domain, ml_tasks)

        analyzed_story = {"story": story, "domain":domain, "tasks":ml_tasks,"features":features}

        content = str(analyzed_story)
        return Response(content, 
                mimetype='application/json',
                headers={'Content-Disposition':'attachment;filename=zones.geojson'})

        
    else: return "Not Allowed"



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run()