# This source file is part of the ARPA-H CARE LLM project
#
# SPDX-FileCopyrightText: 2025 Stanford University and the project authors (see AUTHORS.md)
#
# SPDX-License-Identifier: MIT
#
# Author: Vicky Bikia, PhD, Stanford University (bikia@stanford.edu)
#
  
# Standard library imports
import pandas as pd
from io import BytesIO
import os

# Third-party imports
import streamlit as st

# Local application imports
from columns_interface import DischargeSummaryExcelFileColumns


# Choose the column mapping
col = DischargeSummaryExcelFileColumns()

st.set_page_config(page_title="Medical QA Reviewer", layout="centered")

SAVE_FILE = "saved_expert_responses.xlsx"

if "saved_responses" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        st.session_state.saved_responses = pd.read_excel(SAVE_FILE).to_dict(
            orient="records"
        )
    else:
        st.session_state.saved_responses = []


def generate_llm_response_from_prompt(prompt, discharge_summFFary, question):
    """
    Placeholder function to simulate an LLM-generated response.

    In a production environment, replace this with a real call to an LLM provider, passing the `prompt`, `discharge_summaFFry`,
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

mode = st.radio(
    "Select file mode",
    ("Includes LLM-generated Response", "Needs LLM to generate Response"),
)

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if mode == "Includes LLM-generated Response":
        required_cols = {
            col.NOTE_ID,
            col.QUESTION,
            col.CLINICAL_TEXT,
            col.LLM_GENERATED_RESPONSE,
        }

        if not required_cols.issubset(df.columns):
            st.error(
                f"❌ The file must contain: {col.NOTE_ID}, {col.QUESTION}, {col.CLINICAL_TEXT}, and {col.LLM_GENERATED_RESPONSE}."
            )
            st.stop()
    else:
        required_cols = {
            col.NOTE_ID,
            col.QUESTION,
            col.CLINICAL_TEXT,
            col.PROMPT,
        }
        if not required_cols.issubset(df.columns):
            st.error(
                f"❌ The file must contain: {col.NOTE_ID}, {col.QUESTION}, {col.CLINICAL_TEXT}, and {col.PROMPT}."
            )
            st.stop()

        if col.LLM_GENERATED_RESPONSE in df.columns:
            df = df.drop(columns=[col.LLM_GENERATED_RESPONSE])

        df[col.LLM_GENERATED_RESPONSE] = df.apply(
            lambda row: generate_llm_response_from_prompt(
                row[col.PROMPT],
                row[col.CLINICAL_TEXT],
                row[col.QUESTION],
            ),
            axis=1,
        )

    reviewed_note_ids = {
        r[col.NOTE_ID] for r in st.session_state.saved_responses
    }
    remaining_note_ids = [
        nid for nid in df[col.NOTE_ID] if nid not in reviewed_note_ids
    ]

    if not remaining_note_ids:
        st.success("🎉 All notes have been reviewed!")
    else:
        selected_note_id = st.selectbox(
            f"Select {col.NOTE_ID}", remaining_note_ids
        )
        row_index = df.index[df[col.NOTE_ID] == selected_note_id].tolist()[
            0
        ]

        st.subheader(col.QUESTION)
        st.markdown(
            f"<div style='font-weight:bold; font-size:16px'>{df.at[row_index, col.QUESTION]}</div>",
            unsafe_allow_html=True,
        )

        st.subheader(f"📄 {col.CLINICAL_TEXT}")
        st.markdown(
            f"""<div style='padding:15px; background-color:#f8f9fa; border:1px solid #ddd; border-radius:5px;
                 height:400px; overflow-y:auto; white-space:pre-wrap; font-family:monospace; font-size:15px;'>
                 {df.at[row_index, 'Discharge Summary']}</div>""",
            unsafe_allow_html=True,
        )

        st.subheader(col.LLM_GENERATED_RESPONSE)
        edited_response = st.text_area(
            "Edit or review the response below:",
            value=str(df.at[row_index, col.LLM_GENERATED_RESPONSE]),
            height=300,
        )

        if "approved_responses" not in st.session_state:
            st.session_state.approved_responses = {}

        if st.button("✅ Approve Response"):
            st.session_state.approved_responses[selected_note_id] = edited_response

        if selected_note_id in st.session_state.approved_responses:
            st.subheader("🧑‍⚕️ Expert's Response")
            st.markdown(
                f"""<div style='padding:15px; background-color:#e9f7ef; border:1px solid #c3e6cb; border-radius:5px;
                     white-space:pre-wrap; font-family:monospace; font-size:15px;'>
                     {st.session_state.approved_responses[selected_note_id]}</div>""",
                unsafe_allow_html=True,
            )

            if st.button("💾 Save Expert's Response"):
                record = {
                    col.NOTE_ID: df.at[
                        row_index, col.NOTE_ID
                    ],
                    col.QUESTION: df.at[
                        row_index, col.QUESTION
                    ],
                    col.CLINICAL_TEXT: df.at[
                        row_index, col.CLINICAL_TEXT
                    ],
                    col.EXPERT_RESPONSE: st.session_state.approved_responses[
                        selected_note_id
                    ],
                }

                st.session_state.saved_responses.append(record)
                pd.DataFrame(st.session_state.saved_responses).to_excel(
                    SAVE_FILE, index=False
                )
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
