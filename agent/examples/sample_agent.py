import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from tools import get_company_info, get_current_stock_price, get_history_stock_price


load_dotenv()

SYSTEM_MESSAGE = (
    'Você é um agente analista financeiro e deve utilizar '
    'suas ferramentas para responder o usuário.'
)

model = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
memory = MemorySaver()

tools = [
    get_company_info,
    get_current_stock_price,
    get_history_stock_price,
]

agent_executor = create_react_agent(
    model=model,
    tools=tools,
    prompt=SYSTEM_MESSAGE,
    checkpointer=memory,
)

config = {'configurable': {'thread_id': '1'}}

if __name__ == '__main__':
    while True:
        try:
            pergunta = input('Digite: ')
        except (EOFError, KeyboardInterrupt):
            break

        input_message = {'role': 'user', 'content': pergunta}

        for step in agent_executor.stream(
            {'messages': [input_message]}, config, stream_mode='values'
        ):
            step['messages'][-1].pretty_print()
