import re
import collections

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
        return render_template("secure_upload.html", title='File Upload', basePath=basePath)

    @staticmethod
    def post():
        errors = []
        new_file = None
        words_count = None
        uniq_count = None
        files = request.files.get('new_file')
        errors.append(type(files))
        if not all(files):
            errors.append("Missing Required Fields")

        if files:
            try:
                new_file = files.read()
                errors.append(new_file)
                words = re.split("W+", new_file.lower())
                words_count = len(words)
                uniq_count = collections.Counter()
            except:
                errors.append("Problem reading uploaded file.")

        if not errors:
            output_text = 'Last File received: Words(' + str(words_count) + ') Uniq(' + str(uniq_count) + ')'
            return render_template("secure_upload.html", title='File Received', output_text=output_text, basePath=basePath)

        else:
            return render_template("secure_upload.html", title='Feed ME!!!', errors=errors, basePath=basePath)

app.add_url_rule("/file_upload", view_func=Upload.as_view('users'))

@app.route("/contact/provisioning/certificate_upload/finished", methods=('GET',))
def upload_complete():
    return render_template("secure_upload_complete.html", title='File Upload', pgActive='About', basePath=basePath)

@app.route("/<path:path>")
def send_static_asset(path):
    return send_from_directory(app.static_folder, path)

@app.route("/", methods=('GET',))
def index():
    return render_template("secure_upload.html", title='File Upload', basePath=basePath)

if __name__ == "__main__":
    app.run(debug=True)
