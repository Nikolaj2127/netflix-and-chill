from flask import Flask, request, jsonify
from app.getQuestion import getQuestion

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/getQuestion")
def getQuestion():

    id_film, image_url, id_user = getQuestion()

    return jsonify({
        "id_film": id_film,
        "image_url": image_url,
        "id_user": id_user
    })

@app.route("/postQuestion")
def postQuestion():
    data = request.get_json()