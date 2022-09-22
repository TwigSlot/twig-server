from flask import render_template

def list_users():
    return render_template('admin.html')