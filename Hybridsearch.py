import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from langchain_cohere import CohereEmbeddings

load_dotenv()

app = FastAPI()


# Define a Pydantic model for the request body
class QueryRequest(BaseModel):
    text: str


# Initialize your models
class Citation:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile",
            temperature=0,
        )
        self.embeddings = CohereEmbeddings(
            model="embed-english-light-v3.0",
            cohere_api_key=os.getenv("COHERE_API_KEY"),
        )


class HybridSearcher:
    DENSE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL = "prithivida/Splade_PP_en_v1"

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(
            api_key=os.getenv("QDRANT_API_KEY"), location=os.getenv("QDRANT_URL_KEY")
        )
        self.qdrant_client.set_model(self.DENSE_MODEL)
        self.qdrant_client.set_sparse_model(self.SPARSE_MODEL)

    def search(self, text: str):
        search_result = self.qdrant_client.query(
            collection_name=self.collection_name,
            query_text=text,
            query_filter=None,  # No filters for now
            limit=10,  # Return the top 7 results
        )
        metadata = [hit.metadata for hit in search_result]
        return metadata


# Initialize instances of your classes
citation = Citation()
searcher = HybridSearcher("startupschunk2")


@app.post("/search")
def search(request: QueryRequest):
    try:
        # Perform the hybrid search using the provided text
        results = searcher.search(request.text)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
