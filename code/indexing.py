# Load the libraries
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# STEP 1: Loading of RAW documents --> PDF files

def load_raw_docs(data):
    loader = DirectoryLoader(
        data, # Folder Path
        glob = "*.pdf", # File type filter
        loader_cls = PyPDFLoader # Which loader to use
    )

    documents = loader.load()
    return documents

data_path = "../data/"
documents = load_raw_docs(data = data_path)

# View the Result
#print("Total Length of PDF Pages: ", len(documents))
#print("-" * 50)
#print("Total characters: ", sum(len(doc.page_content) for doc in documents))
#print("-" * 50)
#print("Page Content of the First Document: ", documents[1].page_content)
#print("-" * 50)
#print("Metadata of the First Document: ", documents[1].metadata)

# STEP 2: Split the Documents into Chunks

def create_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 600, # Number of characters per chunk
        chunk_overlap = 100
    )

    text_chunks = text_splitter.split_documents(docs)
    return text_chunks

text_chunks = create_chunks(docs = documents)

# View the Result
# 1. Checking total number of chunks
#print("Total Chunks: ", len(text_chunks))

# 2. Inspect a few random chunks
#for i in range(5):
#    print(f"\n--- Chunk {i} ---")
#    print(text_chunks[i].page_content)

# STEP 3: Defining the Embedding Model --> Provider: Hugging Face

def get_embedding_model(emb_model):
    embedding_model = HuggingFaceEmbeddings(model_name = emb_model)
    return embedding_model

emb_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = get_embedding_model(emb_model = emb_model_name)

# STEP 4: Store the Embeddings into Vector DB --> Provider: FAISS

vector_db_path = "../vector_store/db_faiss"

vector_db = FAISS.from_documents(text_chunks, embedding_model)
vector_db.save_local(vector_db_path)