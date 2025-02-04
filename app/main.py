import os
import pandas as pd
import streamlit as st

from utils import convert_dat_to_df, compute_value_info, set_sample_df, convert_opt_to_df, manipulate_dataframes, compute_opt_info


### ------------------------ ###
# Streamlit Settings
### ------------------------ ###

st.set_page_config(layout="wide")

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

# Title
st.title("Load File Profiler")
uploaded_file = st.file_uploader("Upload a DAT or CSV file", type=["dat", "csv"])
if uploaded_file: # Load File
    
    opt_file = st.file_uploader("Upload an optional OPT file", type=["opt"]) # OPT
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension == ".dat":
        load_file_df = convert_dat_to_df(uploaded_file)
    elif file_extension == ".csv":
        load_file_df = pd.read_csv(uploaded_file, dtype=str)
    else:
        st.error("Unsupported file type.")
        st.stop()
    
    # Data Profiling
    st.button('Run data profile.', on_click=click_button)
    if st.session_state.clicked:
        st.success("File loaded successfully!")
        st.subheader("Size of Load File (Rows,Columns):")
        st.text(load_file_df.shape)
        if opt_file:
            opt_df = convert_opt_to_df(opt_file)
            opt_profile = compute_opt_info(opt_df)
            st.subheader("OPT File")
            st.json(opt_profile['Profile'])
            st.dataframe(opt_profile['Dataframe'])
            if len(load_file_df) != len(opt_profile['Docs']):
                st.warning("OPT reads " + str(len(opt_profile['Docs'])) + " docs and Load File reads " + str(len(load_file_df)) + " docs.")
        try:
            sampled_df = set_sample_df(load_file_df)
            st.subheader("Dataframe Preview")
            st.dataframe(sampled_df)
        except ValueError as e:
            st.error(f"Error: {e}")

        # Profile data
        lf_profile = compute_value_info(load_file_df)
        st.subheader("Load File Data Profile")
        st.dataframe(lf_profile)

        # Data Manipulations / Output
        if opt_file:
            try:
                manipulate_dataframes(load_file_df, opt_df, os.path.splitext(uploaded_file.name)[0].lower())
            except ValueError as e:
                st.error(f"Error: {e}")
        else:
            try:
                manipulate_dataframes(load_file_df, None, os.path.splitext(uploaded_file.name)[0].lower())
            except ValueError as e:
                st.error(f"Error: {e}")