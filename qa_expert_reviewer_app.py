import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Discharge Summary QA Viewer", layout="centered")

SAVE_FILE = "saved_expert_responses.xlsx"

if 'saved_responses' not in st.session_state:
    if os.path.exists(SAVE_FILE):
        st.session_state.saved_responses = pd.read_excel(SAVE_FILE).to_dict(orient="records")
    else:
        st.session_state.saved_responses = []

def generate_llm_response_from_prompt(prompt, discharge_summary, question):
    """
    Placeholder function to simulate an LLM-generated response.

    In a production environment, replace this with a real call to an LLM provider, passing the `prompt`, `discharge_summary`,
    and `question` to generate a tailored response.

    Returns a dummy string for demonstration purposes only.
    """
    answer = "The LLM-generated answer would be here."
    return f"[LLM Response to Prompt: {answer}]\n\n" 

st.markdown(
    """
    <div style="background-color:#fff3cd;padding:10px;border-radius:5px;border:1px solid #ffeeba">
        <strong>⚠️ Warning:</strong> This app is running locally. Do not upload sensitive data if you are not sure of your environment or if this app is deployed online.
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("🩺 Discharge Summary QA Viewer")

# Step 1: Select mode
mode = st.radio("Select file mode", (
    "Includes LLM-generated Response", 
    "Needs LLM to generate Response"
))

# Step 2: Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if mode == "Includes LLM-generated Response":
        required_cols = {"Note Id", "Question", "Discharge Summary", "LLM-generated Response"}
        if not required_cols.issubset(df.columns):
            st.error("❌ The file must contain: 'Note Id', 'Question', 'Discharge Summary', and 'LLM-generated Response'.")
            st.stop()
    else:
        required_cols = {"Note Id", "Question", "Discharge Summary", "Prompt"}
        if not required_cols.issubset(df.columns):
            st.error("❌ The file must contain: 'Note Id', 'Question', 'Discharge Summary', and 'Prompt'.")
            st.stop()

        # Ignore any pre-existing "LLM-generated Response" column
        if "LLM-generated Response" in df.columns:
            df = df.drop(columns=["LLM-generated Response"])

        # Regenerate the LLM-generated Response from prompt
        df["LLM-generated Response"] = df.apply(
            lambda row: generate_llm_response_from_prompt(row["Prompt"], row["Discharge Summary"], row["Question"]),
            axis=1
        )

    reviewed_note_ids = {r["Note Id"] for r in st.session_state.saved_responses}
    remaining_note_ids = [nid for nid in df["Note Id"] if nid not in reviewed_note_ids]

    if not remaining_note_ids:
        st.success("🎉 All notes have been reviewed!")
    else:
        selected_note_id = st.selectbox("Select Note Id", remaining_note_ids)
        row_index = df.index[df["Note Id"] == selected_note_id].tolist()[0]

        st.subheader("Question")
        st.markdown(f"<div style='font-weight:bold; font-size:16px'>{df.at[row_index, 'Question']}</div>", unsafe_allow_html=True)

        st.subheader("📄 Discharge Summary")
        st.markdown(
            f"""<div style='padding:15px; background-color:#f8f9fa; border:1px solid #ddd; border-radius:5px;
                 height:400px; overflow-y:auto; white-space:pre-wrap; font-family:monospace; font-size:15px;'>
                 {df.at[row_index, 'Discharge Summary']}</div>""",
            unsafe_allow_html=True
        )

        st.subheader("LLM-generated Response")
        edited_response = st.text_area("Edit or review the response below:", value=str(df.at[row_index, "LLM-generated Response"]), height=300)

        if 'approved_responses' not in st.session_state:
            st.session_state.approved_responses = {}

        if st.button("✅ Approve Response"):
            st.session_state.approved_responses[selected_note_id] = edited_response

        if selected_note_id in st.session_state.approved_responses:
            st.subheader("🧑‍⚕️ Expert's Response")
            st.markdown(
                f"""<div style='padding:15px; background-color:#e9f7ef; border:1px solid #c3e6cb; border-radius:5px;
                     white-space:pre-wrap; font-family:monospace; font-size:15px;'>
                     {st.session_state.approved_responses[selected_note_id]}</div>""",
                unsafe_allow_html=True
            )

            if st.button("💾 Save Expert's Response"):
                record = {
                    "Note Id": df.at[row_index, "Note Id"],
                    "Question": df.at[row_index, "Question"],
                    "Discharge Summary": df.at[row_index, "Discharge Summary"],
                    "Expert's Response": st.session_state.approved_responses[selected_note_id]
                }

                st.session_state.saved_responses.append(record)
                pd.DataFrame(st.session_state.saved_responses).to_excel(SAVE_FILE, index=False)
                st.success("✅ Expert response saved.")

    if st.session_state.saved_responses:
        st.markdown("---")
        st.subheader("⬇️ Download All Saved Expert Responses (Optional)")

        result_df = pd.DataFrame(st.session_state.saved_responses)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False, sheet_name="ExpertResponses")
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name="expert_responses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
