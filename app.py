import streamlit as st
import json
from pypdf import PdfReader

from utils.auth import login, register
from utils.database import init_db, save_chat, save_note, get_notes
from utils.ai_engine import ask_ai

# ================= INIT =================
init_db()

st.set_page_config(
    page_title="AI Study Buddy",
    layout="wide",
    page_icon="🧠"
)

# ================= STATE =================
def init_state():
    defaults = {
        "logged_in": False,
        "user_email": "",
        "page": "home",
        "messages": [],
        "quiz": None,
        "quiz_answers": {},
        "quiz_submitted": False
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# safe page init
st.session_state.page = st.session_state.get("page", "home")

# ================= CSS =================
st.markdown("""
<style>

.stApp {
    background: #0b0f17;
    color: white;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0e1525;
}

section[data-testid="stSidebar"] button {
    width: 100%;
    border-radius: 10px;
    margin-bottom: 6px;
    background: #111a2e;
    color: white;
    border: 1px solid #1f2a44;
}

/* CHAT */
.user {
    background: linear-gradient(135deg,#4f46e5,#9333ea);
    padding: 10px;
    border-radius: 12px;
    margin: 6px 0;
    max-width: 80%;
    margin-left: auto;
}

.ai {
    background: #111827;
    padding: 10px;
    border-radius: 12px;
    margin: 6px 0;
    max-width: 80%;
    border: 1px solid #1f2a44;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding: 12px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.title("🧠 AI Study Buddy")

        mode = st.radio("Mode", ["Login", "Signup"], horizontal=True)

        with st.form("auth_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            submit = st.form_submit_button("Continue")

            if submit:

                if mode == "Login":
                    if login(email, password):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

                else:
                    ok, msg = register(email, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error(msg)

    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.title("🧠 Study Buddy")

    pages = {
        "🏠 Home": "home",
        "💬 Chat": "chat",
        "📚 Notes": "notes",
        "🧪 Quiz": "quiz",
        "🃏 Flashcards": "flashcards",
        "📊 Analytics": "analytics",
        "📄 PDF Summary": "pdf_summary"
    }

    for label, value in pages.items():
        if st.button(label):
            st.session_state.page = value

    st.markdown("---")
    st.write(f"👤 {st.session_state.user_email}")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.session_state.quiz = None
        st.rerun()

page = st.session_state.page

# ================= HOME =================
if page == "home":

    st.title("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔥 Streak", "7 days")
    col2.metric("📝 Notes", "--")
    col3.metric("💬 Chats", len(st.session_state.messages))
    col4.metric("🧪 Quiz", "--")

    st.info("Focus: DSA + OS + Mini Projects + Daily Practice")

# ================= CHAT =================
elif page == "chat":

    st.title("💬 AI Chat")

    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div class='user'>👤 {m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai'>🤖 {m['content']}</div>", unsafe_allow_html=True)

    msg = st.chat_input("Type your message...")

    if msg:
        st.session_state.messages.append({"role": "user", "content": msg})

        with st.spinner("Thinking..."):
            answer = ask_ai(msg)

        if answer:
            st.session_state.messages.append({"role": "assistant", "content": answer})

        save_chat(st.session_state.user_email, msg, answer)
        st.rerun()

# ================= NOTES =================
elif page == "notes":

    st.title("📚 Notes")

    note = st.text_area("Write note")

    if st.button("Save"):
        if note.strip():
            save_note(st.session_state.user_email, note)
            st.success("Saved!")
        else:
            st.warning("Empty note")

    st.subheader("Your Notes")

    notes = get_notes(st.session_state.user_email)

    if notes:
        for n in notes:
            st.markdown(f"<div class='card'>📝 {n[0]}</div>", unsafe_allow_html=True)
    else:
        st.info("No notes yet")

# ================= QUIZ =================
elif page == "quiz":

    st.title("🧪 Quiz Generator")

    topic = st.text_input("Enter topic")

    if st.button("Generate Quiz"):

        prompt = f"""
Create 3 MCQs on {topic}.
Return ONLY JSON:
[
  {{
    "question": "",
    "options": ["A","B","C","D"],
    "answer": "A"
  }}
]
"""

        quiz_data = ask_ai(prompt)

        try:
            st.session_state.quiz = json.loads(quiz_data)
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
        except:
            st.error("Invalid AI response")

    if st.session_state.quiz is not None:

        for i, q in enumerate(st.session_state.quiz):

            st.write(q["question"])

            st.session_state.quiz_answers[i] = st.radio(
                "Answer",
                q["options"],
                key=f"q_{i}",
                disabled=st.session_state.quiz_submitted
            )

        if not st.session_state.quiz_submitted:

            if st.button("Submit"):
                st.session_state.quiz_submitted = True
                st.rerun()

        else:

            score = 0

            for i, q in enumerate(st.session_state.quiz):
                if st.session_state.quiz_answers[i] == q["answer"]:
                    score += 1
                    st.success(q["question"])
                else:
                    st.error(f"{q['question']} (Ans: {q['answer']})")

            st.success(f"Score: {score}/{len(st.session_state.quiz)}")

            if st.button("Reset"):
                st.session_state.quiz = None
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()

# ================= FLASHCARDS =================
elif page == "flashcards":

    st.title("🃏 Flashcards")

    topic = st.text_input("Topic")

    if st.button("Generate"):
        res = ask_ai(f"Create flashcards for {topic}")
        st.write(res)

# ================= ANALYTICS =================
elif page == "analytics":

    st.title("📊 Analytics")

    st.metric("Progress", "72%")
    st.progress(0.72)

# ================= PDF SUMMARY =================
elif page == "pdf_summary":

    st.title("📄 PDF Summary")

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:

        reader = PdfReader(file)
        text = ""

        for p in reader.pages:
            text += p.extract_text() or ""

        if not text.strip():
            st.error("No readable text found")
        else:
            st.success("PDF loaded")

            if st.button("Generate Summary"):

                with st.spinner("AI reading PDF..."):

                    summary = ask_ai(f"Summarize clearly:\n{text[:8000]}")

                st.subheader("Summary")
                st.write(summary)