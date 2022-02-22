import yaml
from py2neo import Graph

def db_connect():
    try:
        file = open('Config/database.yaml', 'r')
        configurations = yaml.safe_load(file)
        file.close()
    except FileNotFoundError as e:
        print("Database config file not found. \n", e)
        exit(1)

    graph = Graph(
        host = configurations['HOST'],
        port = configurations['PORT'],
        user = configurations['USERNAME'],
        password = configurations['PASSWORD']
    )
    return graph
