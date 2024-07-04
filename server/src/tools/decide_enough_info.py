from genson import SchemaBuilder

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'is_enough_info': {
            'type': 'string',
            'enum': ['yes', 'no']
        }
    }
})

enough_info_tool_schema = builder.to_schema()

enough_info_tool = {
    'type': 'function',
    'function': {
        'name': 'is_enough_info',
        'description': 'Executes different flows, based on whether there is enough info or not.',
        'parameters': enough_info_tool_schema
    }
}

