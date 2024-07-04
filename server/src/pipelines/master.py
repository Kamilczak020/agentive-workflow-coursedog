import json
from typing import Dict
from pipelines.discovery import run_discovery_pipeline
from pipelines.enough_info import run_enough_info_pipeline
from pipelines.response import run_response_pipeline
from tools.cypher_query import run_cypher_query
from tools.search_semantically import run_semantic_search

def parse_pipeline_output(output: Dict, output_name: str, tool = False):
    chat_message = output[output_name]['replies'][0]
    outputs = []

    if tool == True:
        parsed_messages = json.loads(chat_message.content)
        for message in parsed_messages:
            outputs.append({
                'function_name': message['function']['name'],
                'arguments': json.loads(message['function']['arguments']),
            })
    else:
        outputs.append(chat_message.content)

    return outputs

def handle_tool_calls(tool_calls):
    for tool_call in tool_calls:
        match tool_call['function_name']:
            case 'search_semantically':
                return run_semantic_search(tool_call['arguments'])
            case 'execute_cypher_query':
                return run_cypher_query(tool_call['arguments'])

def run_discovery(query, info, past_tool_calls):
    discovery_output = run_discovery_pipeline(query, info, past_tool_calls)
    tool_calls = parse_pipeline_output(discovery_output, 'discovery_generation_llm', True)
    return (tool_calls, handle_tool_calls(tool_calls))

def run_enough_info(query, info):
    info_output = run_enough_info_pipeline(query, info)
    tool_calls = parse_pipeline_output(info_output, 'enough_info_llm', True)
    return tool_calls[0]['arguments']['is_enough_info']
    
def stringify_gathered_info(info):
    output = ''
    for entry in info:
        output += '\n\n'
        output += json.dumps(entry)

    return output

def run_master_pipeline(query):
    infos = []
    past_tool_calls = []
    should_respond = False
    cycles = 0

    (used_tools, tool_output) = run_discovery(query, 'No information discovered yet!', 'No past tool calls yet!')
    infos.append(tool_output)
    past_tool_calls.append(json.dumps(used_tools[0]))
    
    while should_respond == False and cycles < 3:
        print(f'Running cycle #{cycles + 1}')
        print('Gathered info so far', infos)
        info = stringify_gathered_info(infos)
        is_enough = run_enough_info(query, info)
        if (is_enough == 'yes'):
            break

        (used_tools, tool_output) = run_discovery(query, info, '\n\n'.join(past_tool_calls))
        infos.append(tool_output)
        past_tool_calls.append(json.dumps(used_tools[0]))
        cycles += 1

    response_output = run_response_pipeline(query, stringify_gathered_info(infos))
    print(response_output['response_execution_llm'])
