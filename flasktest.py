from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 하이 '


if __name__ == '__main__':
    app.run("0.0.0.0", port=8000)