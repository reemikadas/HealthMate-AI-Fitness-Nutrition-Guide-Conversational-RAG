# =================================================
# Load the libraries
# =================================================
import os
from dotenv import load_dotenv
from typing_extensions import Annotated, TypedDict
from langchain_groq import ChatGroq
from langsmith import Client
from rag_pipeline import ask_healthmate_for_eval

# =================================================
# Setting up the environment variables
# =================================================
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# =================================================
# RAG Evaluators
# =================================================

# =================================================
# 1. CORRECTNESS: Response Vs Reference Anaswer
# Goal: Measure “how similar/correct is the RAG chain answer,
#       relative to a ground-truth answer”
# Mode: Requires a ground truth (reference) answer supplied through a dataset
# Evaluator: Use LLM-as-judge to assess answer correctness.
# =================================================
# =================================================
# Grade Output Schema
# =================================================
class CorrectnessGrade(TypedDict):
    # Note that the order in the fields are defined is the order in which the model will generate them.
    # It is useful to put explanations before responses because it forces the model to think through
    # Its final response before generating it:
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    correct: Annotated[bool, ..., "True if the answer is correct, False otherwise."]

# =================================================
# Grade Prompt
# =================================================
correctness_instructions = """You are a teacher grading a quiz. You will be given a QUESTION, the GROUND TRUTH (correct) ANSWER, and the STUDENT ANSWER. Here is the grade criteria to follow:
(1) Grade the student answers based ONLY on their factual accuracy relative to the ground truth answer. (2) Ensure that the student answer does not contain any conflicting statements.
(3) It is OK if the student answer contains more information than the ground truth answer, as long as it is factually accurate relative to the ground truth answer.

Correctness:
A correctness value of True means that the student's answer meets all the criteria.
A correctness value of False means that the student's answer does not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. Avoid simply stating the correct answer at the outset."""

# =================================================
# Grader LLM
# =================================================
# GRADER_MODEL_NAME = "openai/gpt-oss-safeguard-20b"
GRADER_MODEL_NAME = "qwen/qwen3-32b"

correctness_llm = ChatGroq(
    model = GRADER_MODEL_NAME,
    temperature = 0
).with_structured_output(
    CorrectnessGrade,
    method = "json_schema",
    strict  = True
)

# =================================================
# Custom Correctness Evaluator
# =================================================
def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    """An evaluator for RAG answer accuracy"""
    answers = f"""\
    QUESTION: {inputs['question']}
    GROUND TRUTH ANSWER: {reference_outputs['answer']}
    STUDENT ANSWER: {outputs['answer']}"""

    # Run Evaluator
    grade = correctness_llm.invoke([
        {"role": "system", "content": correctness_instructions},
        {"role": "user", "content": answers}
    ])
    return grade["correct"]

# =================================================
# 2. RELEVANCE: Response Vs Input
# Goal: Measure “how well does the generated response address the initial user input”
# Mode: Does not require reference answer, because it will compare the answer to the input question
# Evaluator: Use LLM-as-judge to assess answer relevance, helpfulness, etc.
# =================================================

# =================================================
# Grade Output Schema
# =================================================
class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "Provide the score on whether the answer addresses the question"]

# =================================================
# Grade Prompt
# =================================================
relevance_instructions = """You are a teacher grading a quiz. You will be given a QUESTION and a STUDENT ANSWER. Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is concise and relevant to the QUESTION
(2) Ensure the STUDENT ANSWER helps to answer the QUESTION

Relevance:
A relevance value of True means that the student's answer meets all the criteria.
A relevance value of False means that the student's answer does not meet all the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. Avoid simply stating the correct answer at the outset."""

# =================================================
# Grader LLM
# =================================================
relevance_llm = ChatGroq(
    model = GRADER_MODEL_NAME,
    temperature = 0
).with_structured_output(
    RelevanceGrade,
    method = "json_schema",
    strict = True
)

