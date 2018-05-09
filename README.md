# developer-microsite
Microsite for the OpenActive Developer engagement

## steps to build locally

Install Python 3. It will need to be 3.6 if it's to be deployed to AWS. Best distribution for good collection of tools is Anaconda - https://www.anaconda.com/download/

virtualenv -p python3 env

source activate env

pip install -r requirements.txt

export FLASK_APP=app.py
export FLASK_DEBUG=1

change directory into the app/ folder

flask run

## deploying to AWS Lambda using Zappa

Coming soon...
