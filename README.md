# Production Load File Data Profiling Tool

This is a Streamlit-based application designed to analyze and manipulate production data load files (`DAT`, `CSV`, and optional `OPT` files). The tool includes features for profiling, sampling, data manipulation, and exporting results.

## Features
- Upload and process load files (`DAT`, `CSV`, and `OPT`).
- Profile data, including column statistics and unique values.
- Random sampling of data (25 rows and all columns).
- Data manipulation features:
  - Remove empty columns.
  - Find and replace text in specific columns, with support for raw strings.
  - Duplicate columns with a custom name.
- Export modified data as UTF-8 encoded CSV files with optional partitioning.

---

## System Requirements
- **Python Version**: Python 3.12 or higher
- **Operating System**: Compatible with Windows, macOS, and Linux
- **Additional Software**: Git (to clone the repository)

---

## Setup Instructions

Follow these steps to clone the app and get it running:

### 1. Install Python
- Download and install Python 3.12 or later from the [official Python website](https://www.python.org/downloads/).
- Make sure to check the option to "Add Python to PATH" during installation.

### 2. Install Git
- Download and install Git from the [official Git website](https://git-scm.com/).

### 3. Clone the Repository
- Open a terminal (Command Prompt, PowerShell, or terminal on macOS/Linux).
- Navigate to an empty folder on your local device
- Run the following command to clone the repository:
    ```
    git clone https://github.com/dkeserovic/production-profile.git
    ```

### 4. Navigate to the Project Directory
- Navigate to the cloned project folder:
    ```
    cd name/of/folder
    ```

### 5. Create and activate Virtual Environment
- Create a virtual environment to manage dependencies:
    ```
    python -m venv venv
    ```
- Activate the virtual environment:
- On **Windows**:
  ```
  venv\Scripts\activate
  ```

### 6. Install Dependencies
- Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```

### 7. Run the Application
- Execute the following command. you can change the max upload size to any value that represents total megabytes
    ```
    streamlit run app/main.py --server.maxUploadSize=5120
    ```


## How to Use the Tool
1. **Upload Files**:
 - Upload your load files (`DAT`, `CSV`, or optional `OPT`).
 - The app will parse and display the data.
2. **Profile Data**:
 - View key statistics such as row/column counts, unique values, and missing data.
3. **Manipulate Data**:
 - Use the provided tools to clean and transform your dataset.
4. **Export Data**:
 - Save the processed data as CSV files, with options for partitioning.

---

## Troubleshooting
- If the app fails to start, ensure you have activated the virtual environment and installed dependencies.
- For encoding issues, ensure your input files are UTF-8 encoded.
- For advanced debugging, check the Streamlit logs in the terminal.