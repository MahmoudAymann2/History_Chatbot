/* === configuration === */
const API_ROOT = "https://f3c8-102-185-183-92.ngrok-free.app"; // <- change when backend URL changes

/* === DOM handles === */
const chat = document.getElementById("chat-container");
const form = document.getElementById("input-form");
const input = document.getElementById("question-input");

/* === helpers === */
const scrollToBottom = () => chat.scrollTo({ top: chat.scrollHeight, behavior: "smooth" });

const addMsg = (sender, text) => {
  const div = document.createElement("div");
  div.className = `bubble ${sender}`;
  div.textContent = text;
  chat.appendChild(div);
  scrollToBottom();
};

/* initial greeting */
addMsg("bot", "مرحبًا! كيف يمكنني مساعدتك في مادة التاريخ؟ يمكنك طرح أي سؤال وسأبذل قصارى جهدي للإجابة عليه.");

/* === form handler === */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  addMsg("user", q);
  input.value = "";
  input.disabled = true;

  /* show placeholder while waiting */
  const placeholder = document.createElement("div");
  placeholder.className = "bubble bot";
  placeholder.textContent = "… جارٍ التفكير";
  chat.appendChild(placeholder);
  scrollToBottom();

  try {
    const res = await fetch(`${API_ROOT}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    placeholder.textContent = data.answer || "عذراً، لم أتلقَّ رداً.";
  } catch (err) {
    placeholder.textContent = "حدث خطأ أثناء الاتصال بالخادم.";
  } finally {
    input.disabled = false;
    input.focus();
    scrollToBottom();
  }
});
/*
// === Dynamic Quotes Overlay for Slideshow ===
const slideQuotes = [
  // img1: (no overlay)
  [],
  // img2: Saad Zaghloul (4 quotes)
  [
    '"الحرية لا تُوهب، بل تُنتزع" - سعد زغلول',
    '"إن الأمة التي لا تحمي نفسها لا يستحق أن يُحترم استقلالها" - سعد زغلول',
    '"اتحادكم هو سر قوتكم" - سعد زغلول',
    '"الحق فوق القوة، والأمة فوق الحكومة" - سعد زغلول'
  ],
  // img3: Egypt (4 quotes)
  [
    'مصر هبة النيل والمصريين.',
    'تحيا مصر عبر العصور.',
    'الأهرامات شاهد على عظمة المصريين.',
    'مصر أرض الحضارة والتاريخ.'
  ],
  // img4: Mohamed Ali (4 quotes)
  [
    '💡 هل تعلم؟ أن محمد علي قام ببناء جيش حديث لأول مرة في مصر.',
    'محمد علي: مؤسس مصر الحديثة.',
    'من أقوال محمد علي: "العلم أساس التقدم".',
    'محمد علي: قائد النهضة المصرية.'
  ],
  // img5: Egypt (4 quotes)
  [
    'مصر أرض الحضارة والتاريخ.',
    'الأهرامات شاهد على عظمة المصريين.',
    'مصر قلب العالم العربي.',
    'مصر بلد الأمن والأمان.'
  ],
  // img6: Mohamed Ali (4 quotes)
  [
    'محمد علي: قائد النهضة المصرية.',
    'من أقوال محمد علي: "العلم أساس التقدم".',
    'محمد علي: باني مصر الحديثة.',
    'محمد علي: رمز الإصلاح والتطوير.'
  ]
];
*/
const overlayContainer = document.getElementById('dynamic-overlay') || (() => {
  const el = document.createElement('div');
  el.id = 'dynamic-overlay';
  document.body.appendChild(el);
  return el;
})();

let lastActive = -1;

function showQuotesForSlide(slideIdx) {
  overlayContainer.innerHTML = '';
  const quotes = slideQuotes[slideIdx] || [];
  if (quotes.length === 0) return;
  // Pick up to 3 quotes randomly for the left side only
  const shuffled = quotes.slice().sort(() => Math.random() - 0.5);
  const leftQuotes = shuffled.slice(0, 3);
  // Use fixed vertical slots for up to 3 quotes
  const slots = [18, 42, 66]; // vh positions for 3 quotes
  leftQuotes.forEach((quote, i) => {
    const div = document.createElement('div');
    div.className = 'card-overlay';
    div.textContent = quote;
    div.style.left = '2vw';
    div.style.right = '';
    div.style.top = slots[i] + 'vh';
    div.style.maxWidth = '16vw';
    div.style.width = '16vw';
    div.style.pointerEvents = 'none';
    overlayContainer.appendChild(div);
  });
}

const slideWrappers = document.querySelectorAll('.slide-wrapper');
setInterval(() => {
  let active = -1;
  slideWrappers.forEach((sw, idx) => {
    const style = window.getComputedStyle(sw);
    if (style.opacity === '1') active = idx;
  });
  if (active !== lastActive && active !== -1) {
    showQuotesForSlide(active);
    lastActive = active;
  }
}, 500);

// Change send button to arrow icon
const sendBtn = document.querySelector('#input-form button');
if (sendBtn) {
  sendBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
} 