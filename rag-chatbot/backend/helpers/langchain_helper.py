from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from helpers.vector_helper import vector_store

search_vector_store_k = int(os.getenv("SEARCH_VECTORSTORE_K"))
retriever = vector_store.as_retriever(search_kwargs={"k": search_vector_store_k})
output_parser = StrOutputParser()
ai_model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

def get_rag_chain(model=ai_model):
    llm = AzureChatOpenAI(model=model)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain

def generate_title(user_input:str, model=ai_model):
    llm = AzureChatOpenAI(model = model)

    title_prompt = PromptTemplate(
        input_variables=["user_input"],
        template="""
You are a helpful assistant tasked with naming chat session. 
Given the user's input, generate a short, clear title (3-7 words) that summarizes the topic.

User Input:
{user_input}

Title:
""".strip()
    )

    chain = title_prompt | llm | output_parser
    title = chain.invoke(user_input)
    return title