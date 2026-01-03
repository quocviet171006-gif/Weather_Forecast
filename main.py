import tkinter as tk
from load_data import read_and_check_file
from clean_data import remove_duplicate_rows, column_name_normalization, convert_date_data_to_datetime, \
    handling_NaN_values
from gui import WeatherApp


def main():
    # Đọc dữ liệu
    print("Đang đọc file dữ liệu...")
    df = read_and_check_file('df_weather.csv')

    if df is None:
        print("Không thể đọc file. Chương trình dừng.")
        return

    # Làm sạch dữ liệu
    print("\nĐang làm sạch dữ liệu...")
    df = remove_duplicate_rows(df)
    df = column_name_normalization(df)
    df = convert_date_data_to_datetime(df)
    df = handling_NaN_values(df, method="mean")

    # Lưu dữ liệu đã làm sạch
    df.to_csv('df_weather.csv', index=False)
    print("Dữ liệu đã được làm sạch và lưu lại!")

    # Khởi động GUI
    print("\nKhởi động giao diện...")
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()