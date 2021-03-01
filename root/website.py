import re
import requests
import json
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from flask.views import MethodView


basePath = ""
staticBasePath = "/static"
uploadsPath = '/opt/upload/uploads'

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 10485760  # 10 MB

class Upload(MethodView):
    @staticmethod
    def get():
        return render_template("upload.html", title='File Upload', basePath=basePath)

    @staticmethod
    def post():
        errors = []
        links = []
        output = []
        token = None
        #default_guid = ""
        output_text = ""
        try:
            token = request.headers['APP_ACCESS_TOKEN']
            # errors.append(format(request.headers))
        except:
            pass
        if token is None:
            try:
                token = request.form['access_key']
            except:
                pass
        if token is not None:
            # errors.append("Found token:{}".format(token))
            headers = {'Authorization': token, 'Content-Type': 'application/json'}
            user_return = requests.get('https://api-ssl.bitly.com/v4/user', headers=headers)
            #errors.append("UserReturn: {}".format(user_return.text))
            user_json = json.loads(user_return.text)
            #errors.append("UserJson: {}".format(user_json))
            if user_json['default_group_guid'] is not None:
                default_guid = user_json['default_group_guid']
                more_records = True
                links_uri = 'https://api-ssl.bitly.com/v4/groups/' + default_guid + '/bitlinks?size=3'
                while more_records:
                    links_return = requests.get(links_uri, headers=headers)
                    links_json = json.loads(links_return.text)
                    for link in links_json['links']:
                        links.append(link['id'])
                    links_uri = links_json['pagination']['next']
                    if links_uri is "":
                        more_records = False
                if len(links) > 0:
                    for bit_link in links:
                        country_uri = 'https://api-ssl.bitly.com/v4/bitlinks/' + bit_link + '/countries?unit=day&units=3&size=100'
                        country_return = requests.get(country_uri, headers=headers)
                        country_json = json.loads(country_return.text)
                        items = country_json['metrics']
                        if len(items) > 0:
                            for item in items:
                                item_detail = item
                                item_detail['bitlink'] = bit_link
                                output.append(item_detail)
                            #errors.append(format(country_json))
                    if len(output) > 0:
                        output_text = "{'bitlink_hits_by_country':" + format(output) + "}"
            else:
                errors.append("No Group ID available for given access token")
        else:
            errors.append("No accesses token provided. Hint: set header ")
        if not errors and output_text is not None:
            return render_template("empty.html", title='Output', output_text=output_text, basePath=basePath)
        else:
            return render_template("empty.html", title='Error', errors=errors, basePath=basePath)

app.add_url_rule("/file_upload", view_func=Upload.as_view('users'))

@app.route("/<path:path>")
def send_static_asset(path):
    return send_from_directory(app.static_folder, path)

@app.route("/", methods=('GET',))
def index():
    return render_template("upload.html", title='File Upload', basePath=basePath)

if __name__ == "__main__":
    app.run(debug=True)
