import json
import logging
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
else:
    string_types = basestring,

model_directory = 'models'


def load_standard(filename):
    if '.json' not in filename:
        filename = filename + '.json'
    if '$' in filename:
        filename = filename.replace('$', '')
    filename = standards_directory + '/' + filename
    file = open(filename, 'r')
    return json.loads(file.read())


def load_model_to_test(filename):
    json_representation = {}
    if '.json' not in filename:
        filename = filename + '.json'
    if '#' in filename:
        filename = filename.replace('#', '')
    print("LOADING MODEL " + filename)
    filename = model_directory + '/' + filename
    file = open(filename, 'r')
    thisjson = json.loads(file.read())
    json_representation['type'] = {
        'requiredType': 'http://schema.org/Text',
        'required': True,
        'requiredContent': thisjson['type']
    }
    if thisjson['hasId']:
        json_representation['identifier'] = {
            'optional': True
        }
        json_representation['id'] = {
            'requiredType': 'http://schema.org/url',
            'required': True
        }
    for field in thisjson['fields']:
        if 'model' in thisjson['fields'][field]:
            json_representation[field] = load_model_to_test(thisjson['fields'][field]['model'])
            json_representation[field]['requiredType'] = thisjson['fields'][field]['model'].replace(
                '#', '')
            try:
                if field in thisjson['requiredFields']:
                    json_representation[field]['required'] = True
                elif field in thisjson['requiredOptions']:
                    json_representation[field]['requiredOption'] = True
                elif field in thisjson['recommendedFields']:
                    json_representation[field]['recommended'] = True
                else:
                    json_representation[field]['optional'] = True
            except:
                json_representation[field]['optional'] = True
        else:
            del thisjson['fields'][field]['example']
            del thisjson['fields'][field]['description']
            del thisjson['fields'][field]['fieldName']
            if 'sameAs' in thisjson['fields'][field]:
                del thisjson['fields'][field]['sameAs']
            if field == '@context':
                json_representation['context'] = thisjson['fields']['@context']
            else:
                json_representation[field] = thisjson['fields'][field]
            try:
                if field in thisjson['requiredFields']:
                    json_representation[field]['required'] = True
                elif field in thisjson['requiredOptions']:
                    json_representation[field]['requiredOption'] = True
                elif field in thisjson['recommendedFields']:
                    json_representation[field]['recommended'] = True
                else:
                    json_representation[field]['optional'] = True
            except:
                json_representation[field]['optional'] = True
            if 'standard' in field:
                json_representation[field]['standard'] = load_standard(field['standard'])
    return json_representation


def check_feed(json_to_check, model_to_test, location_of_sessions=None, array_pointer=None, in_data=False):

    if location_of_sessions is not None:
        json_to_check = json_to_check[location_of_sessions]

    if array_pointer is not None:
        json_to_check = json_to_check[array_pointer]

    if in_data is True:
        json_to_check = json_to_check['data']

    forward_errors = test_feed_node(json_to_check, model_to_test)

    return forward_errors


def check_canonical(json_to_check, model_to_test, location_of_sessions=None, array_pointer=None, in_data=False):
    if location_of_sessions is not None:
        json_to_check = json_to_check[location_of_sessions]

    if array_pointer is not None:
        json_to_check = json_to_check[array_pointer]

    if in_data is True:
        json_to_check = json_to_check['data']

    reverse_errors = test_canonical_node(json_to_check, model_to_test)

    return reverse_errors


def test_is_url(value, required=True):
    if isinstance(value, string_types):
        if value[0:4] == 'http':
            errors = {'success': True, 'message': 'The field is the correct type (URL).'}
        else:
            errors = {
                'success': False, 'message': 'The field should be a well formed URL, but is not.', 'level': 'required'}
    else:
        errors = {'success': False,
                  'message': 'The field must be String, but is not.', 'level': 'required'}
    return errors


def test_is_text(value, required=True):
    if isinstance(value, string_types):
        errors = {'success': True, 'message': 'The field is the correct type (String).'}
    else:
        errors = {'success': False,
                  'message': 'The field must be String, but is not.', 'level': 'required'}
    return errors


def test_is_integer(value, required=True):
    if isinstance(value, int):
        errors = {'success': True, 'message': 'The field is the correct type (Integer).'}
    else:
        errors = {'success': False,
                  'message': 'The field must be Integer, but is not,', 'level': 'required'}
    return errors


def test_is_float(value, required=True):
    if isinstance(value, float):
        errors = {'success': True, 'message': 'The field is the correct type (Float).'}
    else:
        errors = {'success': False, 'message': 'The field must be Float, but is not.', 'level': 'required'}
    return errors


def test_is_datetime(value, required=True):
    return {}


def test_content(value, content):
    if value.lower() == content.lower():
        errors = {'success': True, 'message': 'Required content is present'}
    else:
        errors = {'success': False,
                  'message': 'Required content is absent or incorrect', 'level': 'required'}
    return errors


def test_required_type(fieldname, value, requiredType, standard=False, required=True):
    if requiredType == 'http://schema.org/Text':
        errors = test_is_text(value, required)
    elif requiredType == 'http://schema.org/url':
        errors = test_is_url(value, required)
    elif requiredType == 'http://schema.org/DateTime':
        errors = test_is_datetime(value, required)
    elif requiredType == 'http://schema.org/Float':
        errors = test_is_float(value, required)
    elif requiredType == 'http://schema.org/Integer':
        errors = test_is_integer(value, required)
    return errors


def test_preferred_type(fieldname, value, requiredType, standard=False, required=False):
    return test_required_type(fieldname, value, requiredType, standard, required)


def test_feed_field(fieldname, value, tests):
    errors = {}
    if fieldname == 'type':
        if value == tests['requiredContent']:
            errors = {'success': True, 'message': 'Type correctly set as ' + value}
        else:
            errors = {'success': False, 'message': 'Type incorrectly set as ' +
                      value + ', must be ' + tests['requiredContent']}
    elif 'requiredType' in tests:
        errors = test_required_type(fieldname, value, tests['requiredType'])
        if 'success' in errors and errors['success'] == True:
            if 'requiredContent' in tests:
                errors = test_content(value, tests['requiredContent'])
    return errors


def test_feed_node(node, testnode):
    errors = {}
    if isinstance(node, dict):
        for item in node:
            if item == '@context':
                testitem = 'context'
            else:
                testitem = item
            try:
                if 'type' in testnode[testitem]:
                    errors[item] = test_feed_node(node[item], testnode[testitem])
                    if 'type' not in node[item]:
                        errors[item]['success'] = False
                        errors[item]['message'] = 'Item should declare type of object'
                else:
                    errors[item] = test_feed_field(item, node[item], testnode[testitem])
            except:
                errors[item] = {'success': True, 'message': testitem +
                                ' is not yet represented in the Open Active models. '}
    return errors


def test_canonical_node(node, testnode):
    errors = {}
    for item in testnode:
        if item in node:
            if 'type' in testnode[item]:
                if isinstance(node, dict):
                    print('RECURSE ' + item)
                    print(node[item])
                    # TODO recursion of the canonical model
        else:
            if item != 'context':
                if 'required' in testnode[item]:
                    errors[item] = {'success': False, 'level': 'required',
                                    'message': 'The feed is missing the required field, ' + item}
                if 'recommended' in testnode[item]:
                    errors[item] = {'success': False, 'level': 'recommended',
                                    'message': 'The feed is missing this recommended field, ' + item}
    return errors
