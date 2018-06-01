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

## using the prototype feed checking

Currently the feed checking prototype is only on the 'feed-checker' branch.

Check out that branch and follow the instructions above for building locally. The requirements are currently the same so you can switch branches without rebuilding the virtual environment.

Then navigate to http://127.0.0.1:5000/tools/check-feed

A recent version can also be run on https://developer.openactive.io/tools/check-feed

## how the feed checking currently works

The prototype currently follows the following workflow.

It loads the machine readable models and builds a canonical model of what an Event should look like (including all sub models which have been derived from Schema/SKOS)

It walks the provided event, checking the field types against the relevant equivalent field in the definition in the canonical model. This generates a JSON document of errors/results which are in the same structure as the Event.

It walks the canonical model, checking for fields which are required/recommended but are missing and highlighting fields which are present in the feed but not the model (sometimes these are misnamed, sometimes they're beta namespaced fields, sometimes they're just additional for each provider). This generates as JSON document of errors in the same structure as the Event.

Finally the two JSON documents, one for field type results, one for missing/additional/misnames field results are filtered as to the level of event if the user requires.

### known issues with feed checking

- at the moment you can only check an event block at a time, we need to implement checking a whole feed
- some of the models don't yet have requiredTypes (but this will change soon)
- there's currently no format checking i.e. doesn't check if an ISO8601 DateTime is really an ISO8601 DateTime
- it currently ignores optional field types and will only look at the requiredType/model and test whether that is currently being used (it's less permissive than the spec for now, but that will change)
- it doesn't yet check whether the value is one of the options, it does however look at requiredContent (again, this will change)
- we're not yet currently dealing with SubEvent or SuperEvent
