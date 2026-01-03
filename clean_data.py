import numpy as np
import pandas as pd

# Hàm xoá các dòng trùng lặp
def remove_duplicate_rows(df):
    df = df.copy()
    df = df.drop_duplicates()
    df.reset_index(drop=True, inplace=True)
    return df

#Hàm chuẩn hoá tên cột
def column_name_normalization(df):
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df

# Hàm chuyển dữ liệu date sang datetime
def convert_date_data_to_datetime(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df

# Hàm xử lí NaN
def handling_NaN_values(df, method):
    df = df.copy()
    num_cols = df.select_dtypes(include=[np.number]).columns

    if method == "mean":
        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
    elif method == "median":
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    elif method == "ffill" or method == "bfill":
        df[num_cols] = df[num_cols].ffill().bfill()

    return df