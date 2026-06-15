import pandas as pd

# 读取数据（假设文件和 data 文件夹在同一级）
df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])

def query_dau(date_str):
    """查询某一天的日活用户数"""
    row = df[df["date"] == date_str]
    if row.empty:
        return 0
    return int(row["dau"].iloc[0])

def query_new_users(date_str):
    """查询某一天的新增用户数"""
    row = df[df["date"] == date_str]
    if row.empty:
        return 0
    return int(row["new_users"].iloc[0])

def query_retention(date_str):
    """查询某一天的次日留存率 (0~1)"""
    row = df[df["date"] == date_str]
    if row.empty:
        return 0.0
    return float(row["retention_day1"].iloc[0])

def query_revenue(date_str):
    """查询某一天的营收（美元）"""
    row = df[df["date"] == date_str]
    if row.empty:
        return 0.0
    return float(row["revenue_usd"].iloc[0])


def detect_anomaly(metric: str, date_str: str) -> dict:
    # 获取当天值、昨天值、上周同一天值
    today_val = get_metric(metric, date_str)
    yesterday_val = get_metric(metric, subtract_day(date_str, 1))
    week_ago_val = get_metric(metric, subtract_day(date_str, 7))

    changes = {
        "vs_yesterday": (today_val - yesterday_val) / yesterday_val if yesterday_val else 0,
        "vs_week_ago": (today_val - week_ago_val) / week_ago_val if week_ago_val else 0
    }
    anomalies = {k: v for k, v in changes.items() if abs(v) > 0.15}
    return {"metric": metric, "date": date_str, "anomalies": anomalies}
def get_comment_summary():
    """读取已标注的评论统计结果，返回字符串"""
    import pandas as pd
    try:
        df = pd.read_csv("data/user_comments_labeled.csv")
        counts = df["category"].value_counts()
        summary = f"抱怨 {counts.get('抱怨', 0)} 条，建议 {counts.get('建议', 0)} 条，询问 {counts.get('询问', 0)} 条"
        return summary
    except FileNotFoundError:
        return "尚未运行情感分析，请先执行 sentiment_analyzer.py 生成标签数据。"
   
def query_dau(date=None):
 if date is None:
    date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
# 原有查询逻辑...
def get_channel_summary(date_str=None):
    """获取指定日期各渠道的新增、留存、LTV，返回格式化的字符串"""
    import pandas as pd
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = pd.read_csv("data/channel_data.csv", parse_dates=["date"])
        day_data = df[df["date"] == date_str]
        if day_data.empty:
            return f"未找到 {date_str} 的渠道数据"
        lines = []
        for _, row in day_data.iterrows():
            lines.append(f"- {row['channel']}: 新增 {row['new_users']}, 留存率 {row['retention_day1']:.1%}, LTV ${row['ltv_usd']}")
        return "\n".join(lines)
    except FileNotFoundError:
        return "渠道数据文件不存在，请先运行 generate_advanced_data.py"

def get_activity_summary(date_str=None):
    """获取用户活跃度分层占比"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = pd.read_csv("data/activity_data.csv", parse_dates=["date"])
        day_data = df[df["date"] == date_str]
        if day_data.empty:
            return f"未找到 {date_str} 的活跃度数据"
        row = day_data.iloc[0]
        return f"高活跃用户 {row['high_active_ratio']:.1%}, 中活跃 {row['mid_active_ratio']:.1%}, 低活跃 {row['low_active_ratio']:.1%}"
    except FileNotFoundError:
        return "活跃度数据文件不存在，请先运行 generate_advanced_data.py"

def get_pay_summary(date_str=None):
    """获取付费指标"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = pd.read_csv("data/pay_metrics.csv", parse_dates=["date"])
        day_data = df[df["date"] == date_str]
        if day_data.empty:
            return f"未找到 {date_str} 的付费数据"
        row = day_data.iloc[0]
        return f"付费率 {row['pay_rate']:.1%}, ARPU ${row['arpu_usd']}, ARPPU ${row['arppu_usd']}"
    except FileNotFoundError:
        return "付费指标数据文件不存在，请先运行 generate_advanced_data.py"
    # ==================== 新增：同比/环比/预测/贡献度分析 ====================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

