import argparse
import os
import pandas as pd
import streamlit as st

from utils import save_csv, convert_dat_to_csv, compute_value_info, random_sample_df, convert_opt_to_csv


###

###

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

@st.cache_data
def prep_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

### ------------------------ ###
# Streamlit App
### ------------------------ ###

st.title("Load File Profiler")

uploaded_file = st.file_uploader("Upload a DAT or CSV file", type=["dat", "csv"])

if uploaded_file:
    opt_file = st.file_uploader("Upload an optional OPT file", type=["opt"])
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension == ".dat":
        load_file_df = convert_dat_to_csv(uploaded_file)
    elif file_extension == ".csv":
        load_file_df = pd.read_csv(uploaded_file, dtype=str)
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.button('Run data profile.', on_click=click_button)
    if st.session_state.clicked:
        st.success("File loaded successfully!")
        st.subheader("Random Sample")
        if opt_file:
            opt_df = convert_opt_to_csv
        try:
            sampled_df = random_sample_df(load_file_df)
            st.dataframe(sampled_df)
        except ValueError as e:
            st.error(f"Error: {e}")

        # Profile data
        profile = compute_value_info(load_file_df)
        st.subheader("Data Profile")
        st.dataframe(profile)

        # Save CSV output
        csv = prep_df(load_file_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="large_df.csv",
            mime="text/csv",
        )

###