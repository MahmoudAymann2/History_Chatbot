import faiss
import numpy as np
import json
import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random


# --- إعداد Google Gemini ---
genai.configure(api_key="AIzaSyDhV5xCVB_u0XJTPMuQmbEjymBtepUZtpI")
EMBEDDING_MODEL = "models/text-embedding-004"

# --- تحميل البيانات ---
with open("C:\\Users\\Mandoo\\Desktop\\Faiss_Gemini_Chatbot2\\hist.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# --- استخراج الدروس ---
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

# --- إنشاء Embedding ---
def generate_embedding(text):
    response = genai.embed_content(model=EMBEDDING_MODEL, content=text, task_type="retrieval_document")
    return np.array(response["embedding"], dtype=np.float32)

# --- إعداد FAISS ---
dimension = 768
index = None
lesson_ids = []
lesson_texts = []

def build_faiss_index():
    global index, lesson_ids, lesson_texts

    if os.path.exists("faiss_index.bin"):
        print("📂 Loading existing FAISS index...")
        index, lesson_ids, lesson_texts = load_faiss_index()
        return

    print("🛠 Building FAISS index...")
    index = faiss.IndexFlatL2(dimension)
    lesson_vectors = []

    for lesson in lessons:
        embedding = generate_embedding(lesson["content"])
        lesson_vectors.append(embedding)
        lesson_ids.append(lesson["id"])
        lesson_texts.append(lesson["content"])

    lesson_vectors = np.array(lesson_vectors, dtype=np.float32)
    faiss.normalize_L2(lesson_vectors)
    index.add(lesson_vectors)

    faiss.write_index(index, "faiss_index.bin")
    with open("lesson_ids.json", "w", encoding="utf-8") as f:
        json.dump({"lesson_ids": lesson_ids, "lesson_texts": lesson_texts}, f, ensure_ascii=False)

    print(f"✅ FAISS index built and saved with {len(lesson_ids)} lessons!")

def load_faiss_index():
    index = faiss.read_index("faiss_index.bin")
    with open("lesson_ids.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return index, data["lesson_ids"], data["lesson_texts"]

# --- البحث ---
def search_lessons(query, top_k=5):
    global index, lesson_ids, lesson_texts
    if index is None:
        index, lesson_ids, lesson_texts = load_faiss_index()

    query_embedding = generate_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(query_embedding, top_k)
    results = [lesson_texts[i] for i in indices[0] if i < len(lesson_texts)]

    if not results:
        return ["لم أجد معلومات دقيقة حول هذا الموضوع، لكن يمكنك إعادة صياغة السؤال أو توضيحه."]

    return results

def is_mcq(question: str) -> bool:
    return bool(re.search(r"[أ-ي]\-", question)) or "الإجابة" in question or "اختر" in question


def extract_final_answer(response: str):
    match = re.search(r"الإجابة\s+الصحيحة\s*[:：]?\s*\(?([أبجد])\)?", response)
    return match.group(1) if match else None

def generate_response(question, context):
    import random, re
    context_text = "\n\n".join(context) if isinstance(context, list) else context

    greetings = [
        "أكيد يا بطل! 💪 إليك الإجابة بشكل مبسط:",
        "بكل سرور، هذا ما وجدته لك 😊",
        "دعني أوضح لك كأننا في الحصة 👇",
        "سعيد بسؤالك! وهنا الشرح بالتفصيل:"
    ]
    closings = [
        "\nهل لديك سؤال آخر؟ 🤗",
        "\nبإمكانك تسأل عن أي درس تحب! 📘",
        "\nلا تتردد تسألني أي وقت 😉"
    ]

    if is_mcq(question):
        prompt = f"""أنت مساعد ذكي متخصص في التاريخ لطلاب الثانوية العامة في مصر.
أجب عن السؤال التالي إجابة تفصيلية تشرح فقط لماذا الخيار الصحيح هو الأنسب.
لا تذكر أو تحلل بقية الاختيارات أبدًا.
وفي نهاية إجابتك، اكتب في سطر منفصل:
الإجابة الصحيحة: (أ / ب / ج / د)

السؤال: {question}
المصادر:
{context_text}"""
    else:
        prompt = f"""أنت مساعد ذكي متخصص في التاريخ لطلاب الثانوية العامة في مصر.
أجب عن السؤال التالي بإجابة مبسطة وشاملة تساعد الطالب على الفهم الجيد.
لا تستخدم تنسيق أسئلة اختيار من متعدد، ولا تذكر أي إجابة صحيحة على شكل (أ / ب / ج / د).
اكتفِ بشرح مفصل مناسب للسؤال بناءً على المعلومات المتاحة في المصادر.

السؤال: {question}
المصادر:
{context_text}"""

    # Call Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
    response = model.generate_content(prompt).text.strip()

    # Enforce clean ending for MCQ
    if is_mcq(question):
        final_letter = extract_final_answer(response)
        if not final_letter:
            # Try to guess last option mentioned in text (usually the correct one)
            fallback_match = re.findall(r"\b[أبجد]\b", response)
            if fallback_match:
                guessed = fallback_match[-1]
                response += f"\nالإجابة الصحيحة: {guessed}"
            else:
                response += "\nالإجابة الصحيحة: غير محددة"
    else:
        # Remove any hallucinated MCQ-like endings
        response = re.sub(r"\bالإجابة\s+الصحيحة\s*[:：]?\s*\(?[أبجد]?\)?", "", response)
        response = re.sub(r"\n+الإجابة.*$", "", response, flags=re.MULTILINE)
        response = re.sub(r"\n{2,}", "\n\n", response).strip()

    # Final wrapping
    final_response = f"{random.choice(greetings)}\n\n{response}\n\n{random.choice(closings)}"
    return final_response


# --- Flask API ---
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/ask": {"origins": "*"}})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "السؤال مطلوب"}), 400

    related_lessons = search_lessons(question)
    response = generate_response(question, related_lessons)
    return jsonify({"answer": response})

if __name__ == "__main__":
    build_faiss_index()
    app.run(debug=True)
