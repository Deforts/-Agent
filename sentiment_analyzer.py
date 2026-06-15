import os
import pandas as pd
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))


def classify_comment(comment_text: str) -> dict:
    """
    调用大模型对单条评论进行分类
    返回: {"category": "抱怨" | "建议" | "询问", "reason": 简短理由}
    """
    prompt = f"""
你是一个用户反馈分析专家。请将以下用户评论分类为三类之一：
- 抱怨：用户表达不满、投诉、负面情绪
- 建议：用户提出改进意见、新功能请求
- 询问：用户提问、寻求帮助或信息

只输出 JSON 格式，不要有其他内容，例如：{{"category": "抱怨", "reason": "用户提到闪退"}}

评论内容：{comment_text}
"""
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        result = response.choices[0].message.content
        # 尝试解析 JSON（大模型可能输出带 markdown 代码块）
        import json
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.endswith("```"):
            result = result[:-3]
        data = json.loads(result)
        return data
    except Exception as e:
        print(f"分类失败: {e}, 原文: {comment_text}")
        return {"category": "未知", "reason": "解析失败"}


def analyze_comments(csv_path: str = "data/user_comments.csv", output_path: str = "data/user_comments_labeled.csv"):
    """
    读取评论 CSV，逐条分类，保存结果
    """
    df = pd.read_csv(csv_path)
    # 如果已经分类过且不想重复调用 API，可以检查输出文件是否存在
    if os.path.exists(output_path):
        print(f"输出文件已存在: {output_path}，跳过分析。如需重新分析，请删除该文件。")
        return

    categories = []
    reasons = []
    for idx, row in df.iterrows():
        print(f"正在处理第 {idx + 1}/{len(df)} 条评论...")
        res = classify_comment(row["comment_text"])
        categories.append(res.get("category", "未知"))
        reasons.append(res.get("reason", ""))

    df["category"] = categories
    df["reason"] = reasons
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"分析完成，结果已保存到 {output_path}")


def summary_statistics(labeled_csv: str = "data/user_comments_labeled.csv"):
    """
    统计各分类的数量和占比
    """
    df = pd.read_csv(labeled_csv)
    counts = df["category"].value_counts()
    print("\n===== 用户评论分类统计 =====")
    for cat, cnt in counts.items():
        print(f"{cat}: {cnt} 条 ({cnt / len(df) * 100:.1f}%)")
    return counts


if __name__ == "__main__":
    # 运行分析
    analyze_comments()
    # 输出统计结果
    summary_statistics()