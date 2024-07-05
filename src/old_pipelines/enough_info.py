from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from tools.decide_enough_info import enough_info_tool
from model import get_data_model_prompt

user_prompt_template = '''
    Take into account how the application knowledge is stored, found between <SCHEMA_START> and <SCHEMA_END>.
    <SCHEMA_START>
    {{ schema }}
    <SCHEMA_END>

    Given the following information that was gathered in previous steps, decide wether this is enough information to truthfully answer the user query.
    You can find the info between <GATHERED_INFORMATION_START> and <GATHERED_INFORMATION_END>.
    If there is no information gathered yet, respond no.
    If the information is enough to answer the user query, respond yes.
    Remember, that additional information can be obtained in further steps, as this is simply an early exit condition.

    User Query: {{ query }}

    <GATHERED_INFORMATION_START>
    {{ info }}
    <GATHERED_INFORMATION_END>
'''

prompt_template = [
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

enough_info_llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-3.5-turbo'
)

tools = [
    enough_info_tool
]

step_pipeline = Pipeline()
step_pipeline.add_component('prompt_builder', prompt_builder)
step_pipeline.add_component('enough_info_llm', enough_info_llm)
step_pipeline.connect('prompt_builder', 'enough_info_llm')

def run_enough_info_pipeline(query: str, info: str):
    return step_pipeline.run({
        'prompt_builder': {
            'query': query,
            'info': info,
            'schema': get_data_model_prompt(),
        },
        'enough_info_llm': {
            'generation_kwargs': {
                'tools': tools,
                'tool_choice': {
                    'type': 'function',
                    'function': {
                        'name': 'is_enough_info'
                    }
                }
            }
        }
})
