# generate_weekly_report.py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

def load_weekly_data():
    df_core = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df_core = df_core.sort_values("date")
    # 取最近7天
    last_date = df_core['date'].max()
    start_date = last_date - timedelta(days=6)
    df_week = df_core[df_core['date'] >= start_date].copy()
    return df_week

def compute_weekly_summary(df_week):
    dau_trend = (df_week['dau'].iloc[-1] - df_week['dau'].iloc[0]) / df_week['dau'].iloc[0] * 100
    revenue_trend = (df_week['revenue_usd'].iloc[-1] - df_week['revenue_usd'].iloc[0]) / df_week['revenue_usd'].iloc[0] * 100
    return {
        "本周DAU峰值": f"{df_week['dau'].max():,}",
        "本周DAU均值": f"{df_week['dau'].mean():,.0f}",
        "DAU周增长率": f"{dau_trend:+.1f}%",
        "营收周增长率": f"{revenue_trend:+.1f}%",
        "平均留存率": f"{df_week['retention_day1'].mean():.1%}"
    }

def plot_weekly_trends(df_week):
    fig = make_subplots(rows=2, cols=2, subplot_titles=("DAU (周趋势)", "新增用户", "留存率", "营收"))
    fig.add_trace(go.Scatter(x=df_week['date'], y=df_week['dau'], mode='lines+markers', name='DAU', line=dict(width=3, color='#e74c3c', shape='spline'), marker=dict(size=10, symbol='circle')), row=1, col=1)
    fig.add_trace(go.Bar(x=df_week['date'], y=df_week['new_users'], name='新增', marker_color='#f39c12'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df_week['date'], y=df_week['retention_day1'], mode='lines+markers', name='留存率', line=dict(width=3, dash='dot')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_week['date'], y=df_week['revenue_usd'], mode='lines+markers', name='营收', line=dict(width=3, color='#9b59b6')), row=2, col=2)
    fig.update_layout(title="📈 本周核心指标花哨趋势", title_font_size=24, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Comic Sans MS', size=12))
    fig.update_xaxes(showgrid=True, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridcolor='lightgrey')
    return fig

def generate_weekly_report():
    df_week = load_weekly_data()
    summary = compute_weekly_summary(df_week)
    fig = plot_weekly_trends(df_week)
    
    summary_html = "<div style='display: flex; gap: 20px; flex-wrap: wrap;'>"
    for k, v in summary.items():
        summary_html += f"<div style='background: linear-gradient(145deg, #ff9a9e, #fad0c4); padding: 15px 25px; border-radius: 40px; box-shadow: 0 8px 20px rgba(0,0,0,0.1);'><strong>{k}</strong><br><span style='font-size: 28px;'>{v}</span></div>"
    summary_html += "</div>"
    
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>运营周报 - 花哨版</title>
    <style>
        body {{ background: radial-gradient(circle at 10% 30%, #fbc2eb, #a6c1ee); font-family: 'Segoe UI', cursive; padding: 30px; }}
        h1 {{ text-align: center; font-size: 48px; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
        .card {{ background: rgba(255,255,255,0.85); border-radius: 50px; padding: 25px; margin: 20px auto; max-width: 1200px; backdrop-filter: blur(5px); }}
        .summary {{ text-align: center; margin: 30px 0; }}
        .btn-group {{ text-align: center; margin: 20px; }}
        button {{ background: white; border: none; padding: 10px 30px; border-radius: 40px; font-size: 18px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: 0.2s; }}
        button:hover {{ transform: scale(1.05); background: #f0f0f0; }}
    </style>
    <script>
        function showChart() {{
            document.getElementById('chartContainer').style.display = 'block';
        }}
        function hideChart() {{
            document.getElementById('chartContainer').style.display = 'none';
        }}
    </script>
    </head>
    <body>
        <h1>🌟 运营周报 · 炫彩版 🌟</h1>
        <div class="card">
            <div class="summary">{summary_html}</div>
            <div class="btn-group">
                <button onclick="showChart()">📊 打开图表</button>
                <button onclick="hideChart()">❌ 隐藏图表</button>
            </div>
            <div id="chartContainer" style="display: block;">{chart_html}</div>
        </div>
        <div style="text-align:center; color:white;">报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </body>
    </html>
    """
    with open("运营周报_花哨版.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ 花哨周报已生成：运营周报_花哨版.html")

if __name__ == "__main__":
    generate_weekly_report()