


'''
Operations:
- GET: Accepts a locale. Return JSON in response body
- PUT/POST: Accepts a dictionary, modifies the nav JSON, returns the updated JSON and uploads to S3
- DELETE: Accepts a uid. If the key exists, then delete the entry, returns the updated JSON and uploads to S3
'''
import json
import boto3
from flask import Flask, request, jsonify, render_template
from http import HTTPStatus

app = Flask(__name__)

bucket = 'lll-nonprod-shopapp-us-west-2'
nav_key = 'sandbox/products/categories/{}.json'
locale_key = 'sandbox/products/categories/locales.json'


@app.route('/navigation', methods=['GET'])
def get_navigation():
    locale = request.args.get('locale')

    accepted_locales = ['en_CA', 'fr_CA', 'en_US', 'en_AU', 'en_GB']

    if locale not in accepted_locales:
        return page_not_found('Invalid locale')

    else:
        s3 = boto3.client('s3')

        s3.download_file(bucket, nav_key.format(locale), 'temp.json')

        with open('temp.json', 'r+b') as f:
            data = json.load(f)

            #print(data)

    return jsonify(data)


@app.route('/locales', methods=['GET'])
def get_locales():
    s3 = boto3.client('s3')

    s3.download_file(bucket, locale_key, 'temp.json')
    with open('temp.json', 'r+b') as f:
        data = json.load(f)

    return jsonify(data)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/navigation', methods=['POST'])
def update_navigation():
    content_type = request.args.get('application/json')
    content = request.args.get('changes')
    pass