from flask import Flask, jsonify, request, Markup, Response, send_from_directory
from flaskext.markdown import Markdown

from feed_tools import checker

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
            view_contents = functions.read_file(filepath, json_format=False)
            title = view_contents.split('---')[0]
            content = Markup(markdown.markdown(view_contents.split('---')[1]))
        except:
            filepath = 'content/{view}.html'.format(view=view)
            view_contents = functions.read_file(filepath, json_format=False)
            title = view_contents.split('---')[0]
            content = view_contents.split('---')[1]
        return functions.render_view('content.html', {'title': title, 'content': content})
    else:
        return "404"


@app.route("/models")
def models_home():
    filepath = 'models/model_list.json'
    model_list = functions.read_file(filepath, json_format=True)
    models = model_list['models_order']
    event_core = model_list['event_core']
    event_elements = model_list['event_elements']
    event_booking = model_list['event_booking']
    return functions.render_view('models.html', {'models': models, 'event_core': event_core, 'event_elements': event_elements, 'event_booking': event_booking})


@app.route("/models/<model>")
def models(model):
    try:
        models = functions.read_file('models/model_list.json', json_format=True)['models']
        filepath = 'models/{modelname}.json'.format(modelname=models[model.lower()]['modelName'])
        model = functions.read_file(filepath, json_format=True)
        model = functions.build_full_model(model)
        example = functions.build_example_json(model)
        return functions.render_view('model.html', {'model': model, 'example': json.dumps(example, indent=4, sort_keys=True)})
    except:
        return "404"


@app.route("/tools/check-feed", methods=['GET'])
def check_feed_form():
    return functions.render_view('feed_form.html', {})


@app.route("/tools/check-feed(.json)", methods=['POST'])
@app.route("/tools/check-feed", methods=['POST'])
def check_feed(json_return=False):

    feed_string = request.form['feed_json']

    filter = False
    if 'filter' in request.form:
        filter = request.form['filter']
        if filter == 'all':
            filter = False

    response, json_errors, empty_json = checker.check_feed_string(feed_string, 'Event.json', filter)

    if json_return:
        jsonify(response)

    else:
        return functions.render_view('feed_display.html', {
            'response': response,
            'feed': json.dumps(response['feed_dictionary'], indent=4),
            'incorrect_fields': json.dumps(response['incorrect_fields'], indent=4),
            'missing_fields': json.dumps(response['missing_fields'], indent=4),
            'json_errors': json_errors,
            'empty_json': empty_json,
            'filter': filter,
            'model_to_test': json.dumps(response['model_to_test'], indent=4)
        })
