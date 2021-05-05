from flask import Flask, render_template, request, redirect, Blueprint
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import timeit
import pandas as pd
from matplotlib import pyplot,style
import requests

bp = Blueprint('bpstatistics', __name__, url_prefix='/statistics')

@bp.route('/topsector', methods=['GET', 'POST'])
def topsector():

@bp.route('/upperitems', methods=['GET', 'POST'])
def upperitems():

@bp.route('/loweritems', methods=['GET', 'POST'])
def loweritems():

@bp.route('/marketcap', methods=['GET', 'POST'])
def marketcap():