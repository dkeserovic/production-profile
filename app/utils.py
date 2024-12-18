import pandas as pd
import os
from dateutil.parser import parse
import csv
import sys
import streamlit as st
import re

### ------------------------ ###
#  Data Preparation Functions
### ------------------------ ###

@st.cache_data
def convert_dat_to_df(dat_file):
    # Dealing with overflow errors
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)

    # Read .dat file into a DataFrame
    df = pd.read_csv(dat_file, sep="", quotechar="þ", dtype=str, doublequote=False, encoding='utf-8', engine='python')
    return df

@st.cache_data
def convert_opt_to_df(opt_file):
    # Read .csv file into a DataFrame
    df = pd.read_csv(opt_file, encoding='utf-8', engine='python',names=['Filename', 'Volume', 'Path', 'First Page', 'Col1', 'Col2', 'Page Count'])
    df.dropna(axis=1, how='all')
    return df

@st.cache_data
def compute_value_info(df):
    min_lengths = {}
    max_lengths = {}
    datatypes = {}

    for col in df.columns:
        values = df[col]

        # data type check
        datatype = values.dtype
        values_filled = values.fillna('')
        # Initialize min and max values based on data type

        # Handle datetime columns
        if is_date_col(values_filled):
            min_lengths[col] = values.min()
            max_lengths[col] = values.max()
            datatypes[col] = 'datetime'
                # Check for string columns
        elif datatype is object and pd.api.types.is_string_dtype(values):
            # Replace NaN with empty string
            values_filled = values.fillna('')
            min_lengths[col] = values_filled.str.len().min()
            max_lengths[col] = values_filled.str.len().max()
            datatypes[col] = 'string'
        # Handle boolean columns
        elif pd.api.types.is_bool_dtype(values):
            min_lengths[col] = 0
            max_lengths[col] = 1
            datatypes[col] = 'boolean'
                # Check for numeric columns
        elif pd.api.types.is_numeric_dtype(values):
            # Replace NaN with 0
            values_filled = values.fillna(0)
            # incorrect empty read - revert to object
            if sum(list(values_filled)) == 0:
                min_lengths[col] = 0
                max_lengths[col] = 0
                datatypes[col] = 'object'
            else:
                min_lengths[col] = values_filled.min()
                max_lengths[col] = values_filled.max()
                datatypes[col] = 'numeric'
        # For other types, treat as generic objects
        else:
            min_lengths[col] = 0
            max_lengths[col] = 0
            datatypes[col] = 'unknown'

    num_rows = len(df)
    missing_counts = df.isna().sum()
    filled_percentages = (1 - (missing_counts / num_rows)) * 100

    profile_df = pd.DataFrame({"Data Type":datatypes, "Min": min_lengths, "Max": max_lengths, "% Values Filled": filled_percentages})
    return profile_df

@st.cache_data
def compute_opt_info(df):
    df = df.dropna(axis=1, how='all')

    results = {}
    # 1. List unique prefixes in 'Filename'
    def extract_prefix(filename):
        match = re.match(r'([a-zA-Z_\-]+)(\d+)', filename)
        return match.group(1).strip() if match else None

    prefixes = df['Filename'].apply(extract_prefix).dropna().unique()
    results['Unique Prefixes'] = prefixes.tolist()

    # 2. List filename lengths per prefix
    filename_lengths = df['Filename'].apply(len)
    lengths_per_prefix = (
        df.assign(Length=filename_lengths)
        .groupby(df['Filename'].apply(extract_prefix))['Length']
        .unique()
        .apply(lambda x: list(map(int, x)))  # Convert to int
    )
    results['Filename Lengths per Prefix'] = lengths_per_prefix.to_dict()

    # 3. List unique values in 'Volume'
    results['Unique Volumes'] = df['Volume'].dropna().unique().tolist()

    # 4. Count values in 'First Page'
    first_page_count = (df['First Page'] == "Y").sum()
    results['Total Docs'] = int(first_page_count)

    # 5. Count values in 'Page Count' equal to 1
    page_count_equal_1 = (df['Page Count'] == 1).sum()
    results['Page Count Equal to 1'] = int(page_count_equal_1)

    # 6. Count values in 'Page Count' greater than 1
    page_count_greater_1 = (df['Page Count'] > 1).sum()
    results['Page Count Greater than 1'] = int(page_count_greater_1)

    opt_profile = {'Profile':results, 'Dataframe':df}

    return opt_profile

