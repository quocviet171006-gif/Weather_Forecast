import pandas as pd

def read_and_check_file(file_path):
    try:
        df = pd.read_csv(file_path)
        # In thông tin tổng quan của dữ liệu
        print("Dữ liệu ban đầu:")
        df.info()

        # Kiểm tra kiểu dữ liệu của từng cột
        print("\nKiểu dữ liệu của các cột:")
        print(df.dtypes)

        # Kiểm tra số lượng giá trị thiếu (NaN)
        print("\nSố lượng giá trị thiếu (NaN) theo cột:")
        print(df.isnull().sum())

        return df

    except FileNotFoundError:
        print("Không tìm thấy file")
        return None