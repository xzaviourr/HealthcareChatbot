from Database.connection import db_connect
import re

relationship = re.compile("\(.+\)-\[:(.+) \{\}\]->\((.+)\)")

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
    RETURN z
    """
    results = graph.run(query).data()

    properties = dict()
    for node in results:
        rel_result = re.findall(relationship, str(node['z']))
        if rel_result != []: 
            rln, name = rel_result[0]

        if rln in properties.keys():
            properties[rln].append(name)
        else:
            properties[rln] = [name]

    query = f"""
    MATCH (x:disease)
    WHERE x.name = "{disease}"
    RETURN x
    """
    results = graph.run(query).data()
    for key in results[0]['x'].keys():
        properties[key] = results[0]['x'][key]

    return properties

def test(disease_names):
    disease_details = dict()
    for name in disease_names:
        disease_details[name] = get_disease_properties(name)
    
    no_of_diseases = len(disease_details)
    
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

    print(calculate('has_symptom'))
    
test(list_of_diseases)