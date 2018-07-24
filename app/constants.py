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

models_path = path.abspath('../node_modules/openactive-data-models/src/models')