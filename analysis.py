from datetime import timedelta
import pandas as pd

# lưu dữ liệu vào file csv
def save_data(df, path):
    df.to_csv(path, index=False)
    return True

# thêm dữ liệu thời tiết
def add_record(df, record: dict):
    rec = record.copy()
    if 'Date' in rec:
        rec['Date'] = pd.to_datetime(rec['Date'])
    if 'date' in rec:
        rec['date'] = pd.to_datetime(rec['date'])
    df2 = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)
    df2 = df2.sort_values('date').reset_index(drop=True)
    return df2

# cập nhật dữ liệu
def update_record(df, identifier: dict, updates: dict):
    df2 = df.copy()
    if 'index' in identifier:
        idx = identifier['index']
        if idx in df2.index:
            for k, v in updates.items():
                df2.at[idx, k] = v
    elif 'Date' in identifier:
        d = pd.to_datetime(identifier['Date'])
        mask = df2['date'] == d
        for k, v in updates.items():
            df2.loc[mask, k] = v
    else:
        mask = pd.Series([True] * len(df2))
        for k, v in identifier.items():
            if k in df2.columns:
                mask = mask & (df2[k] == v)
        for k, v in updates.items():
            df2.loc[mask, k] = v
    df2 = df2.sort_values('date').reset_index(drop=True)
    return df2

# xóa dữ liệu
def delete_record(df, identifier: dict):
    df2 = df.copy()
    if 'index' in identifier:
        idx = identifier['index']
        if idx in df2.index:
            df2 = df2.drop(idx)
    elif 'Date' in identifier:
        d = pd.to_datetime(identifier['Date'])
        df2 = df2[df2['date'] != d]
    else:
        mask = pd.Series([True] * len(df2))
        for k, v in identifier.items():
            if k in df2.columns:
                mask = mask & (df2[k] == v)
        df2 = df2[~mask]
    df2 = df2.sort_values('date').reset_index(drop=True)
    return df2

# Phát hiện các đợt nắng nóng kéo dài.
def detect_heatwaves(df, temp_col='day_avgtemp_c', threshold=30, min_days=3):
    try:
        s = df.set_index('date')[temp_col].resample('D').mean().ffill()
        mask = s >= threshold
        events = []
        start = None
        for d, val in mask.items():
            if val and start is None:
                start = d
            if (not val or d == mask.index[-1]) and start is not None:
                end = d if not val else d
                length = (end - start).days + (0 if not val else 1)
                if length >= min_days:
                    events.append((start, end - timedelta(days=0), length))
                start = None
        return events
    except Exception as e:
        print(f"Lỗi detect_heatwaves: {e}")
        return []

# Phát hiện ngày mưa lớn.
def detect_heavy_rain(df, precip_col='day_totalprecip_mm', threshold_mm=100):
    try:
        if precip_col not in df.columns:
            return pd.DataFrame()
        s = df.set_index('date')[precip_col].resample('D').sum()
        result = s[s >= threshold_mm].reset_index().rename(columns={precip_col:'TotalPrecipitation'})
        result['Date'] = result['date']
        return result
    except Exception as e:
        print(f"Lỗi detect_heavy_rain: {e}")
        return pd.DataFrame()