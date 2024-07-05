
from pipelines.response import run_response_pipeline
from pipelines.breakdown import run_breakdown_pipeline
from pipelines.collection import run_collection_pipeline
from pipelines.step_back import run_step_back_pipeline
from pipelines.step_execution import run_step_execution_pipeline
from tools.cypher_query import run_cypher_query
from tools.search_semantically import run_semantic_search

def handle_tool_calls(tool_calls):
    for tool_call in tool_calls:
        match tool_call['function_name']:
            case 'search_semantically':
                return run_semantic_search(tool_call['arguments'])
            case 'execute_cypher_query':
                return run_cypher_query(tool_call['arguments'])

def run_master_pipeline(question: str, update_info):
    step_back_question = run_step_back_pipeline(question)

    update_info(f'## Step-back question: { step_back_question[0] }')
    
    steps = run_breakdown_pipeline(question, step_back_question[0])
    nl = '\n\n'
    nl_dash = '\n -'

    update_info(f'## Steps to execute: {nl} { nl_dash.join(steps) }')
    
    prev_steps = []
    next_steps = [{"index": idx, "task": task} for idx, task in enumerate(steps)]
    
    for current_step_index, step in enumerate(steps):
        current_next_steps = next_steps[current_step_index + 1:]
        if (current_step_index > len(steps)):
            break
        
        update_info(f'# Executing step #{ current_step_index + 1 }')

        execution_output = run_step_execution_pipeline(
            step,
            current_step_index + 1,
            prev_steps,
            current_next_steps
        )

        result = handle_tool_calls(execution_output)
        update_info(f'''
            Plan for step #{ current_step_index + 1 }:
            { execution_output }
        ''')

        prev_steps.append({
            "index": current_step_index,
            "task": step,
            "result": result
        })
    
    information = run_collection_pipeline(question, prev_steps)
    update_info(f'## Post-collection: {nl} {information[0]}')

    response = run_response_pipeline(question, information[0])
    return response[0]

