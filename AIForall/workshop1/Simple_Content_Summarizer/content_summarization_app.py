import streamlit as st
import content_summarization_lib as glib

st.set_page_config(page_title="Content Summarizer")
st.title("Content Summarizer")

input_text = st.text_area("Paste your content here to summarize", height=200)

summarize_button = st.button("Summarize", type="primary")

if summarize_button:
    if input_text.strip():
        st.subheader("Summary")
        
        with st.spinner("Generating summary..."):
            response_content = glib.get_summary(input_text)
            st.write(response_content)
    else:
        st.warning("Please enter some content to summarize.")
