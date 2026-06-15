# 运营数据智能助手

> 基于 Flask + 智谱AI + Plotly + scikit-learn 的一站式产品运营分析平台。  
> 支持自然语言问答、自动化月报/周报生成、同比分析、趋势预测、异常归因及用户评论情感分析。

## 📌 项目背景

产品运营日常工作涉及大量数据查询、报表制作、异常监控和用户反馈分析。本项目的目标是**用 AI Agent 自动化上述流程**，运营人员只需通过聊天框提问，即可获得数据洞察、可视化报告以及行动建议，将原本数小时的工作缩短至数分钟。

## ✨ 核心功能

| 模块 | 能力 | 技术实现 |
|------|------|----------|
| **智能问答** | 自然语言查询 DAU、新增、留存、营收、渠道质量、用户反馈等 | 智谱AI (GLM-4-flash) + 上下文工程 |
| **交互式月报** | 动态图表展示核心指标趋势、渠道分析、活跃度分层、付费指标 | Plotly + pandas |
| **文字周报** | 结构化洞察文章：同比、预测、异常归因、行动建议 | scikit-learn 线性回归 + 正则解析 |
| **同比分析** | 自动计算周同比、月同比（需连续两个月数据） | pandas 时间偏移 |
| **趋势预测** | 基于最近30天数据线性回归，预测下周 DAU/营收 | scikit-learn LinearRegression |
| **异常检测与归因** | 识别新增用户异常波动，计算各渠道贡献度 | 环比阈值 + 渠道增量拆解 |
| **用户评论分析** | 情感分类（抱怨/建议/询问），输出统计摘要 | 智谱AI 提示词工程 |

## 🛠️ 技术栈

- **后端框架**：Flask
- **大模型**：智谱AI (GLM-4-flash) API
- **数据处理**：pandas, numpy
- **可视化**：plotly (交互式图表)
- **机器学习**：scikit-learn (线性回归预测)
- **Web 前端**：HTML, CSS, JavaScript (内嵌)

## 📦 安装与运行

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/运营数据洞察与自动化报告Agent.git
cd 运营数据洞察与自动化报告Agent
2. 安装依赖
创建虚拟环境（推荐）并安装依赖：

bash
pip install -r requirements.txt
requirements.txt 内容如下：

text
flask
pandas
plotly
scikit-learn
zhipuai
python-dotenv
3. 配置 API 密钥
在项目根目录创建 .env 文件，填入你的智谱AI API Key：

text
ZHIPUAI_API_KEY=你的真实密钥
获取地址：智谱AI开放平台 (注册后免费领取额度)

4. 生成模拟数据
运行以下脚本生成运营数据（约30天，包含渠道、活跃度、付费等）：

bash
python generate_mock_data.py      # 核心指标 DAU/新增/留存/营收
python generate_advanced_data.py  # 渠道数据、活跃度分层、付费指标
python sentiment_analyzer.py      # 用户评论情感分析（需先有 data/user_comments.csv）
如果缺少 user_comments.csv，可以手动创建或使用 generate_comments.py 生成示例数据（可向我索要）。

5. 生成图表月报
bash
python generate_web_report.py
运行后会在根目录生成 运营月报_高级版.html，包含全部 Plotly 图表。

6. 启动 Web 服务
bash
python web_app.py
终端会显示 Running on http://127.0.0.1:5000，并自动打开浏览器。若未自动打开，手动访问该地址即可。

🖥️ 使用指南
聊天问答示例
在页面底部的输入框输入问题，例如：

“昨天 DAU 是多少？”

“最近一周哪个渠道留存率最高？”

“本周 DAU 相比上月同期增长多少？”

“预测下周营收会是多少？”

“新增用户有没有异常？哪个渠道引起的？”

“用户有什么抱怨？”

月报区域
页面中间区域展示 运营月报_高级版.html，包含：

核心指标趋势图（DAU、新增、留存、营收）

渠道新增占比饼图、渠道质量对比柱状图

用户活跃度分层面积图

付费指标趋势图

右上角“刷新报告”按钮可重新加载 iframe。

文字周报区域
页面底部自动显示结构化文字周报，包含：

本周核心摘要（DAU/新增/营收及同比）

下周预测

用户反馈、渠道、活跃度、付费洞察

风险与机会分析

行动优先级建议

点击“刷新”可重新生成。

📁 文件结构说明
text
.
├── agent.py                  # Agent 核心：run_agent() 问答 + generate_text_weekly_report() 文字周报
├── tools.py                  # 工具函数：数据查询、同比、预测、异常归因、评论统计
├── web_app.py                # Flask 主程序，整合前端界面和路由
├── generate_mock_data.py     # 生成模拟核心指标数据 (mock_data.csv)
├── generate_advanced_data.py # 生成渠道、活跃度、付费数据 (channel_data.csv, activity_data.csv, pay_metrics.csv)
├── generate_web_report.py    # 生成 Plotly 月报 HTML 文件
├── sentiment_analyzer.py     # 用户评论情感分析脚本，生成 labeled CSV
├── requirements.txt          # Python 依赖
├── .env                      # API 密钥（不提交到 Git）
├── data/                     # 数据文件夹（运行脚本后自动生成）
│   ├── mock_data.csv
│   ├── channel_data.csv
│   ├── activity_data.csv
│   ├── pay_metrics.csv
│   └── user_comments_labeled.csv
├── 运营月报_高级版.html        # 生成的月报文件（不提交 Git）
└── README.md                 # 本文件
❓ 常见问题
1. 启动后网页空白或图表不显示？
检查终端是否有错误输出（如端口冲突、API Key 无效）。

确认已运行 generate_web_report.py 生成了 运营月报_高级版.html。

尝试更换浏览器（推荐 Chrome/Edge），或清除缓存。

2. 同比数据显示“数据缺失”
原因：mock_data.csv 中没有上月同一天的数据。
解决：运行 generate_mock_data.py 并修改其中天数参数（例如改为 60 天），生成更长的数据。

3. 预测或异常分析报错
确保已安装 scikit-learn：pip install scikit-learn。
确保 channel_data.csv 存在（运行 generate_advanced_data.py）。

4. 智谱AI API 调用失败
检查 .env 文件是否正确设置，API Key 是否有效。可在智谱AI控制台查看余额。

5. 如何停止服务？
在终端按 Ctrl+C，忽略可能出现的 Fortran 运行时错误提示（不影响）。

🚀 未来扩展计划
接入真实数据库（MySQL/PostgreSQL）替代 CSV

增加多轮对话记忆（LangChain memory）

支持更多指标（LTV、流失率、渠道 ROI）

部署到云端（阿里云/腾讯云）提供公网访问

定时自动生成周报并发送邮件/飞书

🤝 贡献
欢迎提交 Issue 和 Pull Request。如有疑问，请联系项目维护者。