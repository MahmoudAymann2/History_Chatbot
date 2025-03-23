import faiss
import numpy as np
import json
import pandas as pd
import google.generativeai as genai
from sklearn.metrics import precision_score, recall_score

# Configure Google Gemini API (Ensure the key is correct)
genai.configure(api_key="AIzaSyB1GAGY520fcc1xoUqw7ogwdQeb5Y-uHcM")

EMBEDDING_MODEL = "models/text-embedding-004"
DIMENSION = 3072  # Ensure this matches FAISS index

# Convert Excel dataset to JSON for evaluation
def convert_excel_to_json(excel_path, json_path):
    df = pd.read_excel(excel_path)

    eval_data = []
    for _, row in df.iterrows():
        eval_data.append({
            "question": row["Question"],  
            "relevant_answer": row["Answer"]  # Renamed to match existing dataset
        })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=4)

# Convert dataset
convert_excel_to_json("C:\\Users\\Mandoo\\Desktop\\Graduation Project\\Q&A_All_Chapters.xlsx", "evaluation_dataset.json")

print("✅ Dataset converted successfully!")

# Load FAISS index and lesson metadata
def load_faiss_index():
    if not os.path.exists("faiss_index.bin"):
        raise FileNotFoundError("❌ FAISS index not found. Please run the chatbot script first.")
    
    index = faiss.read_index("faiss_index.bin")
    with open("lesson_ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return index, data["lesson_ids"], data["lesson_texts"]

index, lesson_ids, lesson_texts = load_faiss_index()

# Load evaluation dataset (golden dataset)
with open("evaluation_dataset.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# Generate embeddings using Gemini (to match FAISS index)
def generate_embedding(text):
    try:
        response = genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type="retrieval_document")
        return np.array(response["embedding"], dtype=np.float32)
    except Exception as e:
        print(f"❌ Embedding generation error: {e}")
        return np.zeros(DIMENSION, dtype=np.float32)  # Return a zero vector if an error occurs

# Evaluation Metrics
def precision_at_k(retrieved, relevant, k=5):
    retrieved_at_k = retrieved[:k]
    return len(set(retrieved_at_k) & set(relevant)) / k

def recall_at_k(retrieved, relevant, k=5):
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)

def mrr(retrieved, relevant):
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1 / rank
    return 0

# Search function using FAISS
def search_faiss(query, top_k=5):
    query_embedding = generate_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_embedding)
    distances, indices = index.search(query_embedding, top_k)
    return [lesson_ids[i] for i in indices[0] if i < len(lesson_ids)]

# Run evaluation
total_precision, total_recall, total_mrr = 0, 0, 0
num_queries = len(eval_data)

for sample in eval_data:
    query = sample["question"]
    relevant_answer = sample["relevant_answer"]

    # Find index of relevant_answer in lesson_texts
    relevant_indices = [i for i, text in enumerate(lesson_texts) if text == relevant_answer]
    
    if not relevant_indices:
        print(f"⚠️ No matching lesson found for: {query}")
        continue

    retrieved_docs = search_faiss(query, top_k=5)

    total_precision += precision_at_k(retrieved_docs, relevant_indices, k=5)
    total_recall += recall_at_k(retrieved_docs, relevant_indices, k=5)
    total_mrr += mrr(retrieved_docs, relevant_indices)

# Compute averages
print(f"📌 Precision@5: {total_precision / num_queries:.4f}")
print(f"📌 Recall@5: {total_recall / num_queries:.4f}")
print(f"📌 MRR: {total_mrr / num_queries:.4f}")
