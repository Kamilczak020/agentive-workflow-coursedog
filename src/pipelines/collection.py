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

    Your role is to pick the most relevant pieces of information for answering the original user question.
    The information was collected in multiple steps, from various database and external queries.
    Some of the information may not be relevant to the question, and your role is to weed it out.
    
    The output should contain all the relevant information extracted from external sources.
'''

user_prompt_template = '''
    You will find the knowledge schema between <SCHEMA_START> and <SCHEMA_END>.
    Use this schema as basis for executing queries and searching for information.
    Under any circumistances, do not stray away from the schema.

    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    A user has asked a question, which was later broken down into a list of steps.
    User Question: {{ question }}

    Over multiple information-gathering steps, data was collected to help answer the question.
    Below, you will find a list of all the steps, their tasks and their results.

    {% for step in steps %}
    Step #{{ step['index'] }}:
        Task: {{ step['task'] }}
        Parsed result: {{ step['result'] }}

    {% endfor %}
    
    Your task is to pick out the most relevant information from the data gathered so far.
    Your response should contain all the steps results information bits that will help answer the original user question.

    Relevant Information:
'''

prompt_template = [
    ChatMessage.from_system(system_prompt_template),
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

branch_joiner = BranchJoiner(list[ChatMessage])

llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-4o'
)

pipeline = Pipeline(max_loops_allowed=5)
pipeline.add_component('prompt_builder', prompt_builder)
pipeline.add_component('response_llm', llm)
pipeline.connect('prompt_builder', 'response_llm')

def run_collection_pipeline(question: str, steps: list[dict]):
    output = pipeline.run({
        'prompt_builder': {
            'question': question,
            'steps': steps,
            'schema': get_data_model_prompt()
        }
    })

    return parse_pipeline_output(output, 'response_llm')
