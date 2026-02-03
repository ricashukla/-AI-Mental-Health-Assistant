const questions = [
  "Little interest or pleasure in doing things?",
  "Feeling down, depressed, or hopeless?",
  "Trouble falling/staying asleep, or sleeping too much?",
  "Feeling tired or having little energy?",
  "Poor appetite or overeating?",
  "Feeling bad about yourself or a failure?",
  "Trouble concentrating?",
  "Moving/speaking slowly or restlessness?",
  "Thoughts of self-harm or feeling better off dead?"
];

const questionContainer = document.getElementById("phqQuestions");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

const buildQuestionRow = (question, index) => {
  const row = document.createElement("div");
  row.className = "question";

  const label = document.createElement("label");
  label.textContent = `${index + 1}. ${question}`;
  label.setAttribute("for", `phq-text-${index}`);

  const controls = document.createElement("div");
  controls.className = "question-controls";

  const select = document.createElement("select");
  select.id = `phq-score-${index}`;
  select.innerHTML = `
    <option value="0">0 - Not at all</option>
    <option value="1">1 - Several days</option>
    <option value="2">2 - More than half the days</option>
    <option value="3">3 - Nearly every day</option>
  `;

  const textarea = document.createElement("textarea");
  textarea.id = `phq-text-${index}`;
  textarea.rows = 2;
  textarea.placeholder = "Share more (optional)";

  controls.append(select, textarea);
  row.append(label, controls);
  return row;
};

questions.forEach((question, index) => {
  questionContainer.append(buildQuestionRow(question, index));
});

const setStatus = (message, tone = "info") => {
  statusEl.textContent = message;
  statusEl.className = `status ${tone}`;
};

const collectResponses = () => {
  const responses = [];
  questions.forEach((_, index) => {
    const text = document.getElementById(`phq-text-${index}`).value.trim();
    if (text) {
      responses.push(text);
    }
  });
  return responses;
};

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const userStatement = document.getElementById("userStatement").value.trim();
  const journalText = document.getElementById("journalText").value.trim();
  const phqResponses = collectResponses();

  if (!userStatement && phqResponses.length === 0) {
    setStatus("Please share how you're feeling or answer at least one question.", "warning");
    return;
  }

  setStatus("Analyzing your check-in...", "info");

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_statement: userStatement,
        phq9_responses: phqResponses,
        journal_text: journalText
      })
    });

    if (!response.ok) {
      throw new Error("Failed to analyze response.");
    }

    const result = await response.json();

    document.getElementById("severity").textContent = result.phq9_severity ?? "Unknown";
    document.getElementById("emotions").textContent = (result.emotions || []).join(", ");
    document.getElementById("summary").textContent = result.summary ?? "";
    document.getElementById("activity").textContent = result.activity ?? "";
    document.getElementById("prompt").textContent = result.prompt ?? "";

    resultsEl.classList.remove("hidden");
    setStatus("Check-in complete.", "success");
  } catch (error) {
    console.error(error);
    setStatus("Something went wrong. Please make sure the backend is running.", "error");
  }
});
