import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from tools import query_dau, query_new_users, query_retention, query_revenue, get_comment_summary

load_dotenv()
client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
console = Console()

# ==================== 数据准备函数 ====================
def get_last_n_days_data(n=7):
    df = pd.read_csv("data/mock_data.csv", parse_dates=["date"])
    df = df.sort_values("date", ascending=False).head(n)
    return df

def build_data_context():
    """收集所有相关数据，构建一个详细的文本上下文供大模型参考"""
    context = ""
    
    # 1. 最近7天数据表格
    df = get_last_n_days_data(7)
    if not df.empty:
        context += "📊 最近7天核心运营数据（日期｜DAU｜新增用户｜次日留存率｜营收USD）：\n"
        for _, row in df.iterrows():
            context += f"- {row['date'].strftime('%Y-%m-%d')}: DAU {row['dau']:,}, 新增 {row['new_users']:,}, 留存率 {row['retention_day1']:.1%}, 营收 ${row['revenue_usd']:,.0f}\n"
    else:
        context += "无运营数据。\n"
    
    # 2. 昨天和前天对比（用于环比）
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    day_before = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    try:
        dau_y = query_dau(yesterday)
        dau_db = query_dau(day_before)
        new_y = query_new_users(yesterday)
        new_db = query_new_users(day_before)
        retention_y = query_retention(yesterday)
        retention_db = query_retention(day_before)
        rev_y = query_revenue(yesterday)
        rev_db = query_revenue(day_before)
        
        context += f"\n📈 关键指标环比（昨日 vs 前日）：\n"
        context += f"- DAU: {dau_y} vs {dau_db} (变化 {dau_y-dau_db:+.0f})\n"
        context += f"- 新增用户: {new_y} vs {new_db} (变化 {new_y-new_db:+.0f})\n"
        context += f"- 次日留存率: {retention_y:.1%} vs {retention_db:.1%}\n"
        context += f"- 营收: ${rev_y:,.0f} vs ${rev_db:,.0f}\n"
    except:
        context += "\n⚠️ 无法获取环比数据。\n"
    
    # 3. 用户评论统计
    comment_summary = get_comment_summary()
    context += f"\n💬 用户反馈统计：{comment_summary}\n"
        # 添加同比分析、预测、异常监控
    from tools import get_weekly_compare, get_monthly_compare, predict_next_week, detect_anomaly_and_contribution
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    context += f"\n📅 同比分析（基于 {yesterday}）：\n"
    for metric in ['dau', 'new_users', 'revenue_usd']:
        context += f"- {get_weekly_compare(metric, yesterday)}\n"
        context += f"- {get_monthly_compare(metric, yesterday)}\n"
    
    context += f"\n🔮 趋势预测：\n"
    context += f"- {predict_next_week('dau')}\n"
    context += f"- {predict_next_week('revenue_usd')}\n"
    
    context += f"\n🚨 异常监控与归因（新增用户）：\n"
    context += detect_anomaly_and_contribution(metric="new_users", threshold=0.15)
        # 添加同比、预测、异常归因
    from tools import get_weekly_compare, get_monthly_compare, predict_next_week, detect_anomaly_and_contribution
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    context += f"\n📅 同比分析（{yesterday}）：\n"
    for m in ['dau', 'new_users', 'revenue_usd']:
        context += f"- {get_weekly_compare(m, yesterday)}\n"
        context += f"- {get_monthly_compare(m, yesterday)}\n"
    context += f"\n🔮 趋势预测：\n"
    context += f"- {predict_next_week('dau')}\n"
    context += f"- {predict_next_week('revenue_usd')}\n"
    context += f"\n🚨 异常归因（新增用户）：\n{detect_anomaly_and_contribution('new_users', 0.15)}\n"
    return context


