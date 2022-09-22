from flask import render_template
import requests
from requests import Response
import os
import json

KETO_READ_URL = os.environ.get('KETO_READ_URL')
KETO_WRITE_URL = os.environ.get('KETO_WRITE_URL')

def list_users():
    ret : Response = requests.get(f"{KETO_READ_URL}/relation-tuples")
    return render_template('admin.html', ret = json.loads(ret.text))
    data = {
        "subject_id": "cat lady",
        "relation": "owner",
        "namespace": "videos",
        "object": "/cats",
    }
    check : Response = requests.get(f"{KETO_READ_URL}/relation-tuples/expand", params = data)
    return render_template('admin.html', ret = check.text)
