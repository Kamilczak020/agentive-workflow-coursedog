from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.joiners import BranchJoiner
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from tools.cypher_query import cypher_query_tool
from tools.search_semantically import search_semantically_tool
from pipelines.utils import parse_pipeline_output
from model import get_data_model_prompt
from config import config

system_prompt_template = '''
    You are an expert at university operations and knowledge.
    Use the provided data schema as the main basis for your work.

    Your role is to execute a knowledge-discovery step by performing reasoning
    or executing function calls to acquire more data on the topic.
'''

user_prompt_template = '''
    You will find the knowledge schema between <SCHEMA_START> and <SCHEMA_END>.
    Use this schema as basis for executing queries and searching for information.
    Under any circumistances, do not stray away from the schema.

    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    You have the following tools at your disposal:
    - execute_cypher_query - use it when searching general information in the graph database. Make sure to always match your queries to the provided schema.
    - search_semantically - only use it if searching for information within course description.
    
    {% if current_step_index > 1 %}
    Below, you will find previous execution steps.
    {% endif %}

    {% for prev_step in prev_steps %}
    Previous Step #{{ prev_step['index'] }}:
        Task: {{ prev_step['task'] }}

    {% endfor %}
    
    {% if next_steps|length > 1 %}
    Below, you will find future execution steps.
    {% endif %}

    {% for next_step in next_steps %}
    Next Step #{{ next_step['index'] }}:
        Task: {{ next_step['task'] }}

    {% endfor %}

    Your task is to handle discovery step #{{ current_step }}, using information gathered so far to guide your response.
    Under no circumistances should you generate a result that has already been generated, and can be found in previous step results.

    If you are running cypher queries, ensure you limit them to max 30 results.

    Respond to your task #{{ current_step_index }} below:
    {{ task }}
'''

prompt_template = [
    ChatMessage.from_system(system_prompt_template),
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

branch_joiner = BranchJoiner(list[ChatMessage])

execution_llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-4o'
)

response_llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-4o'
)

pipeline = Pipeline(max_loops_allowed=5)
pipeline.add_component('prompt_builder', prompt_builder)
pipeline.add_component('response_llm', response_llm)
pipeline.connect('prompt_builder', 'response_llm')

def run_step_execution_pipeline(task: str, current_step_index: int, prev_steps: list[dict], next_steps: list[dict]):
    output = pipeline.run({
        'prompt_builder': {
            'task': task,
            'prev_steps': prev_steps,
            'next_steps': next_steps,
            'current_step_index': current_step_index,
            'schema': get_data_model_prompt()
        },
        'response_llm': {
            'generation_kwargs': {
                'tools': [
                    cypher_query_tool,
                    search_semantically_tool,
                ]
            }
        }
    })

    return parse_pipeline_output(output, 'response_llm', True)
