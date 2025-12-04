from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader, TextLoader, JSONLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
import os

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDED_DEPLOYMENT_NAME"),
    openai_api_version=os.getenv("OPENAI_API_EMBEDDED_VERSION")
)
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# vector_store = Chroma(collection_name="first-rag",embedding_function=embeddings,persist_directory="./chroma_langchain_db")
vector_store = Chroma(
    collection_name="first-rag",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db")

def index_document_to_vectordb(file_path:str, file_id:int) -> bool:
    try:
        extension = os.path.splitext(file_path)[1].lower()
        if extension.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif extension.endswith(".docx") or file_path.endswith(".doc"):
            loader = Docx2txtLoader(file_path)
        elif extension.endswith(".html"):
            loader = UnstructuredHTMLLoader(file_path)
        elif extension.endswith(".csv"):
            loader = CSVLoader(file_path)
        elif extension.endswith(".json"):
            loader = JSONLoader(file_path=file_path, jq_schema=".body", metadata_func=lambda meta, _ : {"filename": meta["source"]})
        elif extension.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            print(f"Unsupported file type: {file_path}")
            return False

        docs = loader.load()
        all_splits = text_splitter.split_documents(docs)
        #vector1 = embeddings.embed_query(all_splits[0])
        
        for split in all_splits:
            split.metadata["file_id"] = file_id


        vector_store.add_documents(documents=all_splits)

        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    

def remove_document_from_vector_db(file_id:int)-> bool:
    try:
        docs = vector_store.get(
        where={"file_id":file_id}
        )

        print(f"{len(docs['ids'])} doc chunks found for file_id {file_id}")

        vector_store._collection.delete(
            where={"file_id":file_id}
        )

        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as ex:
        print(f"Error occurred while deleting document with file_id {file_id} from vector db: {str(ex)}")
        return False



