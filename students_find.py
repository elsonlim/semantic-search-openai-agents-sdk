from agents import Agent, ModelSettings, function_tool
from dotenv import load_dotenv
load_dotenv(override=True)

import os 
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

## pinecone variables
PINECONE_INDEX_NAME = "openai-agents-sdk-test" # Todo: move to env var
DIMENSIONS = 768 # Todo: move to env var
METIX = "cosine"   # Todo: move to env var
EMBEDDING_MODEL = "multi-qa-mpnet-base-dot-v1"


## Connect to Pinecone
pc = Pinecone(api_key = os.environ.get("PINECONE_API_KEY"), environment = os.environ.get("PINECONE_ENV"))

try:
    # print(f"Checking if index '{pc.list_indexes()}' exists...")
    if PINECONE_INDEX_NAME not in [index.name for index in pc.list_indexes()]:
        print(f"Error: Index '{PINECONE_INDEX_NAME}' does not exist. Please create and populate it first.")
        exit() 

    # Fetch the index
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    print(f"Connected to Pinecone index '{PINECONE_INDEX_NAME}'. Index description:")
    print(pinecone_index.describe_index_stats()) # Print some stats about the index
except Exception as e:
    print(f"Failed to connect to Pinecone or find index: {e}")
    exit()


def ask_about_student(query_text):
    # --- 4. Embed the Query ---
    try:
        print(f"Embedding query using model '{EMBEDDING_MODEL}'...")
        model = SentenceTransformer(EMBEDDING_MODEL)
        try:
            query_vector = model.encode(query_text, show_progress_bar = False).tolist()
        except Exception as e:
            print(f"Error embedding student data: {e}")

        print("Query embedded successfully.")
    except Exception as e:
        print(f"Error embedding query: {e}")
        exit()

    ### --- 5. Query the Pinecone Index ---
    try:
        query_results = pinecone_index.query(
            vector=[query_vector],
            top_k=3,           # Number of top similar results to retrieve
            include_values=False, # Set to True if you want to retrieve the vector values themselves
            include_metadata=True # Set to True to retrieve the associated metadata
            # filter={           # Optional: Add filters based on metadata
            #    "grade": {"$gte": 5} # Example: Only search among students with grade 5 or higher
            # }
        )
        return query_results

    except Exception as e:
        print(f"Error querying Pinecone index: {e}")

# --- 3. Embed the Query ---
# query_text = "Name is Ethan"
# query_results = ask_about_student(query_text)

# print("\n--- Query Results ---")
# if query_results.matches:
#     for match in query_results.matches:
#         print(f"  ID: {match.id}, Score: {match.score:.4f}")
#         if match.metadata:
#             print(f"    First Name: {match.metadata.get('FirstName')}")
#             print(f"    Last Name: {match.metadata.get('LastName')}")
#             print(f"    Grade: {match.metadata.get('Grade')}")
#             print(f"    Date of Birth: {match.metadata.get('DateOfBirth')}")
#             print(f"    Full Text Description: {match.metadata.get('full_text_description')}")
#         else:
#             print("    (No metadata returned for this match)")
# else:
#     print("  No matching students found.")

@function_tool
def search_student(query_text: str) -> str:
    query_results = ask_about_student(query_text)
    return query_results

agent = Agent(
    name="Students agent",
    instructions="""You are a helpful assistant that can search for students in the database.
    When a user asks about a student, you should use the search_student tool to find the student.
    You should only return the student's information, not any other information.
    If the user asks about a student that is not in the database, you should say "I don't know about that student."
    """,
    model="o3-mini",
    tools=[search_student],
)