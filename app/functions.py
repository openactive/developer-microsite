from flask import Markup, render_template
import markdown
import json

import constants
import logging


def render_view(viewname, params):
    params['navbar_items'] = constants.navbar_items
    return render_template(viewname, **params)


def read_file(path, json_format=True):
    if json_format:
        file_contents = json.loads(open(path, 'r').read())
    else:
        file_contents = open(path, 'r').read()
    return file_contents


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
    model = build_field_arrays(model)
    model = build_option_html_from_markdown(model)
    model = build_field_description_html_from_markdown(model)
    model = build_description_html_from_markdown(model)
    model = build_named_examples(model)
    return model


def build_option_html_from_markdown(model):
    if 'requiredOptions' in model and model['requiredOptions'] is not None:
        for option in model['requiredOptions']:
            option['markdown'] = []
            for paragraph in option['description']:
                option['markdown'].append(Markup(markdown.markdown(paragraph)))
    return model


def build_named_examples(model):
    if 'namedExamples' in model and model['namedExamples'] is not None:
        for example in model['namedExamples']:
            example['markdown'] = []
            for paragraph in example['description']:
                example['markdown'].append(
                    Markup(markdown.markdown(paragraph)))
            named_example = read_file('examples/' + example['example'], json_format=True)
            example['example'] = json.dumps(named_example, indent=4, sort_keys=True)
    return model


def build_field_description_html_from_markdown(model):
    for field in model['fields']:
        model['fields'][field]['markdown'] = []
        for paragraph in model['fields'][field]['description']:
            model['fields'][field]['markdown'].append(Markup(markdown.markdown(paragraph)))
        model['fields'][field]['inlineExample'] = json.dumps(
            model['fields'][field]['example'], indent=4, sort_keys=True)
    return model


def build_description_html_from_markdown(model):
    if 'description' in model and model['description'] is not None:
        for section in model['description']['sections']:
            section['markdown'] = []
            for paragraph in section['paragraphs']:
                section['markdown'].append(
                    Markup(markdown.markdown(paragraph)))
    return model


def build_field_arrays(model):
    if not 'recommendedFields' in model:
        model['recommendedFields'] = []
    if not 'requiredFields' in model:
        model['requiredFields'] = []
    if not 'optionSetFields' in model:
        model['optionSetFields'] = []
    if 'requiredOptions' in model:
        for option in model['requiredOptions']:
            for field in option['options']:
                if field not in model['optionSetFields']:
                    model['optionSetFields'].append(field)
    model['optionalFields'] = [field for field in model['fields'] if field
                               not in model['requiredFields'] and field not in model['recommendedFields'] and field not in model['optionSetFields']]
    model['requiredFields'] = sorted(model['requiredFields'])
    model['recommendedFields'] = sorted(model['recommendedFields'])
    model['optionalFields'] = sorted(model['optionalFields'])
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
