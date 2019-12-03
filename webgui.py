from flask import Flask, redirect, send_from_directory, session, request
import os
import json
from flask_cors import CORS

app = Flask(__name__,
            static_url_path="/docs",
            static_folder="docs")
CORS(app)

@app.route('/', methods=['GET'])
def app_index():
    return redirect('/index.html')

@app.route('/index.html', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/api/compile', methods=['GET','POST'])
def compile():
    src = request.get_json()['src']
    with open('temp.c', 'w+') as f:
        f.write(src)

    r = os.popen('python3 pcc.py temp.c')
    text = r.read()
    r.close()

    if text == '':
        text = 'success!'
        r = os.popen('cat temp.s')
        asm = r.read()
        r.close()

        return json.dumps({"msg": text, "asm": asm})


    return json.dumps({"msg": text, "asm": "Compiled failed!"})

@app.route('/api/link', methods=['GET','POST'])
def link():
    src = request.get_json()['src']
    with open('temp.s', 'w+') as f:
        f.write(src)

    r = os.popen('clang temp.s -o temp')
    text = r.read()
    r.close()

    if text == '':
        text = 'success!'

    return json.dumps({"msg": text})

@app.route('/api/run', methods=['GET','POST'])
def run():
    input_ = request.get_json()['input']

    with open('temp.in', 'w+') as f:
        f.write(input_)

    r = os.popen('./temp < temp.in')
    text = r.read()
    r.close()

    return json.dumps({"output": text, "msg": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)