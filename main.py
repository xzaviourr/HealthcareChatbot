from hashlib import new
from turtle import pos
from flask import Flask, jsonify, request
from User import User
from disease_search import disease_search
from spello.model import SpellCorrectionModel


class HealthcareChatbot:
    def __init__(self):
        self.users = dict()
        self.start_api()

        self.spell_correcter = SpellCorrectionModel(language='en')
        self.spell_correcter.load('Data/model.pkl/model.pkl')

    def start_api(self):
        api = Flask(__name__)

        @api.route('/', methods = ['GET'])
        def show_homepage():
            return "HealthCare Chatbot API running !!!"

        @api.route('/', methods = ['POST'])
        def new_message():
            print("Started")
            input_txt = request.get_json()
            user_id = input_txt['id']
            user_text = input_txt['text']
            
            id, reply = self.process_request(user_id = user_id, user_text = user_text)

            return jsonify({
                "id": id,
                "text": reply
            })
        
        api.run()

    def process_request(self, user_id, user_text):
        current_user = None
        if user_id == "NULL":
            new_user = User()
            user_id = new_user.id
            self.users[new_user.id] = new_user
            current_user = new_user
        else:
            current_user = self.users[user_id]
        
        intent, entities = self.apply_nlu(user_text)
        if intent == "add_symptom":
            for ele in entities:
                current_user.add_symptom(ele)
                reply = "Symptom added"

        elif intent == "ask_disease":
            result = disease_search(list_of_properties=current_user.get_knowledge_graph_query())
            possible_diseases = list()
            for line in result:
                possible_diseases.append(line[0]['name'])
            
            reply = "Possible diseases can be : "
            for ele in possible_diseases:
                reply += ele + ", "
            reply = reply[:-1]
        
        return user_id, reply

    def apply_nlu(self, text):
        try:
            intent, entity = text.split(":")
            entities = entity.split(',')
        except:
            intent = text
            entities = []
        
        return intent, entities

obj = HealthcareChatbot()