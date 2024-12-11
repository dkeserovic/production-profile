import pandas as pd
import os
from dateutil.parser import parse
import csv
import sys
import io
import chardet
import streamlit as st

### ------------------------ ###
#  Data Preparation Functions
### ------------------------ ###

@st.cache_data
def convert_dat_to_csv(dat_file):
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
def convert_opt_to_csv(opt_file):
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
        elif datatype == object and pd.api.types.is_string_dtype(values):
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

def save_csv(df, original_name):
    """Save the DataFrame to the outputs directory."""
    output_path = f"app/outputs/{os.path.splitext(original_name)[0]}.csv"
    df.to_csv(output_path, index=False, encoding='utf-8')

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

def eval_opt(df):
    df = remove_empty_cols(df)
    

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