from typing import Counter


class User:
    """
    Every new user will be an object of this class. It stores all the properties of the user, from past medical history to his symptoms,
    diseases, drugs and other things relevant in the diagnosis.
    """
    counter = 0
    def __init__(self):
        self.id = self.counter
        self.counter += 1

        self.symptoms = []
        
    def add_symptom(self, symptom_name):
        self.symptoms.append(symptom_name)

    def get_knowledge_graph_query(self):
        features = list()
        for symptom in self.symptoms:
            features.append(["symptom", symptom, "has_symptom"])
        
        return features