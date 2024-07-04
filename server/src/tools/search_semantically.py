from genson import SchemaBuilder
from neo4j import GraphDatabase
from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret
from config import config
from dotenv import load_dotenv
from utils import flatten

load_dotenv()

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'phrase': {
            'type': 'string'
        },
        'over_index': {
            'type': 'string',
            'enum': ['course_description']
        }
    }
})

search_semantically_tool_schema = builder.to_schema()

search_semantically_tool = {
    'type': 'function',
    'function': {
        'name': 'search_semantically',
        'description': 'Searches the knowledge semantically for matches and returns results. Use keywords rather than full sentences',
        'parameters': search_semantically_tool_schema,
    }
}

def remove_embed_keys(from_entry):
    return {k: v for k, v in from_entry.items() if not k.endswith('_embed')}

def run_semantic_search(arguments):
    driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])
    with driver.session() as session:
        embedder = OpenAITextEmbedder(api_key=Secret.from_env_var('OPENAI_API_KEY'), model='text-embedding-3-small')
        embedder_response = embedder.run(arguments['phrase'])
        question = embedder_response['embedding']

        response = session.run('''
            CALL db.index.vector.queryNodes($index_name, 10, $question)
            YIELD node
            RETURN node
        ''', question=question, index_name=arguments['over_index'])
        
        output = [remove_embed_keys(node_response['node']) for node_response in response.data()]

    driver.close()
    return output
