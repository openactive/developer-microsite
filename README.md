# developer-microsite
Microsite for the OpenActive Developer engagement

## steps to build locally

Install Python 3. It will need to be 3.6 if it's to be deployed to AWS. Best distribution for good collection of tools is Anaconda - https://www.anaconda.com/download/

`virtualenv -p python3 env`

`source activate env`

`pip install -r requirements.txt`

`export FLASK_APP=app.py`
`export FLASK_DEBUG=1`

change directory into the app/ folder

`flask run`

## deploying to AWS Lambda using Zappa

The Flask application is deployed to AWS Lambda using Zappa (https://github.com/Miserlou/Zappa)

There are good instructions for how to deploy a Zappa app in their README (https://github.com/Miserlou/Zappa#initial-deployments)

A current set of Zappa settings are included with this commit. These are the settings for an app running in Chris' AWS account

1. First create an account with AWS

2. Ensure your AWS credentials are correctly set - https://aws.amazon.com/blogs/security/a-new-and-standardized-way-to-manage-credentials-in-the-aws-sdks/. The AWS CLI is the easiest way to do this, install it here - https://aws.amazon.com/cli/ - use the `aws configure` command to set access key and secret and to set the default region.

3. Within the app folder, run `zappa init`, you'll be asked to give a name for the function. This will be the function that you attach the CNAME to later. One error you may see is "Error: Zappa requires an active virtual environment!" if you see this then set a pointer to the virtual environment you set up to build and run locally `export VIRTUAL_ENV=/path/to/your/virtualenv`

4.  Then run `zappa deploy` when it runs it will give you a link to the Lambda function with an API Gateway instance running in front of it. The currently deployed function is at https://9se5s3jvil.execute-api.eu-west-2.amazonaws.com/dev. The /dev at the end of the URL is the API Gateway stage

5. You'll now need to log into the AWS Console to create a certificate for the CNAME. You'll need to do this in the US-East-1 region - https://console.aws.amazon.com/console/home?region=us-east-1

Now enter Certificate Manager and request a certificate.

6. Switch regions back to where the app is hosted and navigate to API Gateway and then pick Custom Domain Names from the menu and select Create Custom Domain Name

7. Enter the CNAME and select the correct Certificate from the drop down list

8. Under Base Path Mappings enter "/" in the Path and select your API Gateway instance from the dropdown list. Ensure you select the dev stage so that any requests for "/" are proxied to "/dev"

9. Finally point your CNAME at the provided Target Domain Name
