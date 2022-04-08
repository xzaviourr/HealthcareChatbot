import re
from unicodedata import category
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
    
    list_of_diseases = list()
    for row in result:
        list_of_diseases.append(row[0]['name'])   

    return list_of_diseases

l = [['symptom', 'fatigue', 'has_symptom']]
list_of_diseases = disease_search(l)

def get_disease_properties(disease):
    graph = db_connect()
    query = f"""
    MATCH (x:disease)-[z]->(y)
    WHERE x.name = "{disease}"
    RETURN y
    """
    results = graph.run(query).data()
    properties = dict()
    for node in results:
        name, node_type = node['y']['name'], list(node['y']._labels)[0]
        if node_type in properties.keys():
            properties[node_type].append(name)
        else:
            properties[node_type] = [name]

    return properties
    
# get_disease_properties("lungs")

def similarity_score(disease_details):
    """
    Technical similarity - symptom
    way_to_check_similarity - way_to_check
    cure_similarity - cure_way
    department_similarity - department
    category_similarity -  disease category
    """
    def calculate(attribute):
        similarity = dict()
        for key in disease_details.keys():
            symptoms = disease_details[key][attribute]
            for symptom in symptoms:
                if symptom in similarity.keys():
                    similarity[symptom] += 1
                else:
                    similarity[symptom] = 1
    
        for key in similarity.keys():
            similarity[key] = (similarity[key]*100)/no_of_diseases

        return similarity
    
    no_of_diseases = len(disease_details)
    
    technical_similarity = calculate("symptom")
    way_to_check_similarity = calculate("way_to_check")
    # cure_similarity = calculate("cure_way")
    # department_similarity = calculate("department")
    # category_similarity = calculate('disease category')

    print(disease_details)

def suggest_question(list_of_diseases):
    disease_details = dict()
    for disease in list_of_diseases:
        properties = get_disease_properties(disease)
        disease_details[disease] = properties

    similarity_score(disease_details)

suggest_question(list_of_diseases)