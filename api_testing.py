from flask import Flask, jsonify, request

api = Flask(__name__)

@api.route('/', methods = ['GET'])
def show_homepage():
    return "HealthCare Chatbot API running !!!"

@api.route('/', methods = ['POST'])
def new_message():
    input_txt = request.get_json()
    print(input_txt['id'])
    print(input_txt['text'])

    return jsonify({
        "id": id,
        "text": "RECIEVED"
    })

api.run()