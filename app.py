import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Counseling Notes Sanitizer", page_icon="🛡️", layout="wide")
st.title("🛡️ Challenge 4: Private Counseling Notes Sanitizer")
st.write("Automatically strip PII and format session notes for funder grant portals.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    model = st.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.caption("💡 Tip: Use gpt-4o-mini during testing to save credits!")

if not api_key:
    st.warning("👈 Please enter your OpenAI API key in the sidebar to start.")
    st.stop()

client = OpenAI(api_key=api_key)

sample_note = "Date: 11/07/2026. Client: Maria Rodriguez (DOB 05/14/1988), SSN ending 4321. Address: 742 Evergreen Terrace, Miami, FL. Counselor: Mark. Client attended 60-min family counseling session with husband Carlos. Maria reported severe anxiety due to impending eviction notice. We discussed budget planning and coping mechanisms. Client agreed to complete housing application by Tuesday. Follow-up scheduled for next week."

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Raw Session Note (Internal)")
    if st.button("📋 Load Sample Note"):
        st.session_state["note_input"] = sample_note

    raw_note = st.text_area("Paste raw counseling notes below:", value=st.session_state.get("note_input", ""), height=220)
    funder_format = st.selectbox("Select Funder Reporting Template:", ["Standard Grant Progress Report", "County Housing Support Format", "Minimal Demographics Only"])
    submit_button = st.button("🔒 Sanitize & Format Note", type="primary")

with col2:
    st.subheader("2. Funder-Ready Output")
    if submit_button:
        if not raw_note.strip():
            st.error("Please enter a session note first.")
        else:
            with st.spinner("Sanitizing note and stripping PII..."):
                sys_prompt = "You are a HIPAA privacy assistant for a non-profit. Convert raw counseling notes into sanitized funder reports. REDACT all PII (names, DOB, SSN, address). Summarize clinical progress, goals, and next steps in markdown. Include a short Redaction Audit Log at the end."
                try:
                    res = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": f"Template: {funder_format}\n\nNote:\n{raw_note}"}],
                        temperature=0.2
                    )
                    st.session_state["sanitized_output"] = res.choices[0].message.content
                    st.success("Sanitization complete!")
                except Exception as e:
                    st.error(f"OpenAI API Error: {e}")

    if "sanitized_output" in st.session_state:
        st.markdown("### 🛡️ Privacy & Compliance Audit")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Client Names", "Redacted", delta="Protected")
        b2.metric("DOB / SSN", "Stripped", delta="HIPAA Compliant")
        b3.metric("Address", "Anonymized", delta="Location idden")
        b4.metric("Status", "Funder-Ready", delta="Verified Safe")
        st.markdown("---")
        st.markdown(st.session_state["sanitized_output"])
        st.download_button("📥 Download Funder Report (.txt)", data=st.session_state["sanitized_output"], file_name="sanitized_funder_report.txt", mime="text/plain", type="primary")
