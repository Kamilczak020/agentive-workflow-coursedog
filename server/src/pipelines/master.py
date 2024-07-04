import json
from typing import Dict
from pipelines.discovery import run_discovery_pipeline
from pipelines.enough_info import run_enough_info_pipeline
from tools.search_semantically import run_semantic_search

def parse_pipeline_tool_output(output: Dict, output_name: str):
    chat_message = output[output_name]['replies'][0]
    parsed_messages = json.loads(chat_message.content)
    outputs = []

    for message in parsed_messages:
        outputs.append({
            'function_name': message['function']['name'],
            'arguments': json.loads(message['function']['arguments']),
        })

    return outputs

def handle_tool_calls(tool_calls):
    for tool_call in tool_calls:
        match tool_call['function_name']:
            case 'search_semantically':
                return run_semantic_search(tool_call['arguments'])
            case 'execute_cypher_query':
                return

def run_discovery(query, info):
    discovery_output = run_discovery_pipeline(query, info)
    tool_calls = parse_pipeline_tool_output(discovery_output, 'discovery_generation_llm')
    return handle_tool_calls(tool_calls)

def run_enough_info(query, info):
    info_output = run_enough_info_pipeline(query, info)
    tool_calls = parse_pipeline_tool_output(info_output, 'enough_info_llm')
    return tool_calls[0]['arguments']['is_enough_info']
    

def run_master_pipeline(query):
    gathered_information = []
    should_respond = False
    cycles = 0

    tool_output = run_discovery(query, 'No information discovered yet!')
    gathered_information.append(tool_output)
    
    while should_respond == False and cycles < 3:
        print(gathered_information)
        info_so_far = '\n\n'.join(gathered_information)
        is_enough = run_enough_info(query, info_so_far)
        if (is_enough == 'yes'):
            return 'done'

        tool_output = run_discovery(query, info_so_far)
        gathered_information.append(tool_output)
        cycles += 1

    print(tool_output)
