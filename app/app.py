from flask import Flask, jsonify, request, render_template, Markup, Response, send_from_directory
from flaskext.markdown import Markdown

import json
import jstyleson

import functions
import logging


app = Flask(__name__)

# static pages


@app.route("/")
@app.route("/<view>")
def content_handler(view='index'):
    if view in ['index', 'specifications', 'getting-started']:
        view = view + '.html'
        return render_template(view)
    else:
        return "404"


# models list
@app.route("/models")
def models_home():
    file_to_open = 'models/model_list.json'
    models = json.loads(open(file_to_open, 'r').read())['models_order']
    return render_template('models.html', models=models)

# model viewer


@app.route("/models/<model>")
def models(model):
    #    try:
    models = json.loads(open('models/model_list.json', 'r').read())['models']
    model_file = 'models/{modelname}.json'.format(modelname=models[model.lower()]['modelName'])
    model = json.loads(open(model_file, 'r').read())
    model = functions.build_full_model(model)
    example = functions.build_example_json(model)
    return render_template('model.html', model=model, example=json.dumps(example, indent=4, sort_keys=True))
#    except:
#        return "404"
