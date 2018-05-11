from flask import Flask, jsonify, request, Markup, Response, send_from_directory
from flaskext.markdown import Markdown
import markdown

import json
import jstyleson

import functions
import constants

import logging


app = Flask(__name__)


@app.route("/")
@app.route("/<view>")
def content_handler(view='index'):
    view = view.lower()
    if view in constants.content_items:
        try:
            filepath = 'content/{view}.md'.format(view=view)
            view_contents = open(filepath, 'r').read()
            title = view_contents.split('---')[0]
            content = Markup(markdown.markdown(view_contents.split('---')[1]))
        except:
            filepath = 'content/{view}.html'.format(view=view)
            view_contents = open(filepath, 'r').read()
            title = view_contents.split('---')[0]
            content = view_contents.split('---')[1]
        return functions.render_view('content.html', {'title': title, 'content': content})
    else:
        return "404"


@app.route("/models")
def models_home():
    file_to_open = 'models/model_list.json'
    models = json.loads(open(file_to_open, 'r').read())['models_order']
    return functions.render_view('models.html', {'models': models})


@app.route("/models/<model>")
def models(model):
    #    try:
    models = json.loads(open('models/model_list.json', 'r').read())['models']
    model_file = 'models/{modelname}.json'.format(modelname=models[model.lower()]['modelName'])
    model = json.loads(open(model_file, 'r').read())
    model = functions.build_full_model(model)
    example = functions.build_example_json(model)
    return functions.render_view('model.html', {'model': model, 'example': json.dumps(example, indent=4, sort_keys=True)})
#    except:
#        return "404"
