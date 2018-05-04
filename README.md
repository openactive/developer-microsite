# developer-microsite
Microsite for the OpenActive Developer engagement

## steps to build locally

virtualenv -p python3 env

source activate env

pip install -r requirements.txt

export FLASK_APP=app.py
export FLASK_DEBUG=1

flask run

## deploying to AWS Lambda using Zappa

Coming soon...
