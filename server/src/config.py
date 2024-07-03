import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "openai": {
        "api_key": os.getenv('OPENAI_API_KEY')
    },
    "neo4j": {
        "uri": 'neo4j://localhost:7687',
        "auth": ('neo4j', 'development')
    },
    "mongo": {
        "uri": os.getenv('MONGODB_URI')
    }
}