def print_weekly_report():
    console.print(Panel.fit("📊 运营数据周报", style="bold cyan", border_style="cyan"))
    data_df = get_last_n_days_data(7)
    if data_df.empty:
        console.print("[red]无数据[/red]")
        return
    
    # 核心指标表格
    table = Table(title="核心指标（最近7天）", style="bright_blue", header_style="bold magenta")
    table.add_column("日期", style="cyan")
    table.add_column("DAU", justify="right")
    table.add_column("新增", justify="right")
    table.add_column("留存率", justify="right")
    table.add_column("营收(USD)", justify="right", style="yellow")
    for _, row in data_df.iterrows():
        table.add_row(
            row['date'].strftime("%m-%d"),
            f"{row['dau']:,}",
            f"{row['new_users']:,}",
            f"{row['retention_day1']:.1%}",
            f"${row['revenue_usd']:,.0f}"
        )
    console.print(table)
    
    # 最近一天渠道数据
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        from tools import get_channel_summary, get_activity_summary, get_pay_summary
        console.print(Panel(get_channel_summary(yesterday), title=f"📢 渠道来源 ({yesterday})", border_style="green"))
        console.print(Panel(get_activity_summary(yesterday), title="📱 用户活跃度分层", border_style="yellow"))
        console.print(Panel(get_pay_summary(yesterday), title="💰 付费指标", border_style="magenta"))
    except:
        pass
    
    comment_summary = get_comment_summary()
    console.print(Panel(comment_summary, title="💬 用户反馈", border_style="bright_yellow"))
    console.print("✨ 周报生成完毕，进入智能问答模式 ✨", style="bold purple")
# ==================== 问答核心（稳定版）====================
def run_agent(user_question: str) -> str:
    # 构建包含同比、预测、异常归因的完整数据上下文
    data_context = build_data_context()
    
    # 系统提示词（强化要求使用上下文中的高级分析）
    system_prompt = """你是一个专业的产品运营数据分析助手。下面提供了详细的运营数据，包括：
- 最近7天核心指标
- 渠道来源、用户活跃度分层、付费指标
- 用户评论统计
- **同比分析**（本周 vs 上周同期、本月 vs 上月同期）
- **趋势预测**（基于线性回归的下周DAU/营收预测）
- **异常监控与归因**（新增用户异常波动时，各渠道的贡献度）

请严格根据这些数据回答用户的问题。如果用户问及同比、预测、异常归因，请直接引用数据中的相关结论。回答要简洁、专业、有洞察，不要编造不存在的数字。
"""
    
    user_prompt = f"用户问题：{user_question}\n\n当前运营数据上下文：\n{data_context}\n\n请回答："
    
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，调用大模型时出错：{e}。请稍后重试。"


# ==================== 主入口 ====================
if __name__ == "__main__":
    # 如果希望启动时先打印周报（可选），取消下面一行的注释
    # print_weekly_report()
    print("\n🤖 运营智能助手已启动（输入 quit 退出）\n")
    while True:
        q = input("你的问题：")
        if q.lower() == "quit":
            break
        answer = run_agent(q)
        print(f"\n📌 {answer}\n")

def build_data_context():
    context = ""
    # 原有最近7天核心数据
    df = get_last_n_days_data(7)
    if not df.empty:
        context += "📊 最近7天核心运营数据（日期｜DAU｜新增用户｜次日留存率｜营收USD）：\n"
        for _, row in df.iterrows():
            context += f"- {row['date'].strftime('%Y-%m-%d')}: DAU {row['dau']:,}, 新增 {row['new_users']:,}, 留存率 {row['retention_day1']:.1%}, 营收 ${row['revenue_usd']:,.0f}\n"
    
    # 新增：渠道数据摘要（昨天各渠道新增与留存）
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    context += f"\n📢 渠道来源分析（{yesterday}）：\n"
    try:
        from tools import get_channel_summary
        context += get_channel_summary(yesterday) + "\n"
    except:
        context += "渠道数据暂不可用\n"
    
    # 新增：用户活跃度分层
    context += f"\n📱 用户活跃度分层（{yesterday}）：\n"
    try:
        from tools import get_activity_summary
        context += get_activity_summary(yesterday) + "\n"
    except:
        context += "活跃度数据暂不可用\n"
    
    # 新增：付费指标
    context += f"\n💰 付费指标（{yesterday}）：\n"
    try:
        from tools import get_pay_summary
        context += get_pay_summary(yesterday) + "\n"
    except:
        context += "付费数据暂不可用\n"
    
    # 原有评论统计
    comment_summary = get_comment_summary()
    context += f"\n💬 用户反馈统计：{comment_summary}\n"
    
    return context        

