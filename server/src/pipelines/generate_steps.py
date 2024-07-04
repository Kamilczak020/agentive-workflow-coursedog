import json
from typing import List
from haystack import Pipeline
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders import ChatPromptBuilder
from tools.cypher_query import cypher_query_tool
from tools.search_semantically import search_semantically_tool
from model import get_data_model_prompt

from dotenv import load_dotenv

load_dotenv()

step_prompt_content = '''
    Take into account how the application knowledge is stored, found between <SCHEMA_START> and <SCHEMA_END>.
    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    Given the following user query, think out loud and consider the next step of knowledge acquisition, required
    to answer the user query.

    User Query: {{ query }}
'''

step_prompt_template = [
    ChatMessage.from_user(step_prompt_content)
]

step_prompt_builder = ChatPromptBuilder(template=step_prompt_template)
step_generation_llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-3.5-turbo'
)

discovery_prompt_content = '''
    Take into account how the application knowledge is stored, found between <SCHEMA_START> and <SCHEMA_END>.
    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    Original user query {{ query }}
    Given the following breakdown of the problem, execute
'''

discovery_prompt_template = [
    ChatMessage.from_user(discovery_prompt_content)
]

discovery_prompt_builder = ChatPromptBuilder(template=discovery_prompt_template)
discovery_generation_llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-4o'
)

discovery_tools = [
    search_semantically_tool,
    cypher_query_tool,
]

chat_pipeline = Pipeline()
chat_pipeline.add_component('step_prompt_builder', step_prompt_builder)
chat_pipeline.add_component('step_generation_llm', step_generation_llm)
chat_pipeline.add_component('discovery_prompt_builder', discovery_prompt_builder)
chat_pipeline.add_component('discovery_generation_llm', discovery_generation_llm)
chat_pipeline.connect('step_prompt_builder', 'step_generation_llm')
chat_pipeline.connect('discovery_prompt_builder', 'discovery_generation_llm')

def run_generate_steps_pipeline(query: str):
    response = chat_pipeline.run({
        'prompt_builder': {
            'query': query,
            'schema': get_data_model_prompt(),
        },
        'discovery_generation_llm': {
            'generation_kwargs': {
                'tools': discovery_tools,
            }
        }
    })

    print(response)
