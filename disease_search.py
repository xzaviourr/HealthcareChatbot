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
