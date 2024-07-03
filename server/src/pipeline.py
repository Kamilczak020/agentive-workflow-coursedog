from config import config
from neo4j import GraphDatabase
from neo4j_haystack import Neo4jDynamicDocumentRetriever

driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])

cypher_query = f'''
    CALL db.
'''
