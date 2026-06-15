# generate_web_report.py（月报增强版）
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

def load_data():
    base_path = "data/"
    df_core = pd.read_csv(os.path.join(base_path, "mock_data.csv"), parse_dates=["date"])
    df_channel = pd.read_csv(os.path.join(base_path, "channel_data.csv"), parse_dates=["date"])
    df_activity = pd.read_csv(os.path.join(base_path, "activity_data.csv"), parse_dates=["date"])
    df_pay = pd.read_csv(os.path.join(base_path, "pay_metrics.csv"), parse_dates=["date"])
    for df in [df_core, df_channel, df_activity, df_pay]:
        df.sort_values("date", inplace=True)
    return df_core, df_channel, df_activity, df_pay

def compute_monthly_summary(df_core):
    latest = df_core.iloc[-1]
    earliest = df_core.iloc[0]
    dau_growth = (latest['dau'] - earliest['dau']) / earliest['dau'] * 100
    revenue_growth = (latest['revenue_usd'] - earliest['revenue_usd']) / earliest['revenue_usd'] * 100
    avg_retention = df_core['retention_day1'].mean()
    total_revenue = df_core['revenue_usd'].sum()
    return {
        "月度总营收": f"${total_revenue:,.0f}",
        "平均留存率": f"{avg_retention:.1%}",
        "DAU 月增长率": f"{dau_growth:+.1f}%",
        "营收月增长率": f"{revenue_growth:+.1f}%",
        "最高 DAU": f"{df_core['dau'].max():,}",
        "日均新增": f"{df_core['new_users'].mean():,.0f}"
    }

def apply_fancy_layout(fig, title):
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, family='Segoe UI', color='#2c3e50')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Segoe UI', size=12, color='#2c3e50'),
        hoverlabel=dict(bgcolor='white', font_size=12),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

def plot_core_trends(df_core):
    fig = make_subplots(rows=2, cols=2, subplot_titles=("DAU", "新增用户", "次日留存率", "营收(USD)"))
    fig.add_trace(go.Scatter(x=df_core['date'], y=df_core['dau'], mode='lines+markers', name='DAU', line=dict(width=2, color='#3498db'), marker=dict(size=4)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_core['date'], y=df_core['new_users'], mode='lines+markers', name='新增', line=dict(width=2, color='#e67e22'), marker=dict(size=4)), row=1, col=2)
    fig.add_trace(go.Scatter(x=df_core['date'], y=df_core['retention_day1'], mode='lines+markers', name='留存率', line=dict(width=2, color='#2ecc71'), marker=dict(size=4)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_core['date'], y=df_core['revenue_usd'], mode='lines+markers', name='营收', line=dict(width=2, color='#9b59b6'), marker=dict(size=4)), row=2, col=2)
    fig.update_yaxes(tickformat=".0f", row=1, col=1)
    fig.update_yaxes(tickformat=".0f", row=1, col=2)
    fig.update_yaxes(tickformat=".1%", row=2, col=1)
    fig.update_yaxes(tickformat="$.0f", row=2, col=2)
    apply_fancy_layout(fig, "核心运营指标趋势 (月度)")
    return fig

def plot_channel_pie(df_channel):
    last_week = df_channel['date'].max() - timedelta(days=7)
    recent = df_channel[df_channel['date'] >= last_week]
    channel_new = recent.groupby('channel')['new_users'].sum().reset_index()
    fig = px.pie(channel_new, values='new_users', names='channel', title="最近一周各渠道新增占比", hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    apply_fancy_layout(fig, "")
    return fig

def plot_channel_performance(df_channel):
    latest_date = df_channel['date'].max()
    latest = df_channel[df_channel['date'] == latest_date]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("次日留存率", "LTV (USD)"))
    fig.add_trace(go.Bar(x=latest['channel'], y=latest['retention_day1'], name='留存率', marker_color='#f39c12', text=latest['retention_day1'].apply(lambda x: f"{x:.1%}"), textposition='outside'), row=1, col=1)
    fig.add_trace(go.Bar(x=latest['channel'], y=latest['ltv_usd'], name='LTV', marker_color='#1abc9c', text=latest['ltv_usd'], textposition='outside'), row=1, col=2)
    fig.update_yaxes(tickformat=".1%", row=1, col=1)
    fig.update_yaxes(tickformat="$.1f", row=1, col=2)
    apply_fancy_layout(fig, f"各渠道质量对比 ({latest_date.strftime('%Y-%m-%d')})")
    return fig

def plot_activity_trend(df_activity):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_activity['date'], y=df_activity['high_active_ratio'], name='高活跃', stackgroup='one', fill='tonexty', line=dict(color='#27ae60')))
    fig.add_trace(go.Scatter(x=df_activity['date'], y=df_activity['mid_active_ratio'], name='中活跃', stackgroup='one', line=dict(color='#f1c40f')))
    fig.add_trace(go.Scatter(x=df_activity['date'], y=df_activity['low_active_ratio'], name='低活跃', stackgroup='one', line=dict(color='#e67e22')))
    apply_fancy_layout(fig, "用户活跃度分层趋势")
    fig.update_yaxes(tickformat=".0%")
    return fig

