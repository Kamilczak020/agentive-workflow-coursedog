from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.joiners import BranchJoiner
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from tools.cypher_query import cypher_query_tool
from tools.search_semantically import search_semantically_tool
from pipelines.utils import parse_pipeline_output
from config import config

system_prompt_template = '''
    You are an expert at university operations and knowledge.
    Your role is to answer the original user question as truthfully as possible.
    You are provided with information that was collected in a rigorous process.
    You can extrapolate from the data provided and reason, but do not make up facts.
    
    The output should contain an answer to the entire user question.
'''

user_prompt_template = '''
    A user has asked a question, which was later broken down into a list of steps.
    Over multiple information-gathering steps, data was collected to help answer the question.
    Your task is to create a final response using the collected information.
    Relevant information can be found between <INFO_START> and <INFO_END>
    
    <INFO_START>
    {{ information }}
    <INFO_END>

    User Question: {{ question }}
    Your Response:
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

pipeline = Pipeline()
pipeline.add_component('prompt_builder', prompt_builder)
pipeline.add_component('response_llm', llm)
pipeline.connect('prompt_builder', 'response_llm')

def run_response_pipeline(question: str, information: str):
    output = pipeline.run({
        'prompt_builder': {
            'question': question,
            'information': information
        }
    })

    return parse_pipeline_output(output, 'response_llm')
