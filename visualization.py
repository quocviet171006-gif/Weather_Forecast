import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class WeatherVisualizer:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid")

    # Biểu đồ đường: Xu hướng nhiệt độ theo thời gian
    def plot_temp_trend(self):
        if 'date' not in self.df.columns or 'day_avgtemp_c' not in self.df.columns:
            return None

        fig = plt.figure(figsize=(10, 5))
        daily_avg = self.df.groupby('date')['day_avgtemp_c'].mean()
        plt.plot(daily_avg.index, daily_avg.values, label='Nhiệt độ TB (°C)', color='#d62728')
        plt.title('Xu hướng Nhiệt độ trung bình theo Thời gian')
        plt.xlabel('Ngày')
        plt.ylabel('Nhiệt độ (°C)')
        plt.legend()
        plt.tight_layout()
        return fig

    # Biểu đồ cột: Nhiệt độ trung bình theo tháng
    def plot_monthly_stats(self):
        if 'month' not in self.df.columns:
            self.df['month'] = pd.to_datetime(self.df['date']).dt.month

        fig = plt.figure(figsize=(8, 5))
        monthly_avg = self.df.groupby('month')['day_avgtemp_c'].mean()
        plt.bar(monthly_avg.index, monthly_avg.values, color='#ff7f0e', alpha=0.8)
        plt.title('Nhiệt độ Trung bình từng Tháng')
        plt.xlabel('Tháng')
        plt.ylabel('Nhiệt độ (°C)')
        plt.xticks(range(1, 13))
        return fig

    # Boxplot: So sánh nhiệt độ giữa các vùng miền
    def plot_region_comparison(self):
        if 'location_region' not in self.df.columns:
            return None

        fig = plt.figure(figsize=(12, 6))
        # Sắp xếp thứ tự
        try:
            order = self.df.groupby('location_region')['day_avgtemp_c'].median().sort_values(ascending=False).index
            sns.boxplot(data=self.df, x='location_region', y='day_avgtemp_c', order=order, palette="Set2")
            plt.title('Phân bố Nhiệt độ theo Vùng miền (Độ ổn định khí hậu)')
            plt.xlabel('Vùng')
            plt.ylabel('Nhiệt độ (°C)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            return fig
        except Exception as e:
            print(f"Lỗi khi vẽ biểu đồ vùng: {e}")
            return None

    # Biểu đồ nhiệt (Heatmap) phân tích mối quan hệ giữa tất cả các yếu tố
    def plot_correlation(self):
        fig = plt.figure(figsize=(10, 8))

        cols = [
            'day_avgtemp_c',  # Nhiệt độ
            'day_avghumidity',  # Độ ẩm
            'day_totalprecip_mm',  # Lượng mưa
            'day_maxwind_kph',  # Gió
            'day_uv',  # UV
            'day_avgvis_km',  # Tầm nhìn (Mới)
            'day_daily_chance_of_rain'  # Khả năng mưa (Mới)
        ]
        # Đặt tên tiếng Việt
        readable_names = {
            'day_avgtemp_c': 'Nhiệt độ',
            'day_avghumidity': 'Độ ẩm',
            'day_totalprecip_mm': 'Lượng mưa',
            'day_maxwind_kph': 'Gió',
            'day_uv': 'Tia UV',
            'day_avgvis_km': 'Tầm nhìn',
            'day_daily_chance_of_rain': 'Khả năng mưa'
        }
        valid_cols = [c for c in cols if c in self.df.columns]

        if len(valid_cols) > 1:
            df_corr = self.df[valid_cols].rename(columns=readable_names)
            corr = df_corr.corr()

            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
            plt.title('Phân tích tổng hợp: Tương quan giữa các yếu tố thời tiết')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            return fig
        return None