def get_weekly_compare(metric: str, date_str: str = None) -> str:
    """
    计算某指标本周某天 vs 上周同一天的增长率
    metric: 'dau', 'new_users', 'retention_day1', 'revenue_usd'
    """
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    last_week_date = target_date - timedelta(days=7)
    
    # 读取核心数据
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.set_index("date")
    
    if target_date not in df.index or last_week_date not in df.index:
        return f"日期 {date_str} 或上周同期数据缺失"
    
    current = df.loc[target_date, metric]
    last_week = df.loc[last_week_date, metric]
    change_pct = (current - last_week) / last_week * 100 if last_week != 0 else 0
    return f"{metric} 本周{target_date.strftime('%Y-%m-%d')} 为 {current:.2f}，上周同期 {last_week:.2f}，同比变化 {change_pct:+.1f}%"

def get_monthly_compare(metric: str, date_str: str = None) -> str:
    """月同比：本月某天 vs 上月同一天"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    # 上月同一天
    if target_date.month == 1:
        last_month_date = target_date.replace(year=target_date.year-1, month=12, day=target_date.day)
    else:
        last_month_date = target_date.replace(month=target_date.month-1)
    
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.set_index("date")
    
    if target_date not in df.index or last_month_date not in df.index:
        return f"日期 {date_str} 或上月同期数据缺失"
    
    current = df.loc[target_date, metric]
    last_month = df.loc[last_month_date, metric]
    change_pct = (current - last_month) / last_month * 100 if last_month != 0 else 0
    return f"{metric} 本月{target_date.strftime('%Y-%m-%d')} 为 {current:.2f}，上月同期 {last_month:.2f}，同比变化 {change_pct:+.1f}%"

def predict_next_week(metric: str) -> str:
    """
    使用最近30天数据训练线性回归，预测未来7天的平均值
    metric: 'dau', 'revenue_usd'
    """
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.sort_values("date")
    if len(df) < 7:
        return "数据不足，无法预测"
    
    # 使用最近30天（或全部）
    train_df = df.tail(30)
    X = np.arange(len(train_df)).reshape(-1, 1)  # 天数编号
    y = train_df[metric].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测未来7天
    future_X = np.arange(len(train_df), len(train_df)+7).reshape(-1, 1)
    predictions = model.predict(future_X)
    avg_pred = np.mean(predictions)
    return f"预测下周 {metric} 日均值为 {avg_pred:.0f}（基于最近30天线性趋势）"

def detect_anomaly_and_contribution(metric: str = "new_users", threshold: float = 0.15, date_str: str = None) -> str:
    """
    检测某指标是否异常（日环比超过阈值），如果是，计算各渠道的贡献度（仅适用于新增用户）
    返回分析结果字符串
    """
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    prev_date = target_date - timedelta(days=1)
    
    # 读取核心总指标
    df_core = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df_core = df_core.set_index("date")
    if target_date not in df_core.index or prev_date not in df_core.index:
        return "数据缺失，无法检测异常"
    
    current_total = df_core.loc[target_date, metric] if metric in df_core.columns else None
    prev_total = df_core.loc[prev_date, metric] if metric in df_core.columns else None
    if current_total is None or prev_total is None:
        return f"指标 {metric} 不在核心数据中"
    
    change_pct = (current_total - prev_total) / prev_total if prev_total != 0 else 0
    if abs(change_pct) < threshold:
        return f"{metric} 日环比变化 {change_pct:.1%}，未超过阈值 {threshold:.0%}，无异常"
    
    # 如果是新增用户，进行渠道贡献分析
    if metric == "new_users":
        try:
            df_channel = pd.read_csv("data/channel_data.csv", parse_dates=["date"])
            df_channel = df_channel[df_channel["date"].isin([target_date, prev_date])]
            if len(df_channel) == 0:
                return "渠道数据缺失，无法分析贡献度"
            # 计算每个渠道的增量贡献
            channels = df_channel["channel"].unique()
            contributions = []
            for ch in channels:
                curr = df_channel[(df_channel["channel"]==ch) & (df_channel["date"]==target_date)]["new_users"].values
                prev = df_channel[(df_channel["channel"]==ch) & (df_channel["date"]==prev_date)]["new_users"].values
                if len(curr)>0 and len(prev)>0:
                    delta = curr[0] - prev[0]
                    contributions.append((ch, delta))
            # 按贡献绝对值排序
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            result = f"⚠️ {metric} 异常波动：环比 {change_pct:+.1%}。各渠道贡献度（新增变化）：\n"
            for ch, delta in contributions:
                result += f"  - {ch}: {delta:+d}\n"
            return result
        except Exception as e:
            return f"渠道贡献分析失败: {e}"
    else:
        return f"{metric} 异常波动：环比 {change_pct:+.1%}，但暂不支持该指标的渠道拆解。"
    # ==================== 同比、预测、异常归因 ====================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

def get_weekly_compare(metric: str, date_str: str = None) -> str:
    """周同比"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    last_week_date = target_date - timedelta(days=7)
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.set_index("date")
    if target_date not in df.index or last_week_date not in df.index:
        return f"数据缺失"
    current = df.loc[target_date, metric]
    last_week = df.loc[last_week_date, metric]
    change = (current - last_week) / last_week * 100 if last_week != 0 else 0
    return f"{metric} 本周{target_date.strftime('%Y-%m-%d')}={current:.2f}, 上周同期={last_week:.2f}, 同比{change:+.1f}%"

