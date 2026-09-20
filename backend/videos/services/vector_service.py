from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .embedding_service import EmbeddingService


CHROMA_DIR = "vector_db"
COLLECTION_NAME = "video_transcripts"


class VectorService:

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def build_vector_store(self, transcript, video_id):
        print("Building vector store")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_text(transcript)

        docs = [
            Document(
                page_content=chunk,
                metadata={
                    "video_id": video_id,
                    "chunk_index": i
                }
            )
            for i, chunk in enumerate(chunks)
        ]

        ids = [
            f"video_{video_id}_chunk_{i}"
            for i in range(len(chunks))
        ]

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_service.embeddings,
            persist_directory=CHROMA_DIR,
            )
        # Remove existing chunks for this video
        existing = vector_store.get(
        where={"video_id": video_id}
        )

        if existing["ids"]:
            vector_store.delete(
            ids=existing["ids"]
        )


        vector_store.add_documents(
        documents=docs,
        ids=ids
        )

        return vector_store

    
    def get_vector_store(self):
        return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=self.embedding_service.embeddings,
        persist_directory=CHROMA_DIR
        )

    def get_retriever(self, vector_store, video_id, k=4):
        return vector_store.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {
                    "video_id": video_id
                }
            },
            search_type="similarity"
        )

    def delete_video_vectors(self, video_id):
        vector_store = self.get_vector_store()

        existing = vector_store.get(
            where={"video_id": video_id}
        )

        if existing["ids"]:
            vector_store.delete(
                ids=existing["ids"]
            )