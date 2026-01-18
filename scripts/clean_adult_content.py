#!/usr/bin/env python3
"""
清理书源中含有18禁内容的源
"""

import json
import re
from pathlib import Path

# 18禁关键词列表
ADULT_KEYWORDS = [
    # 明确的18禁标识
    '18', 'PO18', 'Woo18', '成人', '18禁',

    # 色情相关
    '色', '情', '欲', '淫', '艳', '春', '宫', '房', '床',
    '激情', '诱惑', '魅惑', '撩人', '风骚', '妖娆', '勾魂', '销魂',
    '荡', '浪', '媚', '骚', '辣文', '肉色', '色欲', '污',

    # 成人服务相关
    '小姐', '鸡', '妓', '嫖', '娼',

    # 明显的性暗示
    '操', '干', '插', '射', '爽', '舔', '吸', '摸', '抚', '揉', '搓',
    '挺', '硬', '湿', '紧', '粉嫩', '鲍',

    # 黄色内容
    '黄', '黄色', '污漫', '肉漫',

    # 腐向内容（BL相关，但保留一些正常的）
    '腐小说', '腐文', '耽美'
]

# 需要特殊处理的完整名称（避免误删）
EXACT_MATCHES = [
    '18mh',
    'PO18文学', 'PO18site', 'PO18完本', 'po18分站',
    '欲望社', '每日色漫', '红尘黄色', '色文网吧',
    '66成人小说', 'Woo18小说', '中文成人文学',
    '丽图·污漫画', '优质粉嫩鲍', '淫淫小说可以漫画',
    '肉色漫画', '色欲文', '欲书台'
]

def contains_adult_content(name: str) -> bool:
    """检查书源名称是否含有18禁内容"""
    name_lower = name.lower()

    # 检查完全匹配
    if name in EXACT_MATCHES:
        return True

    # 检查关键词
    for keyword in ADULT_KEYWORDS:
        if keyword in name:
            # 特殊处理：避免误删正常的书源
            if keyword == '色' and ('色彩' in name or '特色' in name or '本色' in name):
                continue
            if keyword == '情' and ('情节' in name or '剧情' in name or '情怀' in name):
                continue
            if keyword == '春' and ('春秋' in name or '青春' in name):
                continue
            if keyword == '房' and ('书房' in name or '房间' in name):
                continue
            if keyword == '小姐' and '小姐姐' in name:
                continue

            return True

    return False

def clean_adult_sources(input_file: Path, output_file: Path = None) -> tuple[int, int, list]:
    """清理含有18禁内容的书源"""
    if output_file is None:
        output_file = input_file

    # 读取书源文件
    with open(input_file, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    original_count = len(sources)
    removed_sources = []

    # 过滤含有18禁内容的书源
    clean_sources = []
    for source in sources:
        name = source.get('bookSourceName', '')
        if contains_adult_content(name):
            removed_sources.append({
                'name': name,
                'url': source.get('bookSourceUrl', ''),
                'reason': '含有18禁内容'
            })
        else:
            clean_sources.append(source)

    # 保存清理后的书源
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_sources, f, ensure_ascii=False, indent=2)

    final_count = len(clean_sources)
    removed_count = original_count - final_count

    return original_count, final_count, removed_sources

def main():
    """主函数"""
    input_file = Path('sources/legado/full.json')
    backup_file = Path('sources/legado/full_before_adult_clean.json')

    if not input_file.exists():
        print(f"错误：找不到文件 {input_file}")
        return

    # 创建备份
    import shutil
    shutil.copy2(input_file, backup_file)
    print(f"已创建备份：{backup_file}")

    # 清理18禁内容
    original_count, final_count, removed_sources = clean_adult_sources(input_file)

    print(f"\n清理完成！")
    print(f"原始书源数量：{original_count}")
    print(f"清理后数量：{final_count}")
    print(f"移除数量：{len(removed_sources)}")

    if removed_sources:
        print(f"\n移除的书源：")
        for i, source in enumerate(removed_sources, 1):
            print(f"{i:2d}. {source['name']} - {source['url']}")

    # 保存移除记录
    removed_file = Path('sources/legado/removed_adult_sources.json')
    with open(removed_file, 'w', encoding='utf-8') as f:
        json.dump(removed_sources, f, ensure_ascii=False, indent=2)
    print(f"\n移除记录已保存到：{removed_file}")

if __name__ == '__main__':
    main()