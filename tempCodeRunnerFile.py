from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "heelo this is me"
if __name__ == "__main__":
    app.run()