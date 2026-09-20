from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from .vector_service import VectorService
from .llm_service import LLMService


class RAGService:

    def __init__(self):
        self.vector_service = VectorService()
        self.llm_service = LLMService()

    def format_docs(self, docs):
        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    def build_rag_chain(self, vector_store, video_id):

        retriever = self.vector_service.get_retriever(
            vector_store,
            video_id=video_id,
            k=4
        )

        llm = self.llm_service.get_llm()

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert video assistant.

Answer the user's question based ONLY on the transcript
context provided below.

If the answer is not found in the context, say:
"I could not find this information in the video transcript."

Always be concise and precise.

Transcript context:
{context}"""
                ),
                ("human", "{question}"),
            ]
        )

        rag_chain = (
            {
                "context": retriever | RunnableLambda(self.format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain

    def ask_question(self, rag_chain, question):
        answer = rag_chain.invoke(question)
        return answer