# =================================================
# Custom Relevance Evaluator
# =================================================
def relevance(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer helpfulness."""
    answer = f"QUESTION: {inputs['question']}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = relevance_llm.invoke([
        {"role": "system", "content": relevance_instructions},
        {"role": "user", "content": answer}
    ])
    
    return grade["relevant"]

# =================================================
# 3. GROUNDEDNESS: Response Vs Retrieved Docs
# Goal: Measure “to what extent does the generated response agree with the retrieved context”
# Mode: Does not require reference answer, because it will compare the answer to the retrieved context
# Evaluator: Use LLM-as-judge to assess faithfulness, hallucinations, etc.
# =================================================

# =================================================
# Grade Output Schema
# =================================================
class GroundedGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    grounded: Annotated[bool, ..., "Provide the score on if the answer hallucinates from the documents"]

# =================================================
# Grade Prompt
# =================================================
grounded_instructions = """You are a teacher grading a quiz. You will be given FACTS and a STUDENT ANSWER. Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is grounded in the FACTS. (2) Ensure the STUDENT ANSWER does not contain "hallucinated" information outside the scope of the FACTS.

Grounded:
A grounded value of True means that the student's answer meets all the criteria.
A grounded value of False means that the student's answer does not meet all the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. Avoid simply stating the correct answer at the outset."""

# =================================================
# Grader LLM
# =================================================
grounded_llm = ChatGroq(
    model = GRADER_MODEL_NAME,
    temperature = 0
).with_structured_output(
    GroundedGrade,
    method = "json_schema",
    strict = True
)

# =================================================
# Custom Groundedness Evaluator
# =================================================
def groundedness(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer groundedness."""

    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = grounded_llm.invoke([
        {"role": "system", "content": grounded_instructions},
        {"role": "user", "content": answer}
    ])

    return grade["grounded"]

# =================================================
# 4. RETRIEVAL RELEVANCE: Retrieved docs Vs Input
# Goal: Measure “how relevant are my retrieved results for this query”
# Mode: Does not require reference answer, because it will compare the question to the retrieved context
# Evaluator: Use LLM-as-judge to assess relevance
# =================================================

# =================================================
# Grade Output Schema
# =================================================
class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "True if the retrieved documents are relevant to the question, False otherwise."]

# =================================================
# Grade Prompt
# =================================================
retrieval_relevance_instructions = """You are a teacher grading a quiz. You will be given a QUESTION and a set of FACTS provided by the student. Here is the grade criteria to follow:
(1) Your goal is to identify FACTS that are completely unrelated to the QUESTION
(2) If the facts contain ANY keywords or semantic meaning related to the question, consider them relevant
(3) It is OK if the facts have SOME information that is unrelated to the question as long as (2) is met

Relevance:
A relevance value of True means that the FACTS contain ANY keywords or semantic meaning related to the QUESTION and are therefore relevant.
A relevance value of False means that the FACTS are completely unrelated to the QUESTION.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. Avoid simply stating the correct answer at the outset."""

# =================================================
# Grader LLM
# =================================================
retrieval_relevance_llm = ChatGroq(
    model = GRADER_MODEL_NAME,
    temperature = 0
).with_structured_output(
    RetrievalRelevanceGrade,
    method = "json_schema",
    strict = True
)

# =================================================
# Custom Retrieval Relevance Evaluator
# =================================================
def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    """An evaluator for document relevance"""

    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nQUESTION: {inputs['question']}"

    grade = retrieval_relevance_llm.invoke([
        {"role": "system", "content": retrieval_relevance_instructions},
        {"role": "user", "content": answer}
    ])

    return grade["relevant"]

# =================================================
# Run RAG Evaluators
# =================================================

# =================================================
# LangSmith Client
# =================================================
client = Client()

# =================================================
# Target Function
# =================================================
def healthmate_target(inputs: dict):
    question = inputs["question"]
    response = ask_healthmate_for_eval(question)

    return {
        # Used by evaluators
        "answer": response["answer"],

        # Used by groundedness/retrieval relevance
        "documents": response["documents"],
    }

# =================================================
# Run Evaluation
# =================================================
dataset_name = "HealthMate Guide"

experiment_results = client.evaluate(
    healthmate_target,

    data = dataset_name,

    evaluators = [correctness, relevance, groundedness, retrieval_relevance],

    experiment_prefix = "healthmate-rag-eval",

    metadata = {
        "model": "qwen/qwen3-32b",
        "application": "HealthMate RAG",
        "chunk_size": 600,
        "retrieved_docs": 3
    }
)

# =================================================
# Convert Result into Structured Format
# =================================================
results_df = experiment_results.to_pandas()

# Print the Result
print(results_df)

# =================================================
# Save the Result in CSV
# =================================================
results_df.to_csv(
    "healthmate_eval_results.csv",
    index = False
)