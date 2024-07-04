from genson import SchemaBuilder

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'phrase': {
            'type': 'string'
        }
    }
})

search_semantically_tool_schema = builder.to_schema()

search_semantically_tool = {
    'type': 'function',
    'function': {
        'name': 'search_semantically',
        'description': 'Searches the knowledge semantically for matches and returns results',
        'parameters': search_semantically_tool_schema,
    }
}
