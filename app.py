import streamlit as st
import tempfile

from docx_processing.docx_region_extractor import split_docx_to_regions
from pipeline import run_pipeline, process_replies

st.set_page_config(
    page_title="Freight Mail Automation",
    layout="wide"
)

st.title("Freight Market Automation")

st.write("Upload weekly DOCX report and send freight market updates.")

uploaded_file = st.file_uploader(
    "Upload Weekly DOCX",
    type=["docx"]
)

if uploaded_file:

    temp = tempfile.NamedTemporaryFile(delete=False)

    temp.write(uploaded_file.read())

    temp_path = temp.name

    st.success("File uploaded successfully")

    regions = split_docx_to_regions(temp_path)

    st.subheader("Detected Regions")

    for r in regions.keys():
        st.write("✓", r)

    st.subheader("Preview Email")

    region_choice = st.selectbox(
        "Select Region",
        list(regions.keys())
    )

    preview_html = regions[region_choice]

    preview_html = f"""
    <div style="background-color:white;color:black;padding:20px;font-family:Arial;">
    {preview_html}
    </div>
    """

    st.components.v1.html(
        preview_html,
        height=600,
        scrolling=True
    )

    st.divider()

    if st.button("Send Emails"):

        with st.spinner("Sending emails..."):

            logs = run_pipeline(temp_path)

        st.success("Emails sent")

        st.subheader("Logs")

        for l in logs:
            st.write(l)

    st.divider()

    st.subheader("Reply Monitor")

    if st.button("Scan Replies"):

        with st.spinner("Checking inbox..."):

            reply_logs = process_replies()

        for l in reply_logs:
            st.write(l)