def manipulate_dataframes(df1, df2, load_file_name):
    with st.form("data_manipulation_form"):
        st.header("Data Manipulation Options")

        # Remove empty columns
        remove_empty_cols = st.checkbox("Remove empty columns")

        # Find and Replace
        st.subheader("Find and Replace")
        columns_to_search = st.multiselect("Select columns to search in", df1.columns)
        find_text = st.text_input("Text to find")
        replace_text = st.text_input("Replace with")

        # Duplicate Column
        st.subheader("Duplicate Column")
        col_to_duplicate = st.selectbox("Select column to duplicate", df1.columns)
        new_col_name = st.text_input("New column name")

        # Export CSV Settings
        st.subheader("Export Settings")
        export_csv = st.checkbox("Export DataFrame as CSV")
        partition_size = st.number_input(
            "Partition size (rows per CSV file). If no partition needed, enter value that is larger than # of rows in CSV", min_value=1, step=1, value=100000
        )
        export_folder = "app/outputs"

        # Submit Button
        submitted = st.form_submit_button("Apply Changes")

        if submitted:
            # Perform Data Manipulations
            if remove_empty_cols:
                df1.dropna(axis=1, how="all", inplace=True)
                st.success("Empty columns removed.")

            # Handle Find and Replace
            if find_text and columns_to_search:
                try:
                    # Convert input to raw string format
                    raw_find_text = re.escape(find_text)
                    print("Find: " + raw_find_text)
                    raw_replace_text = fr"{replace_text}"
                    print("Replace: " + raw_replace_text)

                    for col in columns_to_search:
                        df1[col] = df1[col].replace(raw_find_text, raw_replace_text, regex=True)
                    st.success(f"Replaced '{find_text}' with '{replace_text}' in selected columns.")
                except Exception as e:
                    st.error(f"Find and replace failed: {e}")

            if col_to_duplicate and new_col_name:
                if new_col_name not in df1.columns:
                    df1[new_col_name] = df1[col_to_duplicate]
                    st.success(f"Duplicated column '{col_to_duplicate}' as '{new_col_name}'.")
                else:
                    st.error(f"Column '{new_col_name}' already exists.")

            # Export CSV Logic
            if export_csv:
                if not os.path.exists(export_folder):
                    os.makedirs(export_folder)

                total_rows = len(df1)
                num_files = (total_rows // partition_size) + (total_rows % partition_size > 0)
                load_file_name = load_file_name.replace(" ", "_")

                for i in range(num_files):
                    start_row = i * partition_size
                    end_row = min(start_row + partition_size, total_rows)
                    partition_df = df1.iloc[start_row:end_row]

                    output_file = os.path.join(export_folder, f"{load_file_name}_{i+1}.csv")
                    partition_df.to_csv(output_file, index=False, encoding="utf-8")

                st.success(f"Exported {num_files} CSV file(s) to '{export_folder}'.")

def sample_values(df):
    num_rows = len(df)
    num_samples = min(num_rows, 50)  # Sample 50 rows or less if the DataFrame is smaller
    sample_df = df.sample(num_samples)
    return sample_df

def is_date_col(vals, fuzzy=False):
    """
    Return whether the list of values can be interpreted as dates.

    :param vals: list of values to check for dates
    :param fuzzy: bool, ignore unknown tokens in string if True
    :return: True if all non-NaN values can be parsed as dates, False otherwise
    """
    for val in vals:
        if pd.isna(val):
            # Skip NaN values
            continue
        if isinstance(val, str):
            try:
                parse(val, fuzzy=fuzzy)
            except ValueError:
                # If any string value cannot be parsed as a date, return False
                return False
        else:
            # If the value is not a string, it cannot be a date
            return False
    # If all non-NaN values can be parsed as dates, return True
    return True

def remove_empty_cols(df):
    # Drop columns where all values are NaN
    df_cleaned = df.dropna(axis=1, how='all')
    return df_cleaned

def clean_csv(df, filename):
    outputs_folder = "output"
    filename = filename.split(".")[0] + "_CLEAN.csv"
    csv_file_path = os.path.join(outputs_folder, filename)
    print(csv_file_path)
    df.to_csv(csv_file_path, index=False, encoding='utf-8')
    return
    
def random_sample_df(df, sample_size=25):
    """
    Perform a random sampling of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to sample from.
    sample_size (int): Number of rows to sample (default is 25).

    Returns:
    pd.DataFrame: A new DataFrame containing the sampled rows.
    """
    if df.empty:
        raise ValueError("The DataFrame is empty.")
    
    if sample_size <= 0:
        raise ValueError("Sample size must be greater than zero.")
    
    if sample_size > len(df):
        sample_size = len(df)  # Adjust to DataFrame size if too large
    
    sampled_df = df.sample(n=sample_size, random_state=42)
    return sampled_df