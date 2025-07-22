import pandas as pd
import re
import requests

EVAL_EXCEL_PATH = "Evalation_Data/emthan 2021 2nd.xlsx"
OUTPUT_EXCEL_PATH = "ch1&2_questions_with_model_answers.xlsx"
API_URL = "http://127.0.0.1:5000/ask"

# --- Utility Functions ---
def clean_text(text):
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"[^(\u0600-\u06FF\s0-9.,؟!)]", "", text)
    return cleaned.strip()

def cosine_sim(text1, text2):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf = vectorizer.fit_transform([text1, text2])
        sim_score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return sim_score
    except ValueError:
        return 0.0

def extract_mcq_answer_code(model_output: str) -> str:
    """
    Try to extract the selected MCQ letter (أ, ب, ج, د) from model output.
    Supports multiple formats, including: 
    "الإجابة الصحيحة: د", "**د**", "(ب)", etc.
    """
    if not model_output:
        return ""

    # Match structured answer like "الإجابة الصحيحة: د"
    match = re.search(r"الإجابة\s+(?:النهائية|الصحيحة)(?:\s+هي)?\s*[:：]?\s*([أ-د])", model_output)
    if match:
        return match.group(1)

    # Match bolded Arabic letter: **د**
    match = re.search(r"\*\*\s*([أ-د])\s*\*\*", model_output)
    if match:
        return match.group(1)

    # Match parenthesized letter: (أ)
    match = re.search(r"\(\s*([أ-د])\s*\)", model_output)
    if match:
        return match.group(1)

    # Match standalone Arabic letter surrounded by spaces or line
    match = re.search(r"\b([أ-د])\b", model_output)
    if match:
        return match.group(1)

    return ""

def detect_intent(question):
    is_mcq = (
        "اختر" in question.lower() or
        "أي مما يلي" in question.lower() or
        re.search(r"\(أ\)|\(ب\)|\(ج\)|\(د\)|\(هـ\)", question) or
        len(re.findall(r"[‌\s][أبجده]-\s", question)) >= 2
    )
    return "mcq" if is_mcq else "general"

# --- Main Evaluation Logic ---
def run_evaluation():
    try:
        df = pd.read_excel(EVAL_EXCEL_PATH)
        print(f"✅ Loaded evaluation questions from '{EVAL_EXCEL_PATH}'")
    except FileNotFoundError:
        print(f"❌ Error: File '{EVAL_EXCEL_PATH}' not found.")
        return

    df["model_answer"] = ""
    df["cosine_similarity"] = 0.0
    df["detected_intent"] = ""
    df["predicted_choice"] = ""

    correct_mcq_count = 0
    total_mcq = 0

    print("\n🚀 Starting evaluation...\n")

    for idx, row in df.iterrows():
        question = str(row["Questions"]).strip()
        correct_answer = str(row["Answers"]).strip()

        print(f"--- Evaluating Question {idx + 1}/{len(df)} ---")
        print(f"Question: {question}")

        try:
            response = requests.post(API_URL, json={"question": question})
            if response.status_code != 200:
                print(f"⚠️ API Error: {response.status_code}")
                df.at[idx, "model_answer"] = "API Error"
                continue

            model_reply = response.json().get("answer", "").strip()
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            df.at[idx, "model_answer"] = "Request Failed"
            continue

        intent = detect_intent(question)
        df.at[idx, "detected_intent"] = intent
        df.at[idx, "model_answer"] = model_reply

        if intent == "mcq":
            total_mcq += 1
            predicted = extract_mcq_answer_code(model_reply)
            df.at[idx, "predicted_choice"] = predicted
            score = 1.0 if predicted.strip() == correct_answer.strip() else 0.0
            if score == 1.0:
                correct_mcq_count += 1
        else:
            # Use semantic similarity for general questions
            score = cosine_sim(clean_text(model_reply), clean_text(correct_answer))

        df.at[idx, "cosine_similarity"] = score

        print(f"Model Answer:\n{model_reply}")
        if intent == "mcq":
            print(f"Correct Answer: {correct_answer} | Predicted: {predicted}")
        else:
            print(f"Correct Answer (text): {correct_answer}")
        print(f"Score: {score:.3f}")
        print("-" * 60)

    # Save output
    try:
        df.to_excel(OUTPUT_EXCEL_PATH, index=False)
        print(f"\n✅ Evaluation complete! Results saved to '{OUTPUT_EXCEL_PATH}'.")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

    # Print MCQ Accuracy
    if total_mcq > 0:
        accuracy = (correct_mcq_count / total_mcq) * 100
        print(f"\n📊 MCQ Accuracy: {correct_mcq_count}/{total_mcq} = {accuracy:.2f}%")

# Run evaluation if this is the main script
if __name__ == "__main__":
    run_evaluation()
