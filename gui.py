import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualization import WeatherVisualizer
from analysis import detect_heatwaves, detect_heavy_rain, add_record, update_record, delete_record, save_data


class WeatherApp:
    def __init__(self, root):
        """Khởi tạo ứng dụng: thiết lập cửa sổ, đọc dữ liệu từ CSV, tạo giao diện"""
        self.root = root
        self.root.title("Hệ thống Thống kê Thời tiết")
        self.root.geometry("1400x700")
        self.root.configure(bg='#f0f0f0')

        try:
            self.df = pd.read_csv('df_weather.csv')
            self.df['date'] = pd.to_datetime(self.df['date'])
            # Tạo các cột cần thiết cho analysis
            if 'day_avgtemp_c' in self.df.columns:
                self.df['Temperature'] = self.df['day_avgtemp_c']
            if 'day_totalprecip_mm' in self.df.columns:
                self.df['Precipitation'] = self.df['day_totalprecip_mm']
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file dữ liệu: {e}")
            return

        self.visualizer = WeatherVisualizer(self.df)
        self.canvas_widget = None

        self.create_widgets()

    def create_widgets(self):
        """Tạo các thành phần giao diện: header, control panel, data management panel, vùng hiển thị"""
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=60)
        header.pack(fill='x')

        title = tk.Label(header, text="📊 THỐNG KÊ THỜI TIẾT",
                         font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=15)

        # Control Panel
        control_frame = tk.Frame(self.root, bg='#ecf0f1', height=100)
        control_frame.pack(fill='x', padx=10, pady=10)

        # Left section: Dropdown chọn tháng/năm
        select_frame = tk.Frame(control_frame, bg='#ecf0f1')
        select_frame.pack(side='left', padx=20)

        tk.Label(select_frame, text="Chọn tháng:", bg='#ecf0f1',
                 font=('Arial', 10)).grid(row=0, column=0, padx=5)

        months = [f"Tháng {i}" for i in range(1, 13)]
        self.month_var = tk.StringVar(value="Tháng 1")
        month_dropdown = ttk.Combobox(select_frame, textvariable=self.month_var,
                                      values=months, state='readonly', width=10)
        month_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(select_frame, text="Năm:", bg='#ecf0f1',
                 font=('Arial', 10)).grid(row=0, column=2, padx=5)

        years = sorted(self.df['date'].dt.year.unique())
        self.year_var = tk.StringVar(value=str(years[0]) if years else "2024")
        year_dropdown = ttk.Combobox(select_frame, textvariable=self.year_var,
                                     values=years, state='readonly', width=8)
        year_dropdown.grid(row=0, column=3, padx=5)

        # Middle section: View buttons
        btn_frame = tk.Frame(control_frame, bg='#ecf0f1')
        btn_frame.pack(side='left', padx=20)

        btn_month = tk.Button(btn_frame, text="📅 Thống kê Tháng",
                              command=self.show_month_stats,
                              bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                              padx=15, pady=8, relief='raised', cursor='hand2')
        btn_month.pack(side='left', padx=5)

        btn_year = tk.Button(btn_frame, text="📈 Thống kê Năm",
                             command=self.show_year_stats,
                             bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                             padx=15, pady=8, relief='raised', cursor='hand2')
        btn_year.pack(side='left', padx=5)

        # Right section: Data management buttons
        data_frame = tk.Frame(control_frame, bg='#ecf0f1')
        data_frame.pack(side='right', padx=20)

        btn_add = tk.Button(data_frame, text="➕ Thêm",
                            command=self.add_data,
                            bg='#27ae60', fg='white', font=('Arial', 9, 'bold'),
                            padx=10, pady=8, relief='raised', cursor='hand2')
        btn_add.pack(side='left', padx=3)

        btn_update = tk.Button(data_frame, text="✏️ Cập nhật",
                               command=self.update_data,
                               bg='#f39c12', fg='white', font=('Arial', 9, 'bold'),
                               padx=10, pady=8, relief='raised', cursor='hand2')
        btn_update.pack(side='left', padx=3)

        btn_delete = tk.Button(data_frame, text="🗑️ Xóa",
                               command=self.delete_data,
                               bg='#c0392b', fg='white', font=('Arial', 9, 'bold'),
                               padx=10, pady=8, relief='raised', cursor='hand2')
        btn_delete.pack(side='left', padx=3)

        btn_save = tk.Button(data_frame, text="💾 Lưu",
                             command=self.save_data_to_file,
                             bg='#8e44ad', fg='white', font=('Arial', 9, 'bold'),
                             padx=10, pady=8, relief='raised', cursor='hand2')
        btn_save.pack(side='left', padx=3)

        # Display Area
        self.display_frame = tk.Frame(self.root, bg='white')
        self.display_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def clear_display(self):
        """Xóa toàn bộ nội dung trong vùng hiển thị"""
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        if self.canvas_widget:
            self.canvas_widget = None

    def reload_data(self):
        """Tải lại dữ liệu sau khi thêm/sửa/xóa"""
        self.df['date'] = pd.to_datetime(self.df['date'])
        if 'day_avgtemp_c' in self.df.columns:
            self.df['Temperature'] = self.df['day_avgtemp_c']
        if 'day_totalprecip_mm' in self.df.columns:
            self.df['Precipitation'] = self.df['day_totalprecip_mm']
        self.visualizer = WeatherVisualizer(self.df)

    def add_data(self):
        """Thêm bản ghi dữ liệu thời tiết mới"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Thêm dữ liệu mới")
        dialog.geometry("400x500")
        dialog.configure(bg='#ecf0f1')

        tk.Label(dialog, text="📝 THÊM DỮ LIỆU MỚI", font=('Arial', 14, 'bold'),
                 bg='#ecf0f1').pack(pady=10)

        # Form fields
        fields = [
            ('Ngày (YYYY-MM-DD):', 'date'),
            ('Địa điểm:', 'location_name'),
            ('Vùng miền:', 'location_region'),
            ('Nhiệt độ TB (°C):', 'day_avgtemp_c'),
            ('Độ ẩm (%):', 'day_avghumidity'),
            ('Lượng mưa (mm):', 'day_totalprecip_mm'),
            ('Gió (kph):', 'day_maxwind_kph'),
            ('Chỉ số UV:', 'day_uv'),
            ('Tầm nhìn (km):', 'day_avgvis_km'),
            ('Khả năng mưa (%):', 'day_daily_chance_of_rain')
        ]

        entries = {}
        for label, key in fields:
            frame = tk.Frame(dialog, bg='#ecf0f1')
            frame.pack(fill='x', padx=20, pady=5)
            tk.Label(frame, text=label, bg='#ecf0f1', width=20, anchor='w').pack(side='left')
            entry = tk.Entry(frame, width=25)
            entry.pack(side='right')
            entries[key] = entry

        def submit():
            try:
                record = {}
                for key, entry in entries.items():
                    value = entry.get().strip()
                    if not value:
                        continue
                    if key == 'date':
                        record['date'] = value
                    elif key in ['day_avgtemp_c', 'day_avghumidity', 'day_totalprecip_mm',
                                 'day_maxwind_kph', 'day_uv', 'day_avgvis_km', 'day_daily_chance_of_rain']:
                        record[key] = float(value)
                    else:
                        record[key] = value

                self.df = add_record(self.df, record)
                self.reload_data()
                messagebox.showinfo("Thành công", "Đã thêm dữ liệu mới!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm dữ liệu: {e}")

        tk.Button(dialog, text="✅ Thêm", command=submit, bg='#27ae60', fg='white',
                  font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=15)

    def update_data(self):
        """Cập nhật dữ liệu thời tiết theo ngày"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cập nhật dữ liệu")
        dialog.geometry("400x400")
        dialog.configure(bg='#ecf0f1')

        tk.Label(dialog, text="✏️ CẬP NHẬT DỮ LIỆU", font=('Arial', 14, 'bold'),
                 bg='#ecf0f1').pack(pady=10)

        # Chọn ngày cần cập nhật
        tk.Label(dialog, text="Chọn ngày cần cập nhật:", bg='#ecf0f1').pack(pady=5)
        date_var = tk.StringVar()
        dates = sorted([d.strftime('%Y-%m-%d') for d in self.df['date'].unique()])
        date_combo = ttk.Combobox(dialog, textvariable=date_var, values=dates,
                                  state='readonly', width=30)
        date_combo.pack(pady=5)

        # Các trường cập nhật
        fields = [
            ('Nhiệt độ TB (°C):', 'day_avgtemp_c'),
            ('Độ ẩm (%):', 'day_avghumidity'),
            ('Lượng mưa (mm):', 'day_totalprecip_mm'),
            ('Gió (kph):', 'day_maxwind_kph'),
            ('Chỉ số UV:', 'day_uv')
        ]

        entries = {}
        for label, key in fields:
            frame = tk.Frame(dialog, bg='#ecf0f1')
            frame.pack(fill='x', padx=20, pady=5)
            tk.Label(frame, text=label, bg='#ecf0f1', width=18, anchor='w').pack(side='left')
            entry = tk.Entry(frame, width=20)
            entry.pack(side='right')
            entries[key] = entry

        def submit():
            try:
                date_str = date_var.get()
                if not date_str:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngày!")
                    return

                updates = {}
                for key, entry in entries.items():
                    value = entry.get().strip()
                    if value:
                        updates[key] = float(value)

                if not updates:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất một trường!")
                    return

                self.df = update_record(self.df, {'Date': date_str}, updates)
                self.reload_data()
                messagebox.showinfo("Thành công", f"Đã cập nhật dữ liệu ngày {date_str}!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")

        tk.Button(dialog, text="✅ Cập nhật", command=submit, bg='#f39c12', fg='white',
                  font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=15)

    def delete_data(self):
        """Xóa dữ liệu thời tiết theo ngày"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Xóa dữ liệu")
        dialog.geometry("350x200")
        dialog.configure(bg='#ecf0f1')

        tk.Label(dialog, text="🗑️ XÓA DỮ LIỆU", font=('Arial', 14, 'bold'),
                 bg='#ecf0f1').pack(pady=10)

        tk.Label(dialog, text="Chọn ngày cần xóa:", bg='#ecf0f1').pack(pady=5)
        date_var = tk.StringVar()
        dates = sorted([d.strftime('%Y-%m-%d') for d in self.df['date'].unique()])
        date_combo = ttk.Combobox(dialog, textvariable=date_var, values=dates,
                                  state='readonly', width=30)
        date_combo.pack(pady=10)

        def submit():
            try:
                date_str = date_var.get()
                if not date_str:
                    messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngày!")
                    return

                confirm = messagebox.askyesno("Xác nhận",
                                              f"Bạn có chắc muốn xóa dữ liệu ngày {date_str}?")
                if confirm:
                    self.df = delete_record(self.df, {'Date': date_str})
                    self.reload_data()
                    messagebox.showinfo("Thành công", f"Đã xóa dữ liệu ngày {date_str}!")
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")

        tk.Button(dialog, text="✅ Xóa", command=submit, bg='#c0392b', fg='white',
                  font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=15)

    def save_data_to_file(self):
        """Lưu dữ liệu vào file CSV"""
        try:
            save_data(self.df, 'df_weather.csv')
            messagebox.showinfo("Thành công", "Đã lưu dữ liệu vào file df_weather.csv!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def show_month_stats(self):
        """Hiển thị thống kê tháng: biểu đồ nhiệt độ và nhiệt độ trung bình"""
        self.clear_display()

        month_str = self.month_var.get()
        month = int(month_str.split()[1])
        year = int(self.year_var.get())

        df_month = self.df[(self.df['date'].dt.month == month) &
                           (self.df['date'].dt.year == year)].copy()

        if df_month.empty:
            messagebox.showwarning("Không có dữ liệu",
                                   f"Không có dữ liệu cho {month_str}/{year}")
            return

        # Chart frame
        chart_frame = tk.Frame(self.display_frame, bg='white')
        chart_frame.pack(side='left', fill='both', expand=True, padx=5)

        vis = WeatherVisualizer(df_month)
        fig = vis.plot_temp_trend()
        if fig:
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            self.canvas_widget = canvas

        # Info frame
        info_frame = tk.Frame(self.display_frame, bg='#ecf0f1', width=300)
        info_frame.pack(side='right', fill='y', padx=5)
        info_frame.pack_propagate(False)

        tk.Label(info_frame, text=f"📊 Thông tin {month_str}/{year}",
                 font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(pady=10)

        # Average temp
        if 'day_avgtemp_c' in df_month.columns:
            avg_temp = df_month['day_avgtemp_c'].mean()
            temp_label = tk.Label(info_frame,
                                  text=f"🌡️ Nhiệt độ TB: {avg_temp:.1f}°C",
                                  font=('Arial', 11), bg='#ecf0f1')
            temp_label.pack(pady=5, padx=10, anchor='w')

    def show_year_stats(self):
        """Hiển thị thống kê năm: 4 tab với biểu đồ nhiệt độ theo tháng, so sánh vùng, tương quan yếu tố, đợt nắng nóng và ngày mưa lớn"""
        self.clear_display()

        year = int(self.year_var.get())
        df_year = self.df[self.df['date'].dt.year == year].copy()

        if df_year.empty:
            messagebox.showwarning("Không có dữ liệu", f"Không có dữ liệu cho năm {year}")
            return

        notebook = ttk.Notebook(self.display_frame)
        notebook.pack(fill='both', expand=True)

        vis = WeatherVisualizer(df_year)

        # Tab 1: Monthly stats
        tab1 = tk.Frame(notebook, bg='white')
        notebook.add(tab1, text='Nhiệt độ theo Tháng')
        fig1 = vis.plot_monthly_stats()
        if fig1:
            canvas1 = FigureCanvasTkAgg(fig1, tab1)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill='both', expand=True)

        # Tab 2: Region comparison
        tab2 = tk.Frame(notebook, bg='white')
        notebook.add(tab2, text='So sánh Vùng miền')
        fig2 = vis.plot_region_comparison()
        if fig2:
            canvas2 = FigureCanvasTkAgg(fig2, tab2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill='both', expand=True)

        # Tab 3: Correlation
        tab3 = tk.Frame(notebook, bg='white')
        notebook.add(tab3, text='Tương quan Yếu tố')
        fig3 = vis.plot_correlation()
        if fig3:
            canvas3 = FigureCanvasTkAgg(fig3, tab3)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill='both', expand=True)

        # Tab 4: Heatwaves and Heavy Rain
        tab4 = tk.Frame(notebook, bg='white')
        notebook.add(tab4, text='Nắng nóng & Mưa lớn')

        # Main container with scrollbar
        main_container = tk.Frame(tab4, bg='white')
        main_container.pack(fill='both', expand=True)

        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = tk.Scrollbar(main_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create two columns inside scrollable frame
        left_frame = tk.Frame(scrollable_frame, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        right_frame = tk.Frame(scrollable_frame, bg='white')
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Left: Heatwaves
        tk.Label(left_frame, text=f"🔥 CÁC ĐỢT NẮNG NÓNG NĂM {year}",
                 font=('Arial', 14, 'bold'), bg='white', fg='#e74c3c').pack(pady=10)

        try:
            heatwaves = detect_heatwaves(df_year)

            if heatwaves and len(heatwaves) > 0:
                for i, (start, end, length) in enumerate(heatwaves, 1):
                    frame = tk.Frame(left_frame, bg='#ffe6e6', relief='solid', borderwidth=1)
                    frame.pack(fill='x', padx=5, pady=5)

                    tk.Label(frame, text=f"Đợt {i}:", font=('Arial', 10, 'bold'),
                             bg='#ffe6e6', fg='#e74c3c').pack(anchor='w', padx=10, pady=5)
                    tk.Label(frame, text=f"Từ: {start.strftime('%d/%m/%Y')}",
                             font=('Arial', 9), bg='#ffe6e6').pack(anchor='w', padx=20)
                    tk.Label(frame, text=f"Đến: {end.strftime('%d/%m/%Y')}",
                             font=('Arial', 9), bg='#ffe6e6').pack(anchor='w', padx=20)
                    tk.Label(frame, text=f"Kéo dài: {length} ngày",
                             font=('Arial', 9, 'bold'), bg='#ffe6e6', fg='#c0392b').pack(anchor='w', padx=20,
                                                                                         pady=(0, 5))
            else:
                tk.Label(left_frame, text="Không có đợt nắng nóng nào trong năm\n(Ngưỡng: >= 30°C, tối thiểu 3 ngày)",
                         font=('Arial', 10), bg='white', fg='gray', justify='center').pack(pady=20)
        except Exception as e:
            tk.Label(left_frame, text=f"Lỗi khi phát hiện nắng nóng:\n{str(e)}",
                     font=('Arial', 9), bg='white', fg='red', justify='center').pack(pady=20)

        # Right: Heavy Rain
        tk.Label(right_frame, text=f"🌧️ CÁC NGÀY MƯA LỚN NĂM {year}",
                 font=('Arial', 14, 'bold'), bg='white', fg='#3498db').pack(pady=10)

        try:
            heavy_rain = detect_heavy_rain(df_year)

            if not heavy_rain.empty:
                for idx, row in heavy_rain.iterrows():
                    frame = tk.Frame(right_frame, bg='#e6f2ff', relief='solid', borderwidth=1)
                    frame.pack(fill='x', padx=5, pady=5)

                    tk.Label(frame, text=f"📅 {row['Date'].strftime('%d/%m/%Y')}",
                             font=('Arial', 10, 'bold'), bg='#e6f2ff', fg='#2980b9').pack(anchor='w', padx=10, pady=5)
                    tk.Label(frame, text=f"Lượng mưa: {row['TotalPrecipitation']:.1f} mm",
                             font=('Arial', 9, 'bold'), bg='#e6f2ff', fg='#3498db').pack(anchor='w', padx=20,
                                                                                         pady=(0, 5))
            else:
                tk.Label(right_frame, text="Không có ngày mưa lớn nào trong năm\n(Ngưỡng: >= 100mm/ngày)",
                         font=('Arial', 10), bg='white', fg='gray', justify='center').pack(pady=20)
        except Exception as e:
            tk.Label(right_frame, text=f"Lỗi khi phát hiện mưa lớn:\n{str(e)}",
                     font=('Arial', 9), bg='white', fg='red', justify='center').pack(pady=20)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')