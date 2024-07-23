# MiniPilot

This application implements a chatbot you can train with your data. From the GUI you will be able to:

- Upload CSV data
- Create an index
- Edit the system and user prompt
- Ask questions in natural language

![demo](src/static/images/minipilot.gif)

The system uses:

- Redis Stack as a vector database to store the dataset and vectorize the content for RAG using Redis [vector search capabilities](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/).
- OpenAI ChatGPT Large Language Model (LLM) [ChatCompletion API](https://platform.openai.com/docs/guides/gpt/chat-completions-api)

## Quickstart

1. git clone https://github.com/redis/MiniPilot.git
2. `export OPENAI_API_KEY="your-openai-key"`
2. `cd MiniPilot`
3. `docker-compose build --no-cache && docker-compose up`
4. Point your browser to [http://127.0.0.1:5007/](http://127.0.0.1:5007/) and start chatting
5. Browse your data with Redis Insight at [http://127.0.0.1:8099](http://127.0.0.1:8099)

## Documentation
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [FAQ](docs/faq.md)


