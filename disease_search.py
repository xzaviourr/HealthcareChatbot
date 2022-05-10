import re
from Database.connection import db_connect
import json

class KGSearchAlgo:
    def __init__(self):
        self.last_attribute = None
        self.user_attributes = []
        self.list_of_diseases = []

    def modify_property(self, input):
        if input.lower() == "yes":
            self.user_attributes.append(['symptom', self.last_attribute, 'has_symptom'])
        else:
            self.user_attributes.append(['symptom', input, 'has_symptom'])
        
        self.disease_search()
        return self.suggest_question()

    def disease_search(self):
        """
        Search disease based on the properties given
        :return: List of diseases having all the properties
        """
        graph = db_connect()
        query = ""
        rel_query = "(x:disease)-[:%s]->(:%s{name:'%s'})"
        for p_type, p_value, r_type in self.user_attributes:
            query = query + rel_query%(r_type, p_type, p_value) + ","

        query = query[:len(query)-1]
        full_query = f"MATCH {query} \nRETURN x"
        result = graph.run(full_query)
        
        self.list_of_diseases = list()
        for row in result:
            self.list_of_diseases.append(row[0]['name'])   

    def get_properties(self, disease):
        graph = db_connect()
        query = f"""
        MATCH (x:disease)-[rel]->(y)
        WHERE x.name = "{disease}"
        RETURN rel
        """
        results = graph.run(query).data()
        disease_node = results[0]['rel'].nodes[0]
        disease_properties = {
            'propogation_way': disease_node['propogation_way'] if 'propogation_way' in disease_node.keys() else 'NONE',
            'cure_last_time': disease_node['cure_last_time'] if 'cure_last_time' in disease_node.keys() else 'NONE',
            'cost_money': disease_node['cost_money'] if 'cost_money' in disease_node.keys() else 'NONE',
            'name': disease_node['name'] if 'name' in disease_node.keys() else 'NONE',
            'description': disease_node['description'] if 'description' in disease_node.keys() else 'NONE',
            'cured_probability': disease_node['cured_probability'] if 'cured_probability' in disease_node.keys() else 'NONE',
            'get_probability': disease_node['get_probability'] if 'get_probability' in disease_node.keys() else 'NONE'
        }
        relationship = re.compile("\((.*)\)-\[:(.*) \{\}\]->\((.*)\)")
        for row in results:
            disease, rel, feature = re.findall(relationship, str(row['rel']))[0]
            if rel in disease_properties.keys():
                disease_properties[rel].append(feature)
            else:
                disease_properties[rel] = [feature]

        return disease_properties

    def similarity_score(self, disease_details):
        """
        Technical similarity - has_symptom, has_recommended drugs, has_cause, required_check
        Spread similarity - propogation_way, 
        Personal similarity - prone_to, do_eat, not_eat, recommended_eat 
        Statistical similarity - cure_last_time, get_probability
        other features - cost_money, name, description
        """
        similarity = {}
        # no_of_diseases = len(disease_details)
        # technical_similarity_metric = ['has_symptom', 'has_recommended_drugs', 'has_cause', 'required_check']
        # spread_similarity_metric = ['propogation_way']
        # personal_similarity_metric = ['prone_to', 'do_eat', 'not_eat', 'recommended_eat']
        # statistical_similarity_metric = ['cure_last_time', 'cured_probability', 'get_probability']

        for feature in disease_details[0].keys():
            similarity[feature] = {}

        for disease in disease_details:
            for feature in disease.keys():
                if feature in ["has_symptom", "cured_by_department", "cured_by", "required_check", "has_recommended_drug",
                "has_common_drug", "do_eat", "recommended_eat", "has_cause", "prone_to"]:
                    for ele in disease[feature]:
                        if ele in similarity[feature].keys():
                            similarity[feature][ele] += 1
                        else:
                            similarity[feature][ele] = 1
                
                if feature in ["propogation_way"]:
                    if disease[feature] in similarity[feature].keys():
                        similarity[feature][disease[feature]] += 1
                    else:
                        similarity[feature][disease[feature]] = 1

                if feature == "cure_last_time":
                    pass
                if feature == "cost_money":
                    pass
                if feature in ["name", "description", "cured_probability"]:
                    pass
                if feature == "accompanies":
                    pass

                if feature in similarity.keys():
                    disease[feature]
            
        for feature in similarity.keys():
            similarity[feature] = dict(sorted(similarity[feature].items(), key=lambda item: item[1], reverse=True))

        return similarity
        
    def suggest_question(self):
        disease_details = list()
        for d in self.list_of_diseases:
            prop = self.get_properties(d)
            disease_details.append(prop)

        scores = self.similarity_score(disease_details)
        no_of_diseases = len(disease_details)
        
        attribute = ""
        for val in scores['has_symptom'].keys():
            if scores['has_symptom'][val] != no_of_diseases:
                attribute = val
                break

        return f"Do you have this symptom - {attribute}"


obj = KGSearchAlgo()
obj.modify_property("fatigue")