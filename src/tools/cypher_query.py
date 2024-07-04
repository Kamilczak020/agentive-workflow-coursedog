from genson import SchemaBuilder
from neo4j import GraphDatabase
from config import config
from dotenv import load_dotenv

load_dotenv()

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'query': {
            'type': 'string'
        }
    }
})

cypher_query_tool_schema = builder.to_schema()

cypher_query_tool = {
    'type': 'function',
    'function': {
        'name': 'execute_cypher_query',
        'description': 'Executes a cpyher query and returns results.',
        'parameters': cypher_query_tool_schema
    }
}

def run_cypher_query(arguments):
    print(arguments['query'])
    driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])
    with driver.session() as session:
        response = session.run(arguments['query'])
        output = response.data()
        print(output)

    driver.close()
    return output
