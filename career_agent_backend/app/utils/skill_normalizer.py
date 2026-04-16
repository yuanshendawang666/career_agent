"""
技能名称标准化与模糊匹配工具模块

提供技能名称的规范化处理以及基于相似度的模糊匹配功能。
"""
import re
from difflib import SequenceMatcher
from typing import Optional

# 技能同义词映射表（可根据业务需求持续扩充）
# 键为原始输入中的常见写法，值为标准化的技能名称
SYNONYMS = {
    "python": "python",
    "py": "python",
    "java": "java",
    "j2ee": "java",
    "javascript": "javascript",
    "js": "javascript",
    "html": "html",
    "css": "css",
    "react": "react",
    "react.js": "react",
    "vue": "vue",
    "vue.js": "vue",
    "angular": "angular",
    "node": "node.js",
    "nodejs": "node.js",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "mongodb": "mongodb",
    "spring": "spring",
    "spring boot": "spring boot",
    "django": "django",
    "flask": "flask",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "data science": "data science",
    "deep learning": "deep learning",
    "dl": "deep learning",
}


def normalize_skill(skill: str) -> str:
    """
    标准化技能名称。

    处理流程：
        1. 去除首尾空格并转为小写。
        2. 若存在于同义词映射表中，则返回标准名称。
        3. 否则去除常见的中文后缀（如“开发”、“工程师”、“技术”），返回剩余部分。

    Args:
        skill (str): 原始技能名称。

    Returns:
        str: 标准化后的技能名称。
    """
    skill_lower = skill.lower().strip()

    # 检查同义词映射
    if skill_lower in SYNONYMS:
        return SYNONYMS[skill_lower]

    # 去除常见的中文后缀（如“Python开发” → “python”）
    skill_lower = re.sub(r"(开发|工程师|技术)$", "", skill_lower).strip()
    return skill_lower


def skill_match(s1: str, s2: str, threshold: float = 0.8) -> bool:
    """
    判断两个技能名称是否匹配（支持同义词和模糊匹配）。

    匹配规则：
        1. 先对两个名称分别进行标准化（normalize_skill）。
        2. 若标准化后完全相同，则返回 True。
        3. 否则计算标准化后的字符串相似度（SequenceMatcher 的 ratio），若大于等于阈值则返回 True。

    Args:
        s1 (str): 第一个技能名称。
        s2 (str): 第二个技能名称。
        threshold (float, optional): 相似度阈值，取值范围 [0,1]，默认 0.8。

    Returns:
        bool: 是否匹配。
    """
    norm1 = normalize_skill(s1)
    norm2 = normalize_skill(s2)

    if norm1 == norm2:
        return True

    ratio = SequenceMatcher(None, norm1, norm2).ratio()
    return ratio >= threshold