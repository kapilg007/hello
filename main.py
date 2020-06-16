from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, The code is working fine."


if __name__ == '__main__':
    app.run()