def get_monthly_compare(metric: str, date_str: str = None) -> str:
    """月同比"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    if target_date.month == 1:
        last_month_date = target_date.replace(year=target_date.year-1, month=12, day=target_date.day)
    else:
        last_month_date = target_date.replace(month=target_date.month-1)
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.set_index("date")
    if target_date not in df.index or last_month_date not in df.index:
        return f"数据缺失"
    current = df.loc[target_date, metric]
    last_month = df.loc[last_month_date, metric]
    change = (current - last_month) / last_month * 100 if last_month != 0 else 0
    return f"{metric} 本月{target_date.strftime('%Y-%m-%d')}={current:.2f}, 上月同期={last_month:.2f}, 同比{change:+.1f}%"

def predict_next_week(metric: str) -> str:
    """线性回归预测下周均值"""
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.sort_values("date")
    if len(df) < 7:
        return "数据不足"
    train_df = df.tail(30)
    X = np.arange(len(train_df)).reshape(-1, 1)
    y = train_df[metric].values
    model = LinearRegression()
    model.fit(X, y)
    future_X = np.arange(len(train_df), len(train_df)+7).reshape(-1, 1)
    preds = model.predict(future_X)
    return f"预测下周{metric}日均值={np.mean(preds):.0f}"

def detect_anomaly_and_contribution(metric: str = "new_users", threshold: float = 0.15, date_str: str = None) -> str:
    """异常检测及渠道贡献度"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    target_date = pd.to_datetime(date_str)
    prev_date = target_date - timedelta(days=1)
    df_core = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df_core = df_core.set_index("date")
    if target_date not in df_core.index or prev_date not in df_core.index:
        return "数据缺失"
    current = df_core.loc[target_date, metric]
    prev = df_core.loc[prev_date, metric]
    change_pct = (current - prev) / prev if prev != 0 else 0
    if abs(change_pct) < threshold:
        return f"{metric}环比{change_pct:.1%} 无异常"
    # 渠道贡献分析（仅当metric为new_users）
    if metric == "new_users":
        try:
            df_ch = pd.read_csv("data/channel_data.csv", parse_dates=["date"])
            df_ch = df_ch[df_ch["date"].isin([target_date, prev_date])]
            channels = df_ch["channel"].unique()
            contrib = []
            for ch in channels:
                curr = df_ch[(df_ch["channel"]==ch)&(df_ch["date"]==target_date)]["new_users"].values
                pre = df_ch[(df_ch["channel"]==ch)&(df_ch["date"]==prev_date)]["new_users"].values
                if len(curr)>0 and len(pre)>0:
                    contrib.append((ch, curr[0]-pre[0]))
            contrib.sort(key=lambda x: abs(x[1]), reverse=True)
            res = f"⚠️ {metric}异常：环比{change_pct:+.1%}\n渠道贡献：\n"
            for ch, delta in contrib:
                res += f"  {ch}: {delta:+d}\n"
            return res
        except:
            return f"{metric}异常：环比{change_pct:+.1%}，渠道分析失败"
    else:
        return f"{metric}异常：环比{change_pct:+.1%}"