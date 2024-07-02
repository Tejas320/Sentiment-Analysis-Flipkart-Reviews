import base64
import json

from flask import Flask, request, send_from_directory
from joblib import load
from utils import LABELS, create_input_data

model = load("./data/models/bow_xgb_clf.jlib")
app = Flask(__name__, static_url_path="/static")


@app.get("/")
def home():
    return send_from_directory("static", "index.html")


@app.get("/query")
def get_category():
    data = request.args.get("data")
    data = base64.b64decode(data).decode("utf-8")
    data = json.loads(data)
    print(data)

    pred = model.predict(create_input_data(data["title"], data["text"]))[0]

    return {"title": data["title"], "text": data["text"], "label": LABELS.get(pred)}


app.run("127.0.0.1", 8081, debug=True)
