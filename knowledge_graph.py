from gettext import Catalog
import json
import pandas as pd
import yaml

from py2neo import Node

from Database.connection import db_connect


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

    def load_dataset(self, file_path):
        """
        Loads json file into pandas dataframe
        :param file_path: Path of a json file (with indent = 4, and newlines after every record)
        :return: pandas dataframe for the loaded file
        """
        try:
            file = open(file_path, 'r')
            raw_data = file.read()
            file.close()
        except FileNotFoundError as e:
            print("Dataset cannot be found. \n", e)
            exit(1)

        raw_objects = raw_data.split('}\n{')
        raw_objects = ['{' + x + '}' for x in raw_objects]
        raw_objects[0] = raw_objects[0][1:]
        raw_objects[-1] = raw_objects[-1][:len(raw_objects[-1]) -1]

        raw_objects = [json.loads(x) for x in raw_objects]
        df = pd.DataFrame.from_dict(raw_objects)
        return df   

    def create_node(self, category, label, properties=None):
        if category == "disease":
            node = Node(
                category, 
                name = label,
                description = properties['desc'],
                prevention = properties['prevent'],
                causes = properties['cause'],
                prone_to = properties['easy_get'],
                propogation_way = properties['get_way'],
                get_probability = properties['get_prob'],
                cure_last_time = properties['cure_lasttime'],
                cured_probabiltity = properties['cured_prob'],
                cost_money = properties['cost_money']
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

        return set(unique_list)

    def controller(self):
        self.dataset = self.dataset[0:5]

        # Create all disease nodes
        for index, row, in self.dataset.iterrows():
            self.create_node(category="disease", label=row['name'], properties=row)

        # Get all unique properties
        disease_categories = self.get_unique(self.dataset.category)
        symptoms = self.get_unique(self.dataset.symptom)
        accompany_diseases = self.get_unique(self.dataset.acompany)
        departments = self.get_unique(self.dataset.cure_department)
        cure_ways = self.get_unique(self.dataset.cure_way)
        ways_to_check = self.get_unique(self.dataset.check)
        drugs = self.get_unique(self.dataset.recommand_drug)
        drugs.update(self.get_unique(self.dataset.common_drug))
        food = self.get_unique(self.dataset.do_eat)
        food.update(self.get_unique(self.dataset.not_eat))
        food.update(self.get_unique(self.dataset.recommand_eat))

        # Create Nodes for all unique properties
        for ele in disease_categories:
            self.create_node(category="disease category", label=ele)
        for ele in symptoms:
            self.create_node(category="symptom", label=ele)
        for ele in accompany_diseases:
            self.create_node(category="accompany_disease", label=ele)
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


obj = KnowledgeGraph()
obj.delete_all_nodes()
obj.controller()