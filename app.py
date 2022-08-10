import requests
import json
from flask import Flask
from flask import request
from fast_bitrix24 import Bitrix

webhook = 'https://vc4dk.bitrix24.ru/rest/311/r1oftpfibric5qym/'
b = Bitrix(webhook)

app = Flask(__name__)


@app.route('/', methods=['POST', 'HEAD', 'GET'])
def result():
     print(request.form)
     for i in request.form:
         print(i)
     return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0')