import streamlit as st
import requests

st.set_page_config(page_title="AI Mental Health Assistant", page_icon="🧠", layout="centered")

st.sidebar.markdown("### Navigate")
section = st.sidebar.radio("", ["🧠 Mental Health Assistant", "📊 Summary Dashboard"])

if section == "🧠 Mental Health Assistant":
    st.title("🧠 AI Mental Health Assistant")

    user_input = st.text_input("💬 How are you feeling today?", placeholder="I am feeling better than yesterday.")

    st.markdown("### 📋 PHQ-9 Questionnaire")
    questions = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling/staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself or a failure?",
        "Trouble concentrating?",
        "Moving/speaking slowly or restlessness?",
        "Thoughts of self-harm or feeling better off dead?"
    ]

    slider_values, text_responses = [], []
    for i, q in enumerate(questions):
        val = st.slider(f"{q}", 0, 3, 0, key=f"slider_{i}")
        text = st.text_area(f"✏️ Share more: {i+1}. {q}", key=f"text_{i}")
        slider_values.append(val)
        text_responses.append(text)

    journal_reflection = st.text_area("📝 Your Reflection", height=100, placeholder="Write your thoughts here...")

    if st.button("🔍 Analyze"):
        filled_responses = [text.strip() for text in text_responses if text.strip() != ""]
        if not user_input.strip() and not filled_responses:
            st.warning("⚠️ Please share how you're feeling or answer at least one question.")
        else:
            payload = {
                "user_statement": user_input,
                "phq9_responses": filled_responses,
                "journal_text": journal_reflection
            }

            try:
                response = requests.post("http://127.0.0.1:8000/analyze", json=payload)
                result = response.json()

                st.success("✅ Mental Health Summary")
                st.markdown(f"**PHQ-9 Severity:** `{result['phq9_severity']}`")
                st.markdown(f"😶‍🌫️ **Emotions Detected:** {', '.join(result['emotions'])}")
                st.markdown(f"💬 **Summary:** {result['summary']}")

                st.markdown("🧘 **Therapy Suggestion:**")
                st.info(result["activity"])

                st.markdown("📖 **Journaling Prompt:**")
                st.code(result["prompt"])

                st.success("📓 Your entry was saved successfully.")
            except Exception as e:
                st.error("Something went wrong. Please check the backend is running.")
