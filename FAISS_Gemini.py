import faiss
import numpy as np
import json
import os
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configure Google Gemini API
genai.configure(api_key="AIzaSyB1GAGY520fcc1xoUqw7ogwdQeb5Y-uHcM")

EMBEDDING_MODEL = "models/text-embedding-004"  # Use the correct embedding model

# Load historical data from JSON
with open("C:\\Users\\Mandoo\\Downloads\\hist.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract lessons
def extract_lessons(data):
    lessons = []
    for chapter in data["chapters"]:
        for lesson in chapter["lessons"]:
            lessons.append({
                "id": f"{chapter['chapter_number']}-{lesson['lesson_number']}",
                "title": lesson["title"],
                "content": lesson["content"]
            })
    return lessons

lessons = extract_lessons(data)

# Generate embeddings using Gemini
def generate_embedding(text):
    response = genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type="retrieval_document")
    return np.array(response["embedding"], dtype=np.float32)

# FAISS Index Setup
dimension = 768  # Must match the embedding model output
index = None
lesson_ids = []
lesson_texts = []

# Function to build and save the FAISS index if it doesn't exist
def build_faiss_index():
    global index, lesson_ids, lesson_texts

    # If the index already exists, just load it
    if os.path.exists("faiss_index.bin"):
        print("📂 Loading existing FAISS index...")
        index, lesson_ids, lesson_texts = load_faiss_index()
        return
    
    print("🛠 Building FAISS index...")

    index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)

    lesson_vectors = []
    
    for lesson in lessons:
        embedding = generate_embedding(lesson["content"])
        lesson_vectors.append(embedding)
        lesson_ids.append(lesson["id"])
        lesson_texts.append(lesson["content"])

    lesson_vectors = np.array(lesson_vectors, dtype=np.float32)
    faiss.normalize_L2(lesson_vectors)  # Normalize for better performance
    index.add(lesson_vectors)

    # Save index for future use
    faiss.write_index(index, "faiss_index.bin")
    with open("lesson_ids.json", "w", encoding="utf-8") as f:
        json.dump({"lesson_ids": lesson_ids, "lesson_texts": lesson_texts}, f, ensure_ascii=False)

    print(f"✅ FAISS index built and saved with {len(lesson_ids)} lessons!")

# Load FAISS index
def load_faiss_index():
    index = faiss.read_index("faiss_index.bin")
    with open("lesson_ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return index, data["lesson_ids"], data["lesson_texts"]

# Search Function
def search_lessons(query, top_k=5):
    global index, lesson_ids, lesson_texts

    # Ensure index is loaded
    if index is None:
        index, lesson_ids, lesson_texts = load_faiss_index()

    query_embedding = generate_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_embedding)  # Normalize BEFORE searching

    distances, indices = index.search(query_embedding, top_k)
    
    results = [lesson_texts[i] for i in indices[0] if i < len(lesson_texts)]

    if not results:
        return ["لم أجد معلومات دقيقة حول هذا الموضوع، لكن يمكنك إعادة صياغة السؤال أو توضيحه."]
    
    return results

# Generate Response with AI
def generate_response(question, context):
    # Convert context list to a string
    context_text = "\n\n".join(context) if isinstance(context, list) else context

    # If context is empty, generate a general historical response
    if not context_text.strip():
        prompt = f"""
        أنت مساعد تعليمي في مادة التاريخ، وعليك الإجابة عن السؤال التالي بطريقة شاملة:
        
        **السؤال:** {question}
        
        **الإجابة يجب أن تكون مرتبة وفق العناصر التالية:**
        - الخلفية التاريخية
        - الأسباب والعوامل المؤثرة
        - النتائج والتأثيرات اللاحقة
        - الخاتمة: ملخص لأهم النقاط
        
        استخدم أسلوبًا واضحًا وسهل الفهم، ولا تعتمد على المعلومات المتاحة فقط، بل استخدم معرفتك العامة بالتاريخ.
        """
    else:
        prompt = f"""
        أنت مساعد تعليمي في مادة التاريخ. استخدم المعلومات التالية للإجابة على السؤال:
        
        **السؤال:** {question}  
        **المعلومات المتاحة:**  
        {context_text}  

        **قم بتقديم الإجابة بشكل منظم وفقًا للعناصر التالية:**  
        - الخلفية التاريخية  
        - الأسباب والعوامل المؤثرة  
        - النتائج والتأثيرات اللاحقة  
        - الخاتمة: ملخص لأهم النقاط  
        """
    
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text


# Flask API
app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "السؤال مطلوب"}), 400

    related_lessons = search_lessons(question)
    response = generate_response(question, related_lessons)  # Pass list instead of string
    
    return jsonify({"answer": response})

@app.route("/")
def home():
    return "Welcome to the Arabic History Chatbot API with FAISS!"

if __name__ == "__main__":
    build_faiss_index()  # Ensure FAISS is built before running
    app.run(debug=True)
