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
        output_text = None
        #words_count = 0
        #files = request.files.get('new_file')
        files = request.files['new_file']
        if files:
            try:
                new_file = files.read()
                #errors.append(new_file)
                data = new_file.decode()
                #data = new_file
                #errors.append(data)
                text_data = re.split("\W+", data)
                #text_data = re.split("W+", data)
                ### Print out list items in text_data for debug
                #for item in text_data:
                    #errors.append(item)
                #errors.append(type(text_data))
                #for word in text_data:
                    #errors.append(word)
                words_count = len(text_data) - 1
                #errors.append(words_count)
                coll_counted = collections.Counter(text_data)
                #for record in coll_counted.keys():
                    #errors.append(record)
                key_count = len(coll_counted.keys()) - 1
                #errors.append(key_count)
                if words_count == 0 and key_count == 0:
                    output_text = "File Received... But it was empty. Word Count:{}, Uniq-Word Count:{}".format(words_count, key_count)
                else:
                    output_text = "File Received. Thanks! Word Count:{}, Uniq-Word Count:{}".format(words_count, key_count)
                #errors.append(output_text)
            except:
                errors.append("Problem parsing uploaded file. Is it TEXT?")
        else:
            errors.append("Missing File")
        if not errors and output_text is not None:
            return render_template("secure_upload.html", title='File Received', output_text=output_text, basePath=basePath)
        else:
            return render_template("secure_upload.html", title='File Upload', output_text=output_text, errors=errors, basePath=basePath)

app.add_url_rule("/file_upload", view_func=Upload.as_view('users'))


@app.route("/<path:path>")
def send_static_asset(path):
    return send_from_directory(app.static_folder, path)

@app.route("/", methods=('GET',))
def index():
    return render_template("secure_upload.html", title='File Upload', basePath=basePath)

if __name__ == "__main__":
    app.run(debug=True)
