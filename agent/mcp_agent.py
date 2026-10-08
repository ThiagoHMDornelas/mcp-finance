import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from mcp_servers import MCP_SERVERS_CONFIG


SYSTEM_MESSAGE = (
    'Você é um agente analista financeiro e deve utilizar '
    'suas ferramentas para responder o usuário.'
)


async def main():
    model = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
    memory = MemorySaver()

    mcp_client = MultiServerMCPClient(MCP_SERVERS_CONFIG)
    tools = await mcp_client.get_tools()

    agent_executor = create_react_agent(
        model=model,
        tools=tools,
        prompt=SYSTEM_MESSAGE,
        checkpointer=memory,
    )

    config = {'configurable': {'thread_id': '1'}}

    while True:
        try:
            pergunta = input('Digite: ')
        except (EOFError, KeyboardInterrupt):
            break

        input_message = {'role': 'user', 'content': pergunta}

        async for step in agent_executor.astream(
            {'messages': [input_message]}, config, stream_mode='values'
        ):
            step['messages'][-1].pretty_print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
