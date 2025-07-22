<p align="left">

<h1>📜 Arabic History Chatbot with FAISS + Gemini AI</h1>

<h2>🚀 Description</h2>
<p>
A smart chatbot for Arabic history using <strong>Retrieval-Augmented Generation (RAG)</strong> with <strong>FAISS</strong> for efficient semantic search and <strong>Google Gemini AI</strong> for contextual Arabic answer generation.
</p>

<h2>✅ Features</h2>
<ul>
  <li>✅ <strong>Embeds historical Arabic content using SentenceTransformers</strong></li>
  <li>✅ <strong>FAISS-based semantic search for fast, relevant lookups</strong></li>
  <li>✅ <strong>Gemini 2.5 API for generating Arabic responses</strong></li>
  <li>✅ <strong>Flask API with real-time interaction and frontend support</strong></li>
  <li>✅ <strong>Evaluation metrics: Precision@5, Recall@5, and Mean Reciprocal Rank (MRR)</strong></li>
</ul>

<h2>🛠️ Installation & Setup</h2>

<ol>
  <li><strong>Clone the Repository</strong><br>
    <code>git clone https://github.com/YOUR_USERNAME/arabic-history-chatbot.git</code><br>
    <code>cd arabic-history-chatbot</code>
  </li>
  <br>
  <li><strong>Create Virtual Environment (optional but recommended)</strong><br>
    <code>python -m venv .venv</code><br>
    <code>.venv\Scripts\activate</code> (on Windows)<br>
    <code>source .venv/bin/activate</code> (on macOS/Linux)
  </li>
  <br>
  <li><strong>Install Dependencies</strong><br>
    <code>pip install -r requirements.txt</code>
  </li>
  <br>
  <li><strong>Set Up Google Gemini API Key</strong><br>
    1. Get your Gemini API key from <a href="https://aistudio.google.com/">Google AI Studio</a>.<br>
    2. Set it as an environment variable:<br>
    <code>export GEMINI_API_KEY="your-google-gemini-api-key"</code> (Linux/macOS)<br>
    <code>set GEMINI_API_KEY="your-google-gemini-api-key"</code> (Windows)
  </li>
  <br>
  <li><strong>Run the Chatbot API</strong><br>
    <code>python app.py</code><br>
    Access it at: <code>http://127.0.0.1:5000/</code>
  </li>
</ol>

<h2>📡 Usage</h2>
<p>Send a <strong>POST request</strong> to <code>/ask</code> with a JSON payload:</p>

<pre>
{
  "question": "ما هي أسباب سقوط الدولة العباسية؟"
}
</pre>

<p><strong>Example using Python:</strong></p>

<pre><code>
import requests

url = "http://127.0.0.1:5000/ask"
response = requests.post(url, json={"question": "ما هي أسباب سقوط الدولة العباسية؟"})
print(response.json())
</code></pre>

<p>Or access the <strong>browser chat interface</strong> at:<br>
<code>http://127.0.0.1:5000/</code></p>

<h2>📊 Evaluation (FAISS Accuracy)</h2>
<p>Run the evaluation script:</p>
<code>python Evaluation_Test.py</code><br><br>
<p>This computes:</p>
<ul>
  <li><strong>Precision@5</strong> – How many retrieved answers are correct?</li>
  <li><strong>Recall@5</strong> – Did we find all possible correct answers?</li>
  <li><strong>MRR</strong> – Mean Reciprocal Rank of the correct answer</li>
</ul>

<h2>📂 Project Structure</h2>
<pre>
arabic-history-chatbot/
├── app.py                  # Main Flask API serving the chatbot
├── doc2text.py             # OCR + preprocessing script for Arabic PDFs
├── Evaluation_Test.py      # Evaluation script for FAISS performance
├── faiss_index.bin         # Prebuilt FAISS index with embeddings
├── hist.json               # Cleaned Arabic history dataset
├── requirements.txt        # Python dependencies
├── static/                 # Frontend assets (JS, CSS, images)
│   ├── script.js
│   ├── style.css
│   └── ...
├── templates/
│   └── index.html          # Chat interface (HTML frontend)
└── .venv/                  # (optional) Python virtual environment
</pre>

<h2>📌 Future Improvements</h2>
<ul>
  <li>🔹 Support for more Arabic dialects and curriculum variations</li>
  <li>🔹 Upgrade to a React-based UI for richer interaction</li>
  <li>🔹 Add support for additional subjects like Biology and Geography</li>
</ul>

<h2>📧 Contact & Contributions</h2>
<p>
Feel free to fork this repo, open issues, or suggest improvements!  
<br>Pull requests are welcome 🚀
</p>

</p>
