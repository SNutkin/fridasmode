import streamlit as st

st.image("fridasmode.png", use_container_width=True)

# Display README.md or any markdown file
with open("README.md", "r", encoding="utf-8") as f:
    md_content = f.read()
st.markdown(md_content, unsafe_allow_html=True)