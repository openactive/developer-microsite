from os import path

content_items = ['index', 'specifications', 'getting-started', 'guidance']

navbar_items = [
    {
        "text": "Getting Started",
        "path": "/getting-started"
    },
    {
        "text": "Specifications",
        "path": "/specifications"
    },
    {
        "text": "Models",
        "path": "/models"
    },
    {
        "text": "Guidance",
        "path": "/guidance"
    },

]

models_package_path = path.abspath('../node_modules/@openactive/data-models/versions/');
models_version = '2.x'

models_path = path.join(models_package_path, models_version, 'models')
examples_path = path.join(models_package_path, models_version, 'examples')