from flask import Flask

app = Flask(__name__)

from main import bp as mainbp
from check import bp as checkbp
from statistics import bp as statisticsbp
app.register_blueprint(mainbp)
app.register_blueprint(checkbp)
app.register_blueprint(statisticsbp)

if __name__ == '__main__':
    app.run(host='127.0.0.1')