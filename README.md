# University Analyics with Agentic Workflows

This app is built on haystack, and uses an agentic workflow to reason about, plan and go on side quests to gather information.
Based on the collected info, it can then construct responses.

## Dataset
This project was developed with Coursedog data, which can only be accessed if you're part of the organization.
None of the project data is, or will be, publicly accessible.

If you wish to run this project locally, you will need to unzip it into `documents`.

## Installation
```bash
pip3 install
```

## Development
This project uses vite-node to provide you with a basic dev experience. Further configurable through `vite.config.ts`
```bash
python3 src/main.py
```

## Docker
A Docker Compose setup is available to locally run neo4j.
```bash
docker compose up

