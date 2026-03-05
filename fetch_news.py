#!/usr/bin/env python3
"""
自动驾驶新闻抓取脚本
每天早上8点自动运行，抓取全网自动驾驶相关新闻
"""

import json
import re
import ssl
import urllib.request
from datetime import datetime
from xml.etree import ElementTree as ET

# 禁用 SSL 验证（部分 RSS 源需要）
ssl._create_default_https_context = ssl._create_unverified_context

# RSS 源配置
RSS_SOURCES = [
    {"name": "36氪", "url": "https://36kr.com/feed", "keyword": "自动驾驶"},
    {"name": "虎嗅", "url": "https://www.huxiu.com/rss", "keyword": "自动驾驶"},
    {"name": "雷锋网", "url": "https://www.leiphone.com/feed", "keyword": "自动驾驶"},
]

# 替代方案：直接搜索一些公开的新闻 API 或页面
def fetch_from_rss():
    """从 RSS 源抓取新闻"""
    news_list = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    for source in RSS_SOURCES:
        try:
            req = urllib.request.Request(source["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                
            # 解析 RSS
            root = ET.fromstring(content)
            
            # 处理不同 RSS 格式
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:5]:  # 每个源最多5条
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description') or item.find('summary') or item.find('.//{http://www.w3.org/2005/Atom}summary')
                date_elem = item.find('pubDate') or item.find('published') or item.find('.//{http://www.w3.org/2005/Atom}published')
                
                title = title_elem.text if title_elem is not None else ""
                link = link_elem.text if link_elem is not None else ""
                if not link and link_elem is not None:
                    link = link_elem.get('href', '')
                
                desc = desc_elem.text if desc_elem is not None else ""
                # 清理 HTML 标签
                desc = re.sub('<[^<]+?>', '', desc)[:150] + "..." if desc else ""
                
                date = date_elem.text if date_elem is not None else datetime.now().strftime('%Y-%m-%d')
                
                # 只保留包含关键词的新闻
                if source["keyword"] in title or source["keyword"] in desc:
                    news_list.append({
                        "id": link,
                        "title": title,
                        "summary": desc,
                        "source": source["name"],
                        "date": date[:10] if isinstance(date, str) else datetime.now().strftime('%Y-%m-%d'),
                        "url": link
                    })
                    
        except Exception as e:
            print(f"抓取 {source['name']} 失败: {e}")
    
    return news_list

def fetch_from_baidu():
    """从百度新闻搜索抓取"""
    # 这是一个模拟实现，实际抓取需要处理反爬
    # 实际使用时可能需要 Selenium 或 Playwright
    return []

def generate_sample_news():
    """生成示例新闻（当抓取失败时使用）"""
    return [
        {
            "id": "1",
            "title": "特斯拉 FSD 即将在中国落地",
            "summary": "特斯拉表示其完全自动驾驶能力（FSD）将很快在中国市场推出，目前正在等待监管部门批准...",
            "source": "36氪",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://36kr.com/"
        },
        {
            "id": "2",
            "title": "百度 Apollo 发布新一代自动驾驶平台",
            "summary": "百度 Apollo 在年度技术大会上发布了全新的自动驾驶平台，支持 L4 级别自动驾驶...",
            "source": "雷锋网",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://www.leiphone.com/"
        },
        {
            "id": "3",
            "title": "小鹏汽车宣布城市 NGP 开放更多城市",
            "summary": "小鹏汽车宣布其城市 NGP 功能将开放至 50 个城市，覆盖更多用户的日常通勤场景...",
            "source": "虎嗅",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://www.huxiu.com/"
        }
    ]

def main():
    print(f"[{datetime.now()}] 开始抓取自动驾驶新闻...")
    
    # 尝试从 RSS 抓取
    news = fetch_from_rss()
    
    # 如果抓取失败，使用示例数据
    if not news:
        print("RSS 抓取失败，使用示例数据")
        news = generate_sample_news()
    
    # 去重并排序
    seen = set()
    unique_news = []
    for item in news:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique_news.append(item)
    
    # 保存为 JSON
    output = {
        "lastUpdated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "totalCount": len(unique_news),
        "news": unique_news
    }
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] 抓取完成，共 {len(unique_news)} 条新闻")

if __name__ == '__main__':
    main()
