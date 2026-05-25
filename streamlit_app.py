import streamlit as st
import uuid
from app.ui.chat_view import render_chat
from app.ui.agent_view import render_agent_dashboard
from app.ui.decision_view import render_decision_board
from app.access_gate import is_approved, submit_access_request

st.set_page_config(
    page_title="Astra AI Copilot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 260px; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    div[data-testid="stSidebarNav"] { display: none; }
    .powered-bar {
        font-size: 0.72rem;
        color: #888;
        padding: 6px 0 12px 0;
        letter-spacing: 0.03em;
    }
</style>
""", unsafe_allow_html=True)

# Session management
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

session_id = st.session_state.session_id

# ── Access Gate session state ─────────────────────────────────────
if "prompt_count" not in st.session_state:
    st.session_state.prompt_count = 0
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False
if "show_gate" not in st.session_state:
    st.session_state.show_gate = False
if "request_submitted" not in st.session_state:
    st.session_state.request_submitted = False
if "email_checked" not in st.session_state:
    st.session_state.email_checked = False
# ─────────────────────────────────────────────────────────────────

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    view = st.radio(
        "Navigate",
        ["Copilot Chat", "Agent Executor", "Decision Board"],
        label_visibility="collapsed"
    )
    st.divider()

    # ── Returning user email check (in sidebar, non-intrusive) ────
    if not st.session_state.access_granted:
        st.markdown("**Already have access?**")
        returning_email = st.text_input(
            "Enter your email",
            key="returning_email_input",
            placeholder="you@company.com",
            label_visibility="collapsed"
        )
        if st.button("Check Access", use_container_width=True):
            if returning_email.strip():
                if is_approved(returning_email.strip()):
                    st.session_state.user_email = returning_email.strip()
                    st.session_state.access_granted = True
                    st.session_state.email_checked = True
                    st.rerun()
                else:
                    st.error("Not approved yet.")
            else:
                st.error("Enter your email first.")
        st.divider()
    else:
        st.success(f"✅ Access granted")
        st.caption(f"{st.session_state.user_email}")
        if st.button("Sign out", use_container_width=True):
            st.session_state.access_granted = False
            st.session_state.user_email = None
            st.session_state.prompt_count = 0
            st.rerun()
        st.divider()
# ─────────────────────────────────────────────────────────────────

# Powered by bar
st.markdown("""
<div class="powered-bar">
✦ Gemini 1.5 Flash &nbsp;·&nbsp; Groq Llama 3 &nbsp;·&nbsp; LangChain ReAct &nbsp;·&nbsp; Supabase &nbsp;·&nbsp; Tavily Search
</div>
""", unsafe_allow_html=True)

# ── Access Gate Modal ─────────────────────────────────────────────
if st.session_state.show_gate and not st.session_state.access_granted:
    st.warning("You've used your free prompt. Request access to keep going.")

    if st.session_state.request_submitted:
        email_display = st.session_state.user_email or "your email"
        st.success(f"✅ Request submitted! You'll hear back at {email_display}")
        st.info("Once approved, enter your email in the sidebar to get full access.")
        st.stop()

    with st.form("access_request_form"):
        st.markdown("### 🔐 Request Full Access to Astra AI")
        st.caption("Takes 30 seconds. Karamjeet reviews and approves manually.")

        name     = st.text_input("Name *")
        email    = st.text_input("Work Email *")
        company  = st.text_input("Company *")
        linkedin = st.text_input("LinkedIn URL (optional)")
        reason   = st.text_area("Why do you need access? (optional)", height=80)

        submitted = st.form_submit_button("Request Access →", use_container_width=True)

        if submitted:
            if not name.strip() or not email.strip() or not company.strip():
                st.error("Name, Email and Company are required.")
            else:
                submit_access_request(name.strip(), email.strip(), company.strip(), linkedin.strip(), reason.strip())
                st.session_state.user_email = email.strip()
                st.session_state.request_submitted = True
                st.rerun()

    st.stop()
# ─────────────────────────────────────────────────────────────────

# Route to selected view
if "Copilot Chat" in view:
    render_chat(session_id)
elif "Agent Executor" in view:
    render_agent_dashboard(session_id)
elif "Decision Board" in view:
    render_decision_board(session_id)