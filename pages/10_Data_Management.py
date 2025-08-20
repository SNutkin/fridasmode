import streamlit as st
import os

st.title("⬇️⬆️ Download & Upload Data Files")

DATA_FILES = [
    "teams.json",
    "matchups.json",
    "bets.json",
    "hero_costs.json"
]

st.header("Download JSON Files")
for filename in DATA_FILES:
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            st.download_button(
                label=f"Download {filename}",
                data=f,
                file_name=filename,
                mime="application/json"
            )
    else:
        st.warning(f"{filename} not found.")

st.divider()
st.header("Upload JSON Files (will overwrite existing)")

for filename in DATA_FILES:
    uploaded = st.file_uploader(f"Upload {filename}", type="json", key=filename)
    if uploaded is not None:
        with open(filename, "wb") as f:
            f.write(uploaded.read())
        st.success(f"{filename} uploaded successfully!")