import os
import openai
from dotenv import load_dotenv

from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import MessagesPlaceholder

from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

load_dotenv(dotenv_path="openai.env")
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_agent(tools: list, model_name="gpt-3.5-turbo-0125") -> AgentExecutor:

    functions = [convert_to_openai_function(f) for f in tools]
    model = ChatOpenAI(model=model_name, temperature=0).bind(functions=functions)

    input_processor = RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are helpful but sassy assistant"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent_chain = input_processor | prompt | model | OpenAIFunctionsAgentOutputParser()
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    agent_executor = AgentExecutor(
        agent=agent_chain, tools=tools, verbose=True, memory=memory
    )
    return agent_executor