def generate_text_weekly_report() -> str:
    """生成文章形式的运营洞察周报（HTML）"""
    from tools import (
        get_weekly_compare, get_monthly_compare, predict_next_week,
        detect_anomaly_and_contribution, get_comment_summary,
        get_channel_summary, get_activity_summary, get_pay_summary
    )
    from datetime import datetime, timedelta
    import pandas as pd
    import re

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 辅助函数：提取数值和百分比
    def extract_val_and_pct(metric, compare_func, date_str):
        res = compare_func(metric, date_str)
        # 分割后提取数值
        parts = res.split(',')
        first_part = parts[0]
        val_match = re.search(r'=([\d.]+)', first_part)
        val = val_match.group(1) if val_match else '0'
        pct_match = re.search(r'([+-][\d.]+)%', res)
        pct = pct_match.group(1) if pct_match else '0'
        return val, pct

    dau_val, dau_weekly = extract_val_and_pct('dau', get_weekly_compare, yesterday)
    dau_monthly = extract_val_and_pct('dau', get_monthly_compare, yesterday)[1]
    new_val, new_weekly = extract_val_and_pct('new_users', get_weekly_compare, yesterday)
    rev_val, rev_weekly = extract_val_and_pct('revenue_usd', get_weekly_compare, yesterday)

    # 预测
    dau_pred = predict_next_week('dau')
    rev_pred = predict_next_week('revenue_usd')
    pred_dau = re.search(r'(\d+)', dau_pred).group(1) if re.search(r'(\d+)', dau_pred) else '?'
    pred_rev = re.search(r'(\d+)', rev_pred).group(1) if re.search(r'(\d+)', rev_pred) else '?'

    # 用户反馈摘要
    comment_summary = get_comment_summary()

    # 渠道、活跃度、付费摘要
    channel_info = get_channel_summary(yesterday)
    activity_info = get_activity_summary(yesterday)
    pay_info = get_pay_summary(yesterday)

    # 异常归因
    anomaly_info = detect_anomaly_and_contribution('new_users', 0.15)

    # 找出最佳和最差渠道（基于最近一周平均留存率）
    try:
        df_ch = pd.read_csv("data/channel_data.csv", parse_dates=["date"])
        last_week = df_ch['date'].max() - timedelta(days=7)
        recent = df_ch[df_ch['date'] >= last_week]
        channel_ret = recent.groupby('channel')['retention_day1'].mean().sort_values(ascending=False)
        best_channel = channel_ret.index[0] if len(channel_ret) > 0 else "推荐裂变"
        worst_channel = channel_ret.index[-1] if len(channel_ret) > 0 else "广告投放"
    except:
        best_channel = "推荐裂变"
        worst_channel = "广告投放"

    # 解析评论统计中的数字（用于建议）
    complain_cnt = 0
    import re as regex
    match_complain = regex.search(r'抱怨\s+(\d+)', comment_summary)
    if match_complain:
        complain_cnt = int(match_complain.group(1))

    # 构建 HTML 文章（注意：避免在 f-string 内使用反斜杠，所有正则已经提前定义）
    html = f"""
    <style>
        .insight-article {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #1e2a3e;
            max-width: 100%;
            margin: 0;
        }}
        .article-header {{
            border-bottom: 3px solid #3498db;
            margin-bottom: 20px;
            padding-bottom: 8px;
        }}
        .article-header h2 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .article-header .date {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 4px;
        }}
        .summary-callout {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 5px solid #3498db;
            padding: 16px 20px;
            border-radius: 16px;
            margin: 20px 0;
            font-weight: 500;
        }}
        .metrics-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin: 24px 0;
        }}
        .metric-card {{
            flex: 1;
            background: white;
            border-radius: 20px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #eef2f5;
        }}
        .metric-title {{
            font-size: 13px;
            text-transform: uppercase;
            color: #5a6e7c;
            letter-spacing: 0.5px;
        }}
        .metric-number {{
            font-size: 28px;
            font-weight: 700;
            margin: 8px 0 4px;
            color: #1e2a3e;
        }}
        .metric-trend {{
            font-size: 13px;
        }}
        .trend-up {{ color: #10b981; }}
        .trend-down {{ color: #ef4444; }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin: 28px 0 12px 0;
            padding-left: 12px;
            border-left: 4px solid #3498db;
        }}
        .insight-box {{
            background: #f8fafc;
            border-radius: 20px;
            padding: 16px 20px;
            margin: 16px 0;
        }}
        .action-list {{
            list-style: none;
            padding-left: 0;
        }}
        .action-list li {{
            margin-bottom: 12px;
            padding-left: 24px;
            position: relative;
        }}
        .action-list li::before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #3498db;
            font-weight: bold;
        }}
        .highlight {{
            background: #fef9e3;
            padding: 2px 6px;
            border-radius: 12px;
            font-weight: 500;
        }}
        hr {{
            margin: 24px 0;
            border: none;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
    <div class="insight-article">
        <div class="article-header">
            <h2>📈 产品运营洞察周报</h2>
            <div class="date">数据截止 {yesterday} · 生成时间 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>

        <div class="summary-callout">
            📌 本周核心表现：DAU {dau_val}（周同比 {dau_weekly}%），新增 {new_val}（{new_weekly}%），营收 ${int(float(rev_val)):,}（{rev_weekly}%）。<br>
            用户反馈统计：{comment_summary}。下周预测 DAU 将达 {pred_dau}，营收 ${int(float(pred_rev)):,}。
        </div>

        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-title">日活用户 (DAU)</div>
                <div class="metric-number">{dau_val}</div>
                <div class="metric-trend">
                    周同比 <span class="{'trend-up' if dau_weekly[0]!='-' else 'trend-down'}">{dau_weekly}%</span>
                     · 月同比 <span class="{'trend-up' if dau_monthly[0]!='-' else 'trend-down'}">{dau_monthly}%</span>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">新增用户</div>
                <div class="metric-number">{new_val}</div>
                <div class="metric-trend">
                    周同比 <span class="{'trend-up' if new_weekly[0]!='-' else 'trend-down'}">{new_weekly}%</span>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">营收 (USD)</div>
                <div class="metric-number">${int(float(rev_val)):,}</div>
                <div class="metric-trend">
                    周同比 <span class="{'trend-up' if rev_weekly[0]!='-' else 'trend-down'}">{rev_weekly}%</span>
                </div>
            </div>
        </div>

        <div class="section-title">📢 用户声音与渠道洞察</div>
        <div class="insight-box">
            <strong>🗣️ 用户反馈统计</strong><br>
            {comment_summary}<br><br>
            <strong>📢 渠道质量</strong><br>
            {channel_info}<br><br>
            <strong>📱 用户活跃度分层</strong><br>
            {activity_info}<br><br>
            <strong>💰 付费指标</strong><br>
            {pay_info}
        </div>

        <div class="section-title">⚠️ 风险与机会</div>
        <div class="insight-box">
            <strong>异常监控</strong><br>
            {anomaly_info}<br><br>
            <strong>渠道表现</strong><br>
            • 留存最佳渠道：<span class="highlight">{best_channel}</span>，建议加大该渠道预算。<br>
            • 留存待优化渠道：<span class="highlight">{worst_channel}</span>，需排查素材或承接问题。<br>
            • 下周预测 DAU 增长至 {pred_dau}，建议提前评估服务器压力。
        </div>

        <div class="section-title">📌 行动优先级建议</div>
        <ul class="action-list">
            <li>针对新增用户周同比 {new_weekly}% 的变化，<strong>{'保持拉新策略，适当放量' if new_weekly[0]!='-' else '暂停低效渠道，优化素材'}</strong>。</li>
            <li>用户反馈中{'抱怨占比较高，优先处理闪退/卡顿问题' if complain_cnt > 3 else '建议类较多，可组织需求评审会'}。</li>
            <li><strong>{best_channel}</strong> 渠道留存率最高，建议增加预算分配；<strong>{worst_channel}</strong> 渠道需 A/B 测试新落地页。</li>
            <li>预测下周 DAU 将达 {pred_dau}，建议提前扩容服务器，避免高峰期拥堵。</li>
            <li>营收增长趋势良好，可尝试针对高价值用户推送限时折扣，拉升 ARPU。</li>
        </ul>
        <hr>
        <div style="font-size:12px; color:#94a3b8; text-align:center;">本报告由运营数据智能助手自动生成，数据基于最近30天模拟数据。</div>
    </div>
    """
    return html