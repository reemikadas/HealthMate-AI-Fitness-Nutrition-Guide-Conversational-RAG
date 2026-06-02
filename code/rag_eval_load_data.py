# =================================================
# Load the libraries
# =================================================
import os
from dotenv import load_dotenv
from langsmith import Client
from evaluation_dataset import evaluation_data

# =================================================
# Setting up the environment variables
# =================================================
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# =================================================
# Create Dataset and Test examples in LangSmith
# =================================================
# Create a Client who is responsible to upload your dataset and examples in Langsmith
client = Client()

# Create Empty Dataset in LangSmith
dataset_name = "HealthMate Guide"
try:
    dataset = client.create_dataset(
        dataset_name = dataset_name
    )

    print("New dataset created!")

except Exception:

    dataset = client.read_dataset(
        dataset_name = dataset_name
    )

    print("Existing dataset loaded!")

# Define and load test examples in the dataset
test_samples = evaluation_data
client.create_examples(
    dataset_id = dataset.id,
    examples = test_samples
)

print("Examples uploaded successfully!")