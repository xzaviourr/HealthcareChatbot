import re
from Database.connection import db_connect

def disease_search(list_of_properties):
    """
    Search disease based on the properties given
    :param list_of_properties: List of properties, list element of type [property_type, property_value, relationship_type]
    :return: List of diseases having all the properties
    """
    graph = db_connect()
    query = ""
    rel_query = "(x:disease)-[:%s]->(:%s{name:'%s'})"
    for p_type, p_value, r_type in list_of_properties:
        query = query + rel_query%(r_type, p_type, p_value) + ","

    query = query[:len(query)-1]
    full_query = f"MATCH {query} \nRETURN x"
    result = graph.run(full_query)
    return result

def suggest_question(list_of_diseases):
    graph = db_connect()
    list_of_symptoms = dict()
    for disease in list_of_diseases:
        query = f"""
            MATCH (x:disease)-[:has_symptom]->(y:symptom)
            WHERE x.name = "{disease}"
            RETURN y"""
        result = graph.run(query)
        symptoms = [symptom[0]['name'] for symptom in result]
        list_of_symptoms[disease] = symptoms      

    for k in list_of_symptoms.keys():
        print(k, list_of_symptoms[k])
        print("\n\n")


l = [['symptom', 'fatigue', 'has_symptom']]
result = disease_search(l)

list_of_diseases = list()
for row in result:
    list_of_diseases.append(row[0]['name'])   

suggest_question(list_of_diseases)
