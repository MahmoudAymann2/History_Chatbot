<p align="left">
📜 Arabic History Chatbot with FAISS<br><br>

🚀 **Description**<br>
A smart chatbot for Arabic history using **Google Gemini AI** and **FAISS for efficient retrieval**.<br><br>

✅ **Features**<br>
✅ Embeds historical content using Google Gemini<br>
✅ FAISS-based similarity search for quick lookups<br>
✅ Flask API for easy integration<br>
✅ Supports Arabic Q&A<br>
✅ Evaluates search accuracy using Precision@5, Recall@5, and MRR<br><br>

🛠️ **Installation & Setup**<br><br>

1️⃣ **Clone the Repository**<br>
<code>git clone https://github.com/YOUR_USERNAME/arabic-history-chatbot.git</code><br>
<code>cd arabic-history-chatbot</code><br><br>

2️⃣ **Install Dependencies**<br>
<code>pip install -r requirements.txt</code><br><br>

3️⃣ **Set Up Google Gemini API Key**<br>
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).<br>
2. Set it as an environment variable:<br>
<code>export GEMINI_API_KEY="your-google-gemini-api-key"</code><br><br>

4️⃣ **Run the Chatbot API**<br>
<code>python chatbot.py</code><br>
The API will start at: <code>http://127.0.0.1:5000/</code><br><br>

📡 **Usage**<br>
Send a **POST request** to <code>/ask</code> with a JSON payload:<br>
<code>
{
  "question": "ما هي أسباب سقوط الدولة العباسية؟"
}
</code><br><br>

Example using Python:<br>
<code>
import requests

url = "http://127.0.0.1:5000/ask"
response = requests.post(url, json={"question": "ما هي أسباب سقوط الدولة العباسية؟"})
print(response.json())
</code><br><br>

📊 **Evaluation (FAISS Accuracy)**<br>
Run the FAISS evaluation script:<br>
<code>python evaluate_faiss.py</code><br>
This script computes:<br>
- **Precision@5** (How many retrieved answers are correct?)<br>
- **Recall@5** (Did we find all possible correct answers?)<br>
- **MRR (Mean Reciprocal Rank)** (How early was the correct answer retrieved?)<br><br>

📂 **Project Structure**<br>
<pre>
📁 arabic-history-chatbot
├── chatbot.py             # Main chatbot API
├── evaluate_faiss.py      # FAISS evaluation script
├── faiss_index.bin        # Prebuilt FAISS index
├── lesson_ids.json        # Lesson metadata for FAISS
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── data
    ├── hist.json          # Arabic history dataset
    ├── evaluation_dataset.json  # Evaluation questions/answers
</pre><br>

📌 **Future Improvements**<br>
🔹 Support for more Arabic dialects<br>
🔹 Interactive UI with React.js<br>
🔹 Expansion to other historical subjects<br><br>

📧 **Contact & Contributions**<br>
Feel free to contribute, open issues, or suggest improvements! 🚀
</p>
