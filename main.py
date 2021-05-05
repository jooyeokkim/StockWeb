from flask import Flask, render_template, request, redirect, Blueprint

bp = Blueprint('bpmain', __name__, url_prefix='/main')
@bp.route('/', methods=['POST', 'GET'])
def main():
    return render_template('main.html')