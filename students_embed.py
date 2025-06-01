# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

STUDENTS_CSV_FILE = "students.csv"
VECTOR_STORE_ID = "Students_Data_1"

# --- 1. Setup openai client ---
try:
    client = OpenAI()
    print("OpenAI client initialized.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please ensure your OPENAI_API_KEY is set.")
    exit()


# --- 2. Process CSV File for embedding ---
def process_csv_to_list_of_dictionary(csv_file_path):
    """Reads the CSV, processes rows into text, and saves to a .txt file."""
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found. Please create it first.")
        return False

    student_data_list = df.to_dict(orient='records')
    return student_data_list

student_data_list = process_csv_to_list_of_dictionary(STUDENTS_CSV_FILE)

print(student_data_list)

# Setup Pinecone
pc = Pinecone(api_key = os.environ.get("PINECONE_API_KEY"), environment = os.environ.get("PINECONE_ENV"))

## pinecone variables
PINECONE_INDEX_NAME = "openai-agents-sdk-test" # Todo: move to env var
DIMENSIONS = 768 # Todo: move to env var
METIX = "cosine"   # Todo: move to env var
EMBEDDING_MODEL = "multi-qa-mpnet-base-dot-v1"

## Check if index exists, if so delete it
if PINECONE_INDEX_NAME in [index.name for index in pc.list_indexes()]:
    pc.delete_index(PINECONE_INDEX_NAME)
    print(f"{PINECONE_INDEX_NAME} succesfully deleted.")
else:
     print(f"{PINECONE_INDEX_NAME} not in index list.")

## recreate index
pc.create_index(
    name = PINECONE_INDEX_NAME, 
    dimension = DIMENSIONS, 
    metric = METIX, 
    spec = ServerlessSpec(
        cloud = "aws", 
        region = "us-east-1")
    )

## fetch the index
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# Choosing the model for embedding the data
model = SentenceTransformer('EMBEDDING_MODEL') # Model needs to match number of dimensions, for multi-qa-mpnet-base-dot-v1 it is 768

# embeding the data
vectors_to_upsert = []
for student in student_data_list:
    # 1. ID
    id = str(student["StudentID"])

    # Embedding values
    text_to_embed = (
        f"Student ID: {student['StudentID']}, Name: {student['FirstName']} {student['LastName']}, "
        f"Date of Birth: {student['DateOfBirth']}, Grade: {student['Grade']}, "
        f"Email: {student['EmailAddress']}"
    )

    try:
        values = model.encode(text_to_embed, show_progress_bar = False)
    except Exception as e:
        print(f"Error embedding student data: {e}")
        continue

    # Create Medata data
    metadata = {
        **student,
        "full_text_description": text_to_embed # Store the original text for easy retrieval/context
    }

    vectors_to_upsert.append({
        "id": id,
        "values": values,
        "metadata": metadata
    })

## Upload to pinecode by batch
BATCH_SIZE = 50
if vectors_to_upsert:
    print(f"\nUpserting {len(vectors_to_upsert)} vectors to index '{PINECONE_INDEX_NAME}'...")
    for i in range(0, len(vectors_to_upsert), BATCH_SIZE):
        batch = vectors_to_upsert[i:i + BATCH_SIZE]
        try:
            pinecone_index.upsert(vectors=batch)
            print(f"Upserted batch {i//BATCH_SIZE + 1} of {len(vectors_to_upsert)//BATCH_SIZE + 1 if len(vectors_to_upsert)%BATCH_SIZE!=0 else len(vectors_to_upsert)//BATCH_SIZE}.")
        except Exception as e:
            print(f"Error during upsert of batch starting at index {i}: {e}")
    print("All student data upserted successfully!")
else:
    print("No vectors prepared for upsert.")

# Add the data to the index


# Query the data