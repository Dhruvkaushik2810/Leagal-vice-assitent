const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const clearBtn = document.getElementById("clearBtn");
const statusEl = document.getElementById("status");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;

  if (role === "assistant") {
    speakText(text);
  }
}

function speakText(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = "en-IN";
  utter.rate = 1;
  window.speechSynthesis.speak(utter);
}

async function sendQuery(text) {
  if (!text.trim()) return;
  addMessage("user", text.trim());
  input.value = "";

  statusEl.textContent = "Thinking...";
  const response = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: text })
  });
  const data = await response.json();
  addMessage("assistant", data.answer || "No response.");
  statusEl.textContent = "Idle";
}

sendBtn.addEventListener("click", () => sendQuery(input.value));
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuery(input.value);
  }
});

clearBtn.addEventListener("click", () => {
  chat.innerHTML = "";
});

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const recognizer = new SpeechRecognition();
  recognizer.lang = "en-IN";
  recognizer.interimResults = false;
  recognizer.continuous = false;

  micBtn.addEventListener("click", () => {
    statusEl.textContent = "Listening...";
    recognizer.start();
  });

  recognizer.onresult = (event) => {
    const text = event.results[0][0].transcript;
    sendQuery(text);
  };

  recognizer.onerror = () => {
    statusEl.textContent = "Mic error";
  };

  recognizer.onend = () => {
    if (statusEl.textContent === "Listening...") {
      statusEl.textContent = "Idle";
    }
  };
} else {
  micBtn.disabled = true;
  micBtn.textContent = "Speech not supported";
}

addMessage("assistant", "Hello, I am your Legal Advisor. How can I assist you?");
