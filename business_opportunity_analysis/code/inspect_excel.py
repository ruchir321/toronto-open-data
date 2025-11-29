import pandas as pd

def inspect_excel(file_path):
    try:
        df = pd.read_excel(file_path, nrows=5)
        print(f"Columns in {file_path}:")
        print(df.columns.tolist())
        print(df.head())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    try:
        df = pd.read_excel(file_path, sheet_name="RawData-Ref Period 2011", nrows=5)
        print(f"Columns in {file_path} (Sheet: RawData-Ref Period 2011):")
        print(df.columns.tolist())
        print(df.head())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

inspect_excel("../data/wellbeing_economics.xlsx")
