import os
import hashlib
import random
from logging.config import dictConfig
import logging
import json


#from werkzeug.utils import secure_filename
from main import *
from flask import Flask, request, Response
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
#from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

UPLOAD_FOLDER = r'/var/www/storage.goai.ru/temp'
file_with_docs_already_done = r'status.txt'
save_json = r'/var/www/python.goai.ru/FlaskApp/json'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Актуатор
@app.route('/actuator/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"})


 # Актуатор. Модель готова принимать и обрабатывать запросы. Все веса загружены, все внешние коннекторы установлены.
@app.route('/actuator/ready', methods=['GET'])
def ready():
    return jsonify({"status": "UP"})


@app.route('/predict', methods=['GET', 'POST'])
def main():
    # сюда добавим файл с уже спаршенными файлами
    already_done = open(file_with_docs_already_done).read().split('\n')
    for i in os.listdir(UPLOAD_FOLDER):
        file_name = os.path.join(UPLOAD_FOLDER, i)
        if file_name in already_done:
            continue
        answer = get_result(file_name)
        new_name = answer['file_name'] + answer['doc_type'] + '.json'
        json.dump(answer, open(os.path.join(save_json, new_name), 'w'))
        ff = open(file_with_docs_already_done, 'a')
        ff.write('\n')
        ff.write(file_name)
        ff.write('\n')
        ff.close()
    return jsonify({"status": "ok!"})
     

 
if __name__ == "__main__":
    app.run()