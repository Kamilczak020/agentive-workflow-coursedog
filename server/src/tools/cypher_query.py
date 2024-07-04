from genson import SchemaBuilder

builder = SchemaBuilder()
builder.add_schema({
    'type': 'object',
    'properties': {
        'query': {
            'type': 'string'
        }
    }
})

cypher_query_tool_schema = builder.to_schema()

cypher_query_tool = {
    'type': 'function',
    'function': {
        'name': 'execute_cypher_query',
        'description': 'Executes a cpyher query and returns results.',
        'parameters': cypher_query_tool_schema
    }
}