def plot_pay_trends(df_pay):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("付费率", "ARPU & ARPPU"))
    fig.add_trace(go.Scatter(x=df_pay['date'], y=df_pay['pay_rate'], mode='lines+markers', name='付费率', line=dict(color='#e74c3c')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_pay['date'], y=df_pay['arpu_usd'], mode='lines+markers', name='ARPU', line=dict(color='#3498db')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_pay['date'], y=df_pay['arppu_usd'], mode='lines+markers', name='ARPPU', line=dict(color='#9b59b6')), row=2, col=1)
    fig.update_yaxes(tickformat=".1%", row=1, col=1)
    fig.update_yaxes(tickformat="$.2f", row=2, col=1)
    apply_fancy_layout(fig, "付费指标月度趋势")
    return fig

def generate_html_report():
    print("正在读取数据...")
    df_core, df_channel, df_activity, df_pay = load_data()
    summary = compute_monthly_summary(df_core)
    print("绘制图表...")
    figs = {
        "核心指标趋势": plot_core_trends(df_core),
        "渠道新增占比": plot_channel_pie(df_channel),
        "渠道质量对比": plot_channel_performance(df_channel),
        "用户活跃度分层": plot_activity_trend(df_activity),
        "付费指标趋势": plot_pay_trends(df_pay)
    }
    
    # 生成带切换按钮的HTML
    summary_html = "<div style='display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;'>"
    for k, v in summary.items():
        summary_html += f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 20px; min-width: 150px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.1);'><h3>{k}</h3><p style='font-size: 24px; margin: 10px 0;'>{v}</p></div>"
    summary_html += "</div>"
    
    chart_html = ""
    for i, (title, fig) in enumerate(figs.items()):
        chart_id = f"chart_{i}"
        btn_id = f"btn_{i}"
        chart_div = fig.to_html(full_html=False, include_plotlyjs='cdn' if i==0 else False)
        chart_html += f"""
        <div class='chart-card' id='{chart_id}_container'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                <h2 style='margin:0; color:#2c3e50;'>{title}</h2>
                <button class='toggle-btn' data-target='{chart_id}' style='background: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px;'>👁️ 隐藏</button>
            </div>
            <div id='{chart_id}' class='chart-container'>{chart_div}</div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>运营月报 - 高级版</title>
        <style>
            body {{
                background: linear-gradient(135deg, #f5f7fa 0%, #e9edf2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            h1 {{
                text-align: center;
                font-size: 42px;
                background: linear-gradient(120deg, #2c3e50, #3498db);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                margin-bottom: 30px;
            }}
            .summary-section {{
                background: rgba(255,255,255,0.7);
                backdrop-filter: blur(10px);
                border-radius: 30px;
                padding: 30px;
                margin-bottom: 40px;
                box-shadow: 0 20px 35px rgba(0,0,0,0.1);
            }}
            .chart-card {{
                background: white;
                border-radius: 24px;
                padding: 20px;
                margin-bottom: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                transition: transform 0.2s;
            }}
            .chart-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }}
            .toggle-btn {{
                transition: background 0.2s;
            }}
            .toggle-btn:hover {{
                background: #2980b9;
            }}
            footer {{
                text-align: center;
                margin-top: 50px;
                color: #7f8c8d;
                font-size: 14px;
            }}
            @media (max-width: 768px) {{
                .summary-section div {{
                    flex-direction: column;
                    align-items: center;
                }}
            }}
        </style>
        <script>
            // 为每个图表添加切换功能
            document.addEventListener('DOMContentLoaded', function() {{
                const btns = document.querySelectorAll('.toggle-btn');
                btns.forEach(btn => {{
                    btn.addEventListener('click', function() {{
                        const targetId = this.getAttribute('data-target');
                        const chartDiv = document.getElementById(targetId);
                        if (chartDiv.style.display === 'none') {{
                            chartDiv.style.display = 'block';
                            this.innerHTML = '👁️ 隐藏';
                        }} else {{
                            chartDiv.style.display = 'none';
                            this.innerHTML = '🔍 打开';
                        }}
                    }});
                }});
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <h1>📊 产品运营月度报告</h1>
            <div class="summary-section">
                <h2 style="text-align:center; margin-top:0;">📌 月度关键指标</h2>
                {summary_html}
            </div>
            {chart_html}
            <footer>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据基于最近30天模拟数据 | 点击按钮可隐藏/打开图表</footer>
        </div>
    </body>
    </html>
    """
    output_file = "运营月报_高级版.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 高级月报已生成：{output_file}")

if __name__ == "__main__":
    generate_html_report()