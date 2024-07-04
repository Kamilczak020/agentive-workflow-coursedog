from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage

user_prompt_template = '''
    Given the following information gathered about the subject, answer the user's query as well as possible.
    It is located between <GATHERED_INFO_START> and <GATHERED_INFO_END>.

    <GATHERED_INFO_START>
    {{ info }}
    <GATHERED_INFO_END>

    User query: {{ query }}
'''

prompt_template = [
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

response_execution_llm = OpenAIChatGenerator(
    api_key=Secret.from_env_var('OPENAI_API_KEY'),
    model='gpt-4o'
)

response_pipeline = Pipeline()
response_pipeline.add_component('prompt_builder', prompt_builder)
response_pipeline.add_component('response_execution_llm', response_execution_llm)
response_pipeline.connect('prompt_builder', 'response_execution_llm')

def run_response_pipeline(query: str, info: str):
    return response_pipeline.run({
        'prompt_builder': {
            'query': query,
            'info': info,
        }
})
