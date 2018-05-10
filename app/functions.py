from flask import Markup, render_template
import markdown
import json

import constants
import logging


def render_view(viewname, params):
    params['navbar_items'] = constants.navbar_items
    return render_template(viewname, **params)


def build_full_model(model):
    if not 'type' in model['fields']:
        model['fields']['type'] = {
            'fieldName': 'type',
            'requiredType': 'http://schema.org/Text',
            'description': ['The type of object, in this case ' + model['type']],
            'example': model['type'],
            'requiredContent': model['type']
        }
        model['requiredFields'].append('type')
    if model['hasId']:
        model['fields']['id'] = {
            'fieldName': 'id',
            'requiredType': 'http://schema.org/url',
            'description': ['A unique url based identifier for the record'],
            'example': ''
        }
        if model['hasId'] and model['sampleId']:
            model['fields']['id']['example'] = model['sampleId'] + '1234'
        model['fields']['identifier'] = {
            'fieldName': 'identifier',
            'description': ['A unique identifier for the record'],
            'example': '1234'
        }
        model['requiredFields'].append('id')
    if not 'recommendedFields' in model:
        model['recommendedFields'] = []
    if not 'requiredFields' in model:
        model['requiredFields'] = []
    model['optionalFields'] = [field for field in model['fields'] if field
                               not in model['requiredFields'] and field not in model['recommendedFields']]
    model['requiredFields'] = sorted(model['requiredFields'])
    model['recommendedFields'] = sorted(model['recommendedFields'])
    model['optionalFields'] = sorted(model['optionalFields'])
    for field in model['fields']:
        model['fields'][field]['markdown'] = []
        for item in model['fields'][field]['description']:
            model['fields'][field]['markdown'].append(Markup(markdown.markdown(item)))
        model['fields'][field]['inlineExample'] = json.dumps(
            model['fields'][field]['example'], indent=4, sort_keys=True)
    return model


def build_example_json(model):
    example = {}
    for field in model['fields']:
        example[field] = model['fields'][field]['example']
    example['type'] = model['type']
    if model['hasId'] and model['sampleId']:
        if not '#' in model['sampleId']:
            example['id'] = model['sampleId'] + '1234'
            example['identifier'] = 1234
        else:
            example['id'] = model['sampleId']
    return example
