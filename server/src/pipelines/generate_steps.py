from haystack import Pipeline
from haystack.utils import Secret
from config import config
from neo4j import GraphDatabase
from haystack.components.generators import OpenAIGenerator
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.builders.prompt_builder import PromptBuilder

from model import get_data_model_prompt

driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])

prompt_template = '''
    Take into account how the application knowledge is stored.
    Schema: {{ schema }}

    Given the following user query, think out loud and break it down into resolution steps,
    That would help gain insights into the problem.
    User Query: {{ query }}

'''

text_embedder = OpenAITextEmbedder(api_key=Secret.from_env_var('OPENAI_API_KEY'))
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-4o'
)

chat_pipeline = Pipeline()
chat_pipeline.add_component('prompt_builder', prompt_builder)
chat_pipeline.add_component('llm', llm)
chat_pipeline.connect('prompt_builder', 'llm')

def run_generate_steps_pipeline(query):
    result = chat_pipeline.run({
        'prompt_builder': {
            'query': query,
            'schema': get_data_model_prompt(),
        }
    })

    print(result)
