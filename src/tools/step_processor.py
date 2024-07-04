from genson import SchemaBuilder

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'steps': {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
    }
})

step_processor_tool_schema = builder.to_schema()

step_processor_tool_name = 'execute_step_processor'

step_processor_tool = {
    'type': 'function',
    'function': {
        'name': step_processor_tool_name,
        'description': 'Processes each individual step provided to input',
        'parameters': step_processor_tool_schema
    }
}

step_processor_tool_choice = {
    'type': 'function',
    'function': {
        'name': step_processor_tool_name
    }
}
