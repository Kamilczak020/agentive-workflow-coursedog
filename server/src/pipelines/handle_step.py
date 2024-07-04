from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from config import config
from neo4j import GraphDatabase
from haystack.dataclasses import ChatMessage
from tools.cypher_query import cypher_query_tool
from tools.search_semantically import search_semantically_tool
from model import get_data_model_prompt

from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(config['neo4j']['uri'], auth=config['neo4j']['auth'])

user_prompt_template = '''
    Take into account how the application knowledge is stored, found between <SCHEMA_START> and <SCHEMA_END>.
    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    Given the following step description, use the provided tools to extract necessary information from knowledge sources.

    Step description: {{ step }}
'''

prompt_template = [
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

step_execution_llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-3.5-turbo'
)

tools = [
    search_semantically_tool,
    cypher_query_tool,
]

step_pipeline = Pipeline()
step_pipeline.add_component('prompt_builder', prompt_builder)
step_pipeline.add_component('step_execution_llm', step_execution_llm)
step_pipeline.connect('prompt_builder', 'step_execution_llm')

def run_handle_step_pipeline(step: str):
    return step_pipeline.run({
        'prompt_builder': {
            'step': step,
            'schema': get_data_model_prompt(),
        },
        'step_execution_llm': {
            'generation_kwargs': {
                'tools': tools,
            }
        }
})
