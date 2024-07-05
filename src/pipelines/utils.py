import json


def parse_pipeline_output(output: dict, output_name: str, tool = False):
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
