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
    models = functions.read_file(filepath, json_format=True)['models_order']
    return functions.render_view('models.html', {'models': models})


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
    model_to_test = {}
    incorrect_fields = {}
    missing_fields = {}

    filter = False

    if 'show_only_failures' in request.form:
        filter = 'only_failures'

    # first test if the feed is valid JSON
    try:
        feed_dictionary = json.loads(feed_string.strip())
        json_errors = False
    except:
        feed_dictionary = False
        json_errors = True

    # if it is valid JSON
    if not json_errors:
        if len(feed_dictionary) == 0:
            empty_json = True
        else:
            empty_json = False
        # load the model which we'll test against
        model_to_test = checker.load_model_to_test('Event.json')

        # then look for fields with the wrong sort of values
        incorrect_fields = checker.check_feed_field_types(feed_dictionary, model_to_test)

        # then look for missing fields
        missing_fields = checker.check_for_missing_fields(feed_dictionary, model_to_test)


    if filter:
        incorrect_fields = checker.filter_errors(incorrect_fields, filter)
        missing_fields = checker.filter_errors(missing_fields, filter)

    response = {
        'feed': feed_dictionary,
        'incorrect_fields': incorrect_fields,
        'missing_fields': missing_fields
    }

    if json_return:
        jsonify(response)

    else:
        return functions.render_view('feed_display.html', {
            'response': response,
            'feed': json.dumps(feed_dictionary, indent=4),
            'incorrect_fields': json.dumps(incorrect_fields, indent=4),
            'missing_fields': json.dumps(missing_fields, indent=4),
            'json_errors': json_errors,
            'empty_json': empty_json,
            'filter': filter,
            'model_to_test': json.dumps(model_to_test, indent=4)
        })
