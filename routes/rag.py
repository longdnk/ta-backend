import sys
import os
from transformers import AutoTokenizer

from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from pydantic import BaseModel, Field
from fastapi import APIRouter, status, Request

from os.path import join, realpath
from sqlalchemy.exc import SQLAlchemyError

os.environ["TOKENIZERS_PARALLELISM"] = "true"

sys.path.append(realpath(join(realpath(__file__), "..", "..")))


rag_router = APIRouter(prefix="/rags", tags=["rags"])
print("===Rag Router===")


class RequestItem(BaseModel):
    text: str


class RAGSystem:
    """Sentence embedding based Retrieval Based Augmented generation.
    Given database of pdf files, retriever finds num_retrieved_docs relevant documents
    """

    def __init__(self, num_retrieved_docs=10):
        self.num_docs = num_retrieved_docs
        loader = CSVLoader("routes/dataset.csv")
        documents = loader.load()

        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=tokenizer, chunk_size=200, chunk_overlap=10
        )

        all_splits = text_splitter.split_documents(documents)

        # Create a vectorstore database
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        self.vector_db = Chroma.from_documents(
            documents=all_splits, embedding=embeddings, persist_directory="chroma_db"
        )

        self.retriever = self.vector_db.as_retriever()

    def retrieve(self, query):
        # Retrieve top k similar documents to query
        docs = self.retriever.invoke(query, k=self.num_docs)
        return docs

    def query(self, query):
        # Generate the answer
        context = self.retrieve(query)
        data = ""
        for item in list(context):
            data += item.page_content

        return data


rag_system = RAGSystem()

@rag_router.post("", status_code=status.HTTP_201_CREATED)
async def retrieval_in_rag(request_item: RequestItem):
    try:
        result = rag_system.query(request_item.text)
        return {
            "message": "Rag Retrieval Done success",
            "code": status.HTTP_201_CREATED,
            "data": result,
        }

    except SQLAlchemyError as e:
        # Xử lý ngoại lệ nếu có lỗi xảy ra
        return {
            "message": "Error",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": str(e),
        }
