from flask import render_template, request, redirect, url_for
import requests
from requests import Response
import os
import json
import twig_server.app as app

KETO_READ_URL = os.environ.get('KETO_READ_URL')
KETO_WRITE_URL = os.environ.get('KETO_WRITE_URL')

def get_all():
    ret : Response = requests.get(f"{KETO_READ_URL}/relation-tuples")
    return json.loads(ret.text)

def list_relations():
    return render_template('admin.html', ret = get_all())

def check_relation():
    app.app.logger.info([x for x in request.form.items()])
    namespace = request.form.get('namespace')
    object = request.form.get('object')
    relation = request.form.get('relation')
    subject_id = request.form.get('subject_id')
    data = {
        "subject_id": subject_id,
        "relation": relation,
        "namespace": namespace,
        "object": object,
    }
    check : Response = requests.get(f"{KETO_READ_URL}/relation-tuples/check", params = data)
    return render_template('admin.html', check_status = check.text, 
                            ret = get_all(), request = request)