import json
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.validators import JsonSchemaValidator
from haystack.components.joiners import BranchJoiner
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from tools.process_steps import process_steps_tool, process_steps_tool_choice, process_steps_tool_schema
from model import get_data_model_prompt
from config import config

system_prompt_template = '''
    You are an expert at university operations and knowledge.
    Use the schema to build a list of knowledge-gathering tasks.
    Do not stray away from the schema provided.
'''

user_prompt_template = '''
    You will find the knowledge schema between <SCHEMA_START> and <SCHEMA_END>.

    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    Consider the following step-back question and answer, that were created to
    generalize the user question.
    {{ step_back_question }}
    {{ step_back_answer }}

    Your role is to break down the user question into a set of 1-5 information gathering tasks.
    Each task will be later executed sequentially, and each will have information
    gathered in a previous step.

    Do not create data-compilation steps, this is already handled.
    The generated tasks should be concise, but contain all necessary information.
    
    Here is some examples:
    User Question: Which professors teach biology?
    List of tasks:
        - Determine which available courses deal with biology and biology-related fields
        - Determine which sections are related to those courses
        - Determine which professors teach those sections

    User Question: What is a good course for someone who wants to go into IT?
    List of tasks:
        - Determine which fields and academic paths are IT-related
        - For each of those fields and paths, semantically determine courses

    User Question: Who is John Hill?
    List of tasks:
        - Determine if there is a professor called John Hill
        - Determine which sections teach
        - Determine which courses are related to those sections
        - Use course descriptions to give insight into what John teaches

    Given the provided user question, construct a list of tasks.
    User Question: {{ question }}
'''

prompt_template = [
    ChatMessage.from_system(system_prompt_template),
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

branch_joiner = BranchJoiner(list[ChatMessage])

reasoning_llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-4o'
)


response_llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-4o'
)

schema_validator = JsonSchemaValidator(process_steps_tool_schema)

pipeline = Pipeline(max_loops_allowed=5)
pipeline.add_component('prompt_builder', prompt_builder)
pipeline.add_component('reasoning_llm', reasoning_llm)
pipeline.add_component('response_llm', response_llm)
pipeline.add_component('branch_joiner', branch_joiner)
pipeline.add_component('schema_validator', schema_validator)
pipeline.connect('prompt_builder', 'reasoning_llm')
pipeline.connect('reasoning_llm', 'branch_joiner')
pipeline.connect('branch_joiner', 'response_llm')
pipeline.connect('response_llm.replies', 'schema_validator.messages')
pipeline.connect('schema_validator.validation_error', 'branch_joiner')

def parse_breakdown_output(output: dict, output_name: str):
    chat_message = output[output_name]['validated'][0]

    parsed_messages = json.loads(chat_message.content)
    arguments = parsed_messages[0]['function']['arguments']
    parsed_arguments = json.loads(arguments)

    return parsed_arguments['steps']

def run_breakdown_pipeline(question: str, step_back_question: str) -> list[str]:
    output = pipeline.run({
        'prompt_builder': {
            'question': question,
            'step_back_question': step_back_question,
            'schema': get_data_model_prompt()
        },
        'response_llm': {
            'generation_kwargs': {
                'tools': [ process_steps_tool ],
                'tool_choice': process_steps_tool_choice
            }
        }
    })

    return parse_breakdown_output(output, 'schema_validator')
