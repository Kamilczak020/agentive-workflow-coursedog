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

process_steps_tool_schema = builder.to_schema()

process_steps_tool_name = 'process_steps'

process_steps_tool = {
    'type': 'function',
    'function': {
        'name': process_steps_tool_name,
        'description': 'Given each step, executes it to acquire more information about the user question.',
        'parameters': process_steps_tool_schema
    }
}

process_steps_tool_choice = {
    'type': 'function',
    'function': {
        'name': process_steps_tool_name
    }
}
