from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home!'

@app.route('/test', methods=['POST','GET'])
def test():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')