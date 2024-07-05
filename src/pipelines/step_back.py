from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from pipelines.utils import parse_pipeline_output
from config import config

system_prompt_template = '''
    You are an expert at university operations and knowledge.
    Do not relate questions to any publicly accessible data, simply focus on paraphrasing it.
'''

user_prompt_template = '''
    Your task is to step back and paraphrase a question to a more generic 
    step-back question, which is easier to answer.
    Your step back questions should be concise, but include all relevant information.

    Here is some examples:
    Original Question: What does Jason Hall teach?
    Stepback Question: Who is Jason Hall, in context of university knowledge?

    Original Question: I'm a grad student, that loves building robots. Which academic direction could I pursue?
    Stepback Question: Which academic concepts deal with robotics?

    Original Question: {{ question }}
    Stepback Question:
'''

prompt_template = [
    ChatMessage.from_system(system_prompt_template),
    ChatMessage.from_user(user_prompt_template)
]

prompt_builder = ChatPromptBuilder(template=prompt_template)

response_llm = OpenAIChatGenerator(
    api_key=Secret.from_token(config['openai']['api_key']),
    model='gpt-3.5-turbo'
)

pipeline = Pipeline() 
pipeline.add_component('prompt_builder', prompt_builder)
pipeline.add_component('response_llm', response_llm)
pipeline.connect('prompt_builder', 'response_llm')

def run_step_back_pipeline(question: str) -> list:
    output = pipeline.run({
        'prompt_builder': {
            'question': question,
        }
    })

    return parse_pipeline_output(output, 'response_llm')
