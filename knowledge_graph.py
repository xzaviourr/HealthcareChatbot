from gettext import Catalog
import json
import pandas as pd
import yaml
import time

from py2neo import Node

from Database.connection import db_connect

counter = 1
class KnowledgeGraph:
    """
    Instance of knowledge graph, that is hosted on neo4j server. Contains functions for creation of the knowledge graph object
    """
    def __init__(self) -> None:
        try:
            file = open('Config/knowledge_graph.yaml', 'r')
            self.configurations = yaml.safe_load(file)
            file.close()
        except FileNotFoundError as e:
            print("knowledge graph config file not found. \n", e)
            exit(1)

        try:
            file = open('Database/queries.yaml')
            self.db_queries = yaml.safe_load(file)
            file.close()
        except FileNotFoundError as e:
            print("Database queries file not found. \n", e)
            exit(1)

        self.dataset = self.load_dataset(self.configurations['DATASET_PATH'])
        self.graph = db_connect()

        self.attribute_matching = {
            "category": ["category", "belongs_to_category"], 
            "symptom": ["symptom", "has_symptom"], 
            "prevent": ["prevent", "has_prevention"],
            "cause": ["cause", "has_cause"],
            "acompany": ["disease", "accompanies"], 
            "cure_department": ["department", "cured_by_department"], 
            "cure_way": ["cure_way", "cured_by"], 
            "check": ["way_to_check", "required_check"], 
            "recommand_drug": ["drug", "has_recommended_drug"], 
            "common_drug": ["drug", "has_common_drug"], 
            "do_eat": ["food", "do_eat"], 
            "not_eat": ["food", "not_eat"], 
            "recommand_eat": ["food", "recommended_eat"],
            "easy_get": ["prone_to", "prone_to"]
            }

    def load_dataset(self, file_path):
        """
        Loads json file into pandas dataframe
        :param file_path: Path of a json file (with indent = 4, and newlines after every record)
        :return: pandas dataframe for the loaded file
        """
        try:
            df = pd.read_json(file_path)
        except FileNotFoundError as e:
            print("Dataset cannot be found. \n", e)
            exit(1)
        return df   

    def create_node(self, category, label, properties=None):
        label = str(label)
        label = label.lstrip().rstrip().lower()
        if category == "disease":
            if str(self.graph.run(f"""MATCH (x:disease) WHERE x.name="{label}" RETURN x.name""")) != "(No data)":
                return
            
            cost_money = "No Data"
            if properties['cost_money'] != None and properties['cost_money'] != []: 
                if properties['cost_money'] != [] and len(properties['cost_money']) == 2: 
                    cost_money = str(properties['cost_money'][0]) + " - " + str(properties['cost_money'][1])
                else:
                    cost_money =  str(properties['cost_money'][0])
            
            node = Node(
                category, 
                name = label,
                description = str(properties['desc']).lower(),
                propogation_way = str(properties['get_way']).lower(),
                get_probability = str(properties['get_prob']).lower(),
                cure_last_time = str(properties['cure_lasttime']).lower(),
                cured_probabiltity = str(properties['cured_prob']).lower(),
                cost_money = cost_money 
            )
        else:
            node = Node(
                category,
                name = label
            )
        self.graph.create(node)

    def delete_all_nodes(self):
        self.graph.run(self.db_queries['DELETE_ALL_NODES'])

    def get_unique(self, df_col):
        unique_list = list()
        for cell in df_col:
            for ele in cell:
                unique_list.append(ele)

        return unique_list

    def create_all_graph_nodes(self):
        def preprocess_labels(list_of_attribute):
            for i in range(len(list_of_attribute)):
                list_of_attribute[i] = list_of_attribute[i].lstrip().rstrip().lower()
            list_of_attribute = set(list_of_attribute)
            return list_of_attribute

        # Create all disease nodes
        for index, row, in self.dataset.iterrows():
            self.create_node(category="disease", label=row['name'], properties=row)

        # Get all unique properties
        disease_categories = self.get_unique(self.dataset.category)
        symptoms = self.get_unique(self.dataset.symptom)
        departments = self.get_unique(self.dataset.cure_department)
        cure_ways = self.get_unique(self.dataset.cure_way)
        ways_to_check = self.get_unique(self.dataset.check)
        drugs = self.get_unique(self.dataset.recommand_drug)
        drugs += self.get_unique(self.dataset.common_drug)
        food = self.get_unique(self.dataset.do_eat)
        food += self.get_unique(self.dataset.not_eat)
        food += self.get_unique(self.dataset.recommand_eat)
        prevent = self.get_unique(self.dataset.prevent)
        cause = self.get_unique(self.dataset.cause)
        easy_get = self.get_unique(self.dataset.easy_get)

        symptoms = preprocess_labels(symptoms)
        disease_categories = preprocess_labels(disease_categories)
        departments = preprocess_labels(departments)
        cure_ways = preprocess_labels(cure_ways)
        ways_to_check = preprocess_labels(ways_to_check)
        drugs = preprocess_labels(drugs)
        food = preprocess_labels(food)
        prevent = preprocess_labels(prevent)
        cause = preprocess_labels(cause)
        easy_get = preprocess_labels(easy_get)

        # Create Nodes for all unique properties
        for ele in disease_categories:
            self.create_node(category="disease category", label=ele)
        for ele in symptoms:
            self.create_node(category="symptom", label=ele)
        for ele in departments:
            self.create_node(category="department", label=ele)
        for ele in cure_ways:
            self.create_node(category="cure_way", label=ele)
        for ele in ways_to_check:
            self.create_node(category="way_to_check", label=ele)
        for ele in drugs:
            self.create_node(category="drug", label=ele)
        for ele in food:
            self.create_node(category="food", label=ele)
        for ele in prevent:
            self.create_node(category="prevention", label=ele)
        for ele in cause:
            self.create_node(category='cause', label=ele)
        for ele in easy_get:
            self.create_node(category="prone_to", label=ele)

    def create_relationship(self, start_node_type, end_node_type, start_node_name, end_node_name, relation_type):
        global counter
        print(counter)
        counter += 1
        start_node_name = str(start_node_name).lower().lstrip().rstrip()
        end_node_name = str(end_node_name).lower().lstrip().rstrip()
        end_node_name =  end_node_name.replace("\"", "")
        if relation_type == "acompanies":
            if str(self.graph.run(f"""MATCH (x:disease) WHERE x.name="{end_node_name}" RETURN x.name""")) != "(No data)":
                query = f"""
                    MATCH (a:{start_node_type}), (b:{end_node_type})
                    WHERE a.name = "{start_node_name}" AND b.name = "{end_node_name}"
                    MERGE (a)-[:{relation_type}]->(b)
                    """
                self.graph.run(query) 
        else:
            query = f"""
            MATCH (a:{start_node_type}), (b:{end_node_type})
            WHERE a.name = "{start_node_name}" AND b.name = "{end_node_name}"
            MERGE (a)-[:{relation_type}]->(b)
            """
            x = self.graph.run(query)
            print(query)
        
    def create_all_graph_edges(self):
        for index, row in self.dataset.iterrows():
            disease = row['name']
            for att in self.attribute_matching.keys():
                prop = row[att]
                for node in prop:
                    self.create_relationship(
                        start_node_type="disease",
                        end_node_type=self.attribute_matching[att][0],
                        start_node_name=disease,
                        end_node_name=node,
                        relation_type=self.attribute_matching[att][1]
                    )

    def build_graph(self):
        print("BUILDING KNOWLEDGE GRAPH STARTED")

        # print("PREVIOUS DATA DELETION STARTED")
        # start = time.time()
        # self.delete_all_nodes()
        # end = time.time()
        # print("PREVIOUS DATA DELETION FINISHED, TIME TAKEN ", end-start, " seconds")

        print("GRAPH NODES CREATION STARTED")
        start = time.time()
        self.create_all_graph_nodes()
        end = time.time()
        print("GRAPH NODES CREATION FINISHED, TIME TAKEN ", end   -start, " seconds")

        print("GRAPH EDGE CREATION STARTED")
        start = time.time()
        self.create_all_graph_edges()
        end = time.time()
        print("GRAPH EDGE CREATION FINISHED, TIME TAKEN ", end-start, " seconds")
        print("KNOWLEDGE GRAPH CREATED")

# obj = KnowledgeGraph()
# obj.build_graph()