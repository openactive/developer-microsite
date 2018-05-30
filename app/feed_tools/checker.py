import json
import logging
import sys

# define some constants

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
else:
    string_types = basestring,

model_directory = 'models'


# standards are not validated against yet, but should be
def load_standard(filename):
    if '.json' not in filename:
        filename = filename + '.json'
    if '$' in filename:
        filename = filename.replace('$', '')
    filename = standards_directory + '/' + filename
    file = open(filename, 'r')
    return json.loads(file.read())

# TODO how to represent permissive field types better
# model loader
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
    # add in common fields, such as type and id if the model has an id
    json_representation['type'] = {
        'requiredType': 'http://schema.org/Text',
        'requiredField': True,
        'requiredContent': thisjson['type']
    }
    if thisjson['hasId']:
        json_representation['identifier'] = {
            'optionalField': True
        }
        json_representation['id'] = {
            'requiredType': 'http://schema.org/url',
            'requiredField': True
        }
    # iterate through the model's fields
    for field in thisjson['fields']:
        # if a field points at another model, load it
        if 'model' in thisjson['fields'][field]:
            json_representation[field] = load_model_to_test(thisjson['fields'][field]['model'])
            # set the required type to the model
            json_representation[field]['requiredType'] = thisjson['fields'][field]['model'].replace(
                '#', '')
            # TODO consider refactoring this into a function
            try:
                if field in thisjson['requiredFields']:
                    json_representation[field]['requiredField'] = True
                elif field in thisjson['requiredOptions']:
                    json_representation[field]['requiredOption'] = True
                elif field in thisjson['recommendedFields']:
                    json_representation[field]['recommendedField'] = True
                else:
                    json_representation[field]['optionalField'] = True
            except:
                json_representation[field]['optionalField'] = True
        else:
            # the field does not point to a model, so we'll set up the field definition
            # remove unused field definition elements
            del thisjson['fields'][field]['example']
            del thisjson['fields'][field]['description']
            del thisjson['fields'][field]['fieldName']
            if 'sameAs' in thisjson['fields'][field]:
                del thisjson['fields'][field]['sameAs']
            # special case for @context and the inability of Python to reference it
            if field == '@context':
                json_representation['context'] = thisjson['fields']['@context']
            else:
                json_representation[field] = thisjson['fields'][field]
            # again refactor this into a shared function
            try:
                if field in thisjson['requiredFields']:
                    json_representation[field]['requiredField'] = True
                elif field in thisjson['requiredOptions']:
                    json_representation[field]['requiredOption'] = True
                elif field in thisjson['recommendedFields']:
                    json_representation[field]['recommendedField'] = True
                else:
                    json_representation[field]['optionalField'] = True
            except:
                json_representation[field]['optionalField'] = True
            # load the standard if the field uses one (not validated against yet)
            if 'standard' in field:
                json_representation[field]['standard'] = load_standard(field['standard'])
    return json_representation

# function to check feed field types
# TODO possibly rename this function
def check_feed(json_to_check, model_to_test, location_of_sessions=None, array_pointer=None, in_data=False):

    if location_of_sessions is not None:
        json_to_check = json_to_check[location_of_sessions]

    if array_pointer is not None:
        json_to_check = json_to_check[array_pointer]

    if in_data is True:
        json_to_check = json_to_check['data']

    forward_errors = test_feed_node(json_to_check, model_to_test)

    return forward_errors


# function to check feed field presence
# TODO possibly rename this function
def check_canonical(json_to_check, model_to_test, location_of_sessions=None, array_pointer=None, in_data=False):
    if location_of_sessions is not None:
        json_to_check = json_to_check[location_of_sessions]

    if array_pointer is not None:
        json_to_check = json_to_check[array_pointer]

    if in_data is True:
        json_to_check = json_to_check['data']

    reverse_errors = test_canonical_node(json_to_check, model_to_test)

    return reverse_errors

### TESTS ###

# test for whether the field value is a URL
def test_is_url(value, required=True):
    if isinstance(value, string_types):
        if value[0:4] == 'http':
            errors = {'success': True, 'message': 'The field is the correct type (URL).'}
        else:
            errors = {
                'success': False, 'message': 'The field should be a well formed URL, but is not.', 'errorType': 'incorrect_value_format'}
    else:
        errors = {'success': False,
                  'message': 'The field must be String, but is not.', 'errorType': 'incorrect_value_format'}
    return errors


# test for whether the field is a String
def test_is_text(value, required=True):
    if isinstance(value, string_types):
        errors = {'success': True, 'message': 'The field is the correct type (String).'}
    else:
        errors = {'success': False,
                  'message': 'The field must be String, but is not.', 'errorType': 'incorrect_value_format'}
    return errors


# test for whether the field is an Integer
def test_is_integer(value, required=True):
    if isinstance(value, int):
        errors = {'success': True, 'message': 'The field is the correct type (Integer).'}
    else:
        errors = {'success': False,
                  'message': 'The field must be Integer, but is not,', 'errorType': 'incorrect_value_format'}
    return errors


# test for whether the field is a Float
def test_is_float(value, required=True):
    if isinstance(value, float):
        errors = {'success': True, 'message': 'The field is the correct type (Float).'}
    else:
        errors = {'success': False, 'message': 'The field must be Float, but is not.', 'errorType': 'incorrect_value_format'}
    return errors


# test for whether the field is a datetime
# TODO fill out test
# TODO also test for date
def test_is_datetime(value, required=True):
    return {}


# test for whether specific content is present
def test_content(value, content):
    if value.lower() == content.lower():
        errors = {'success': True, 'message': 'Required content is present'}
    else:
        errors = {'success': False,
                  'message': 'Required content is absent or incorrect', 'errorType': 'incorrect_content'}
    return errors


# switch for tests
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


# TODO use this, at the moment we only test for required types
def test_preferred_type(fieldname, value, requiredType, standard=False, required=False):
    return test_required_type(fieldname, value, requiredType, standard, required)


# testing an individual field
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
    errors['value'] = value
    errors['tests'] = tests
    return errors


# testing a dictionary node
# TODO include how to test within arrays
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
                errors[item] = {'success': True, 'value': node[item], 'message': testitem +
                                ' is not yet represented in the Open Active models. Please check if a suitable field exists.', 'errorType': 'field_may_be_misnamed'}
    return errors

# TODO rename this, we're looking for missing fields
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
                if 'requiredField' in testnode[item]:
                    errors[item] = {'success': False, 'errorType': 'missing_required_field',
                                    'message': 'The Event is missing the required field, ' + item}
                if 'recommendedField' in testnode[item]:
                    errors[item] = {'success': False, 'errorType': 'missing_recommended_field',
                                    'message': 'The Event is missing this recommended field, ' + item}
    return errors
