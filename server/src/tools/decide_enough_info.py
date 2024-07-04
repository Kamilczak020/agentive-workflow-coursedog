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
        'description': 'If the answer is no, the application will perform additional queries. If the answer is yes, the application will generate a final response.',
        'parameters': enough_info_tool_schema
    }
}

