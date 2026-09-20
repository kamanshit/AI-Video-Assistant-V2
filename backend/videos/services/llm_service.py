import os
from langchain_groq import ChatGroq


class LLMService:

    def __init__(self):
        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def get_llm(self):
        return self.llm