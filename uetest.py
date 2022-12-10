# coding: utf-8
from flask import Flask
from flask import render_template
from flask import request, make_response

from datetime import timedelta
import json
from libue.client import UETestClient
import sys, os

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder,static_folder=static_folder)
else:
    app = Flask(__name__)


app.config['JSON_AS_ASCII'] = False

global client_dict, action_dict, uid
client_dict = {}
action_dict = {}
uid = 0
def jsonfy(json_dict):
    return json.dumps(json_dict, indent=2, ensure_ascii=False )

def json2proto(json_string):
    pass

@app.route("/")
def root():
    global uid
    uid += 1
    username = f'user-{uid}'
    rsp = make_response(render_template('test.html'))
    rsp.set_cookie('username', username)
    return rsp

@app.route('/disconnect')
def disconnect():
    global client_dict
    username = request.cookies.get('username')
    print(f'disconnect user : {username}')
    client_dict.pop(username)
    return "Success"

@app.route('/connect/<address>')
def connect(address):
    global client_dict
    username = request.cookies.get('username')
    [host, port] = address.split(':')
    print(f'connect user {username}')
    print(f"address: {host} {port}")
    # if host == '127.0.0.1' : 
    #     return "Success"
    # else :
    #     return "False"
    try:
        client = UETestClient(host, port)
        client_dict[username] = client
        return "Success"
    except Exception as e:
        client = None
        print(e)
        return f"\n\t{e.details()}  \n\t{e.debug_error_string()}"


@app.route('/send/<jstr>')
def exec_command(jstr):
    global client_dict
    username = request.cookies.get('username')
    client = client_dict.get(username, None)
    if not client:
        return jsonfy({"msg": "Connect Disconnected", 'err_code': 1})
    try:
        req = json.loads(jstr)
    except Exception as e:
        return jsonfy({"msg": "json串异常",'err_code': 2,})
    try:
        ret = client.execute(req)
    except Exception as e:
        return jsonfy({"msg": f"\n\t{e.details()}  \n\t{e.debug_error_string()}", 'err_code': 100,})
    return jsonfy({"msg": "success", "err_code": 0, "response": ret})



@app.route('/fastaction')
def fast_action():
    global action_dict
    with open('actions.json', encoding='utf-8') as f:
        actions = json.load(f)
    action_dict = {k: json.dumps(v, indent=2) for k, v in actions.items()}
    ret = ' '.join(action_dict.keys())
    return ret

@app.route('/getaction/<action>')
def gen_action(action):
    global action_dict
    return action_dict.get(action)

if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    # app.run(host='localhost', port='5000')
    from waitress import serve
    print(' * Running on http://localhost:5000/ (Press CTRL+C to quit)')
    serve(app, host='0.0.0.0', port=5000, threads=30)  # WAITRESS!
