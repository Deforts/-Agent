# generate_mock_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
end_date = datetime(2026, 6, 11)
dates = [end_date - timedelta(days=i) for i in range(59, -1, -1)]

data = []
for i, date in enumerate(dates):
    # 基础趋势（缓慢增长）
    trend = 1 + i * 0.008
    # 周期性波动：模拟周末效应（周六日DAU略高，周一略低）
    weekday = date.weekday()  # 0=周一, 6=周日
    if weekday >= 5:  # 周末
        cycle = 1.05
    elif weekday == 0:  # 周一
        cycle = 0.96
    else:
        cycle = 1.0
    
    # 随机噪声
    noise_dau = np.random.normal(0, 0.03)
    noise_new = np.random.normal(0, 0.05)
    
    base_dau = 12000
    dau = int(base_dau * trend * cycle * (1 + noise_dau))
    dau = max(10000, min(18000, dau))
    
    base_new = 2000
    new_users = int(base_new * trend * (1 + noise_new))
    new_users = max(1500, min(3500, new_users))
    
    # 留存率受星期影响（周末留存略低）
    retention = 0.42 + np.random.normal(0, 0.01)
    if weekday >= 5:
        retention -= 0.02
    retention = max(0.38, min(0.46, retention))
    retention = round(retention, 3)
    
    # 营收与DAU正相关，加噪声
    revenue = int(dau * 0.55 + np.random.randint(-300, 500))
    revenue = max(6000, min(10000, revenue))
    
    data.append([date.strftime("%Y-%m-%d"), dau, new_users, retention, revenue])

df = pd.DataFrame(data, columns=["date", "dau", "new_users", "retention_day1", "revenue_usd"])
df.to_csv("data/mock_data.csv", index=False)
print("已生成更真实的60天数据（包含周期性波动和随机噪声）")