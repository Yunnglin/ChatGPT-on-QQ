from flask import Flask, request
import requests
import yaml
from typing import Tuple

app = Flask(__name__)

import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

def get_host_port() -> Tuple[str, int]:
    with open('./config.yml', 'r', encoding='utf-8') as f:
        obj = yaml.load(f.read(), Loader = yaml.FullLoader)
    url = obj['servers'][0]['http']['post'][0]['url']
    host, port = url.replace('http://', '').split(':')
    return str(host), int(port)

def openai_reply(question) -> str:
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    choices = response['choices']
    first_item = choices[0]
    return first_item['text']
    

@app.route('/', methods=["POST"])
def post_data():
    raw_package: dict = request.get_json()
    if 'message_type' in raw_package:
        message_type = raw_package['message_type']
        user_id = raw_package['sender']['user_id']
        message = raw_package['message']
        res = openai_reply(message)
        get_request = "http://127.0.0.1:5700/send_private_msg?user_id={}&message={}".format(user_id, res)
        # 发送消息
        requests.get(get_request)

    return 'ok'

if __name__ == '__main__':
    from gevent import pywsgi

    host, port = get_host_port()
    server = pywsgi.WSGIServer(
        listener=(host, port),
        application=app,
        log=None
    )
    server.serve_forever()