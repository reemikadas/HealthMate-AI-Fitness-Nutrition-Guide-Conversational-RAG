# =================================================
# Load the libraries
# =================================================
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
#from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder

# =================================================
# STEP 1: Load the Environment
# =================================================
load_dotenv()

# =================================================
# STEP 2: Setup the API Key --> Provider: Groq
# =================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# =================================================
# STEP 3: Define the LLM model
# =================================================
# GROQ_MODEL_NAME = "llama-3.1-8b-instant"
GROQ_MODEL_NAME = "openai/gpt-oss-20b"

llm = ChatGroq(
    model = GROQ_MODEL_NAME,
    temperature = 0, # For creativity in answers
    max_tokens = 512, # Max No. of tokens to generate
    api_key = GROQ_API_KEY
)

# ==================================================================================================
# STEP 4: Load the Knowledge Base --> Embedding Provider: HuggingFace | Vector_db provider: FAISS
# ==================================================================================================
DB_FAISS_PATH = "../vector_store/db_faiss"

hugface_emb_model = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = HuggingFaceEmbeddings(model_name = hugface_emb_model)

vector_db = FAISS.load_local(
    DB_FAISS_PATH,
    embedding_model,
    allow_dangerous_deserialization = True
)

# =================================================
# STEP 5: Building a RAG Chain
# =================================================

# STEP 5(a): Query Rewriting Prompt
# =================================================
contextualize_q_system_prompt = """
Given a chat history and the latest user question,
rewrite the latest question into a standalone question
that can be understood without the chat history.

Do NOT answer the question.
Only rewrite it if needed.
Otherwise, return it as-is.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])


# STEP 5(b): Defining Chat Prompt
# =================================================
#rag_predefined_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

rag_custom_prompt = ChatPromptTemplate.from_messages([("system", """
You are an expert AI Fitness and Nutrition Assistant.
                                                     
Your role is to help users with:
- workout planning
- exercise guidance
- muscle building
- fat loss
- nutrition advice
- meal suggestions
- recovery tips
- healthy lifestyle habits
                                                     
Use ONLY the provided context to answer the question.

If the answer is not available in the context:
- Say: "I could not find relevant information in the knowledge base."
- Do NOT make up information.

Guidelines:
- Keep answers clear, concise, and beginner-friendly.
- Use bullet points when appropriate.
- Give actionable recommendations.
- If discussing workouts, mention sets/reps only if available in context.
- If discussing nutrition, explain calories/protein/macros only if available in context.
- Avoid medical diagnosis or unsafe health advice.
- If the user asks about injuries, medications, or serious medical conditions, suggest consulting a healthcare professional.

<context>
{context}
</context>
"""),

    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# STEP 5(c): Document combiner chain for stuffing chunks into prompt and sending it to LLM
# =================================================
#doc_combiner_chain = create_stuff_documents_chain(
#    llm,
#    rag_predefined_chat_prompt
#)

doc_combiner_chain = create_stuff_documents_chain(
    llm,
    rag_custom_prompt
)

# STEP 5 (d): Combining Retriever with Document Combiner
# =================================================
retriever = vector_db.as_retriever(
    search_kwargs = {'k': 3} # Top 3 chunks 
)

history_aware_retriever = create_history_aware_retriever(
    llm,
    retriever,
    contextualize_q_prompt
)

#rag_pipe = create_retrieval_chain(
#    retriever,
#    doc_combiner_chain
#)

rag_pipe = create_retrieval_chain(
    history_aware_retriever,
    doc_combiner_chain
)

# =================================================
# Query Function
# =================================================
def ask_healthmate(query, chat_history):

    # Convert Streamlit History
    formatted_chat_history = []

    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            formatted_chat_history.append(
                ("human", msg["message"])
            )
        
        elif msg["role"] == "assistant":
            formatted_chat_history.append(
                ("ai", msg["message"])
            )
    
    # Invoke Conversational RAG
    response = rag_pipe.invoke({
        "input" : query,
        "chat_history" : formatted_chat_history
    })

    answer = response["answer"]
    docs = response["context"]

    # Sources
    sources = []

    for doc in docs:
        source = doc.metadata.get(
            "source", "unknown"
        )

        page = doc.metadata.get(
            "page", "N/A"
        )

        source_name = source.split("/")[-1]

        sources.append(
            f"{source_name} - (Page {page})"
        )
    
    return answer, list(set(sources))

#def ask_healthmate(query):
#    response = rag_pipe.invoke({"input" : query})
#    answer = response["answer"]
#    docs = response["context"]

#    sources = []

#    for doc in docs:
#        source = doc.metadata.get("source", "Unknown")
#        page = doc.metadata.get("page", "N/A")

        # Clean File Name
#        source_name = source.split("/")[-1]

#        sources.append(f"{source_name} - (Page {page})")

#    return answer, list(set(sources))

# =================================================
# Evaluation Function
# =================================================
def ask_healthmate_for_eval(query):
    # Invoke RAG Pipeline
    response = rag_pipe.invoke({
        "input" : query,
        "chat_history" : []
    })

    answer = response["answer"]

    docs = response["context"]

    # Extract retrieved chunk text
    #retrieved_chunks = [
    #    doc.page_content for doc in docs
    #]

    return {
        "question" : query,
        "answer" : answer,
        "documents": docs
        # "contexts" : retrieved_chunks
    }

# =================================================
# Test with few queries
#user_query = input("Write your Query Here: ")
#response = rag_pipe.invoke({'input' : user_query})
#result = response["answer"]
#docs = response["context"]

#sources = set()

#for doc in docs:
#    source = doc.metadata.get("source", "Unknown")
#    page = doc.metadata.get("page", "N/A")

    # Clean file name
#    source_name = source.split("/")[-1]

#    sources.add(f"{source_name} (Page {page})")

#print("RESULT:\n", result)

#print("\nSOURCE DOCUMENTS:")
#for source in sources:
#    print("-